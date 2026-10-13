#!/usr/bin/env python3
"""Skill security scanner for community-submitted Skill CRs.

A Skill carries a prompt body plus tool/command/RBAC grants that a K8squad agent
will EXECUTE. A malicious skill is therefore a prompt-injection / RCE / data-exfil
vector. This scanner statically inspects skill manifests and their markdown bodies
and emits GitHub-Actions annotations, classifying findings as:

  HIGH   -> blocks the PR (must be removed or justified by a maintainer edit)
  MEDIUM -> requires human security sign-off ONCE per skill content revision,
            recorded persistently in .github/security/reviewed-skills.txt
            (fast path: a maintainer applies the `skill-security-reviewed` label).

It is deliberately STATIC: it parses YAML/markdown as data and NEVER executes any
skill payload, so it is safe to run against untrusted fork PRs on a GitHub-hosted
runner with a read-only token and no secrets.

## Persistent MEDIUM sign-off baseline (ISI-5790)

A MEDIUM finding (privileged sidecar, exec:docker, unpinned git ref, egress to a
new host) means "a human must look once". Historically the only record of that
sign-off was the per-PR `skill-security-reviewed` label — ephemeral, so already
reviewed skills (e.g. container-build, go-build-test) RE-TRIPPED the gate on
every unrelated PR and blocked all skill-authoring work.

`.github/security/reviewed-skills.txt` is a durable record of those sign-offs,
keyed by `<skill-dir> <content-hash>`. The content hash covers EVERY file under
`skills/<name>/`, so any edit to a reviewed skill changes its hash and the
sign-off is re-demanded. A MEDIUM finding whose owning skill is recorded in the
baseline at its CURRENT hash is treated as already-reviewed and does NOT count
toward the `medium` total the workflow blocks on. HIGH findings are NEVER
baselined — they always block. A NEW or CHANGED skill with a MEDIUM finding is
not in the baseline (hash miss) and still blocks until signed off.

Usage:
    skill_security_scan.py [ROOT]            # scan ROOT/skills (default: cwd)
    skill_security_scan.py --emit-baseline [ROOT]
                                             # print reviewed-skills.txt lines for
                                             # every skill currently carrying a
                                             # MEDIUM finding (records a sign-off)

Outputs:
  - GitHub annotations on stdout (::error / ::warning / ::notice)
  - a human summary to $GITHUB_STEP_SUMMARY (if set)
  - high=<n> / medium=<n> to $GITHUB_OUTPUT (if set); `medium` EXCLUDES findings
    acknowledged by the reviewed-skills baseline
  - findings.json next to this script's CWD when --json is given

Always exits 0 (report-only); the workflow decides pass/fail from the counts so
the MEDIUM sign-off can be honored. Pass --strict-exit for local use (exit 2 on
HIGH, 3 on un-baselined MEDIUM) — used by the self-test.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

import yaml

HIGH = "HIGH"
MEDIUM = "MEDIUM"


@dataclass
class Rule:
    id: str
    severity: str
    pattern: re.Pattern
    title: str
    message: str


def _rx(p: str) -> re.Pattern:
    return re.compile(p, re.IGNORECASE | re.MULTILINE)


# --- Text rules: applied to inline skill bodies and markdown body files. --------
# HIGH = unambiguous attack primitives. MEDIUM = suspicious, needs a human.
TEXT_RULES: list[Rule] = [
    # ---- HIGH: remote-code-execution primitives -------------------------------
    Rule("pipe-to-shell", HIGH,
         _rx(r"\b(?:curl|wget|fetch)\b[^\n|]*\|\s*(?:sudo\s+)?(?:ba|z|d|c)?sh\b"),
         "curl/wget piped to a shell",
         "Downloading and directly executing a remote script is a classic RCE / "
         "supply-chain vector."),
    Rule("base64-exec", HIGH,
         _rx(r"base64\b[^\n]*(?:--?d(?:ecode)?|-D)\b[^\n]*\|\s*(?:ba|z)?sh\b"
             r"|\|\s*base64\b[^\n]*(?:--?d|-D)\b[^\n]*\|\s*(?:ba)?sh\b"),
         "base64-decoded payload piped to a shell",
         "Obfuscated (base64) code decoded straight into a shell is a common way "
         "to hide a malicious payload."),
    Rule("reverse-shell", HIGH,
         _rx(r"/dev/tcp/|/dev/udp/|\bn(?:et)?c(?:at)?\s+[^\n]*\s-e\b"
             r"|\bbash\s+-i\b|mkfifo\b[\s\S]{0,80}?\bn(?:et)?c\b"
             r"|\bsocat\b[^\n]*exec"),
         "reverse shell",
         "Reverse-shell construct (/dev/tcp, nc -e, bash -i, socat exec) gives a "
         "remote attacker interactive control."),
    Rule("python-reverse-shell", HIGH,
         _rx(r"socket\.socket\([^\n]*\)[\s\S]{0,160}?(?:connect\(|/bin/sh|/bin/bash)"
             r"|pty\.spawn\("),
         "python reverse shell",
         "socket+subprocess/pty pattern is a scripted reverse shell."),
    # ---- HIGH: credential / secret exfiltration -------------------------------
    Rule("credential-file-access", HIGH,
         _rx(r"\.git-credentials\b|\bid_rsa\b|\bid_ed25519\b|/etc/shadow\b"
             r"|\.aws/credentials\b|\.ssh/id_|\.netrc\b|\.kube/config\b"
             r"|\.docker/config\.json\b"),
         "access to a credential/secret file",
         "Reading private keys, cloud creds, or the kubeconfig is a data-exfil "
         "red flag in a skill body."),
    Rule("env-exfiltration", HIGH,
         _rx(r"\b(?:printenv|env|set)\b[^\n]*\|\s*(?:curl|wget|nc|ncat)\b"
             r"|(?:curl|wget|nc)\b[^\n]*\$\{?[A-Za-z_]*(?:TOKEN|SECRET|KEY|PASSWORD|PASSWD)"
             r"|\$\{?(?:GITHUB_TOKEN|AWS_SECRET_ACCESS_KEY)\}?[^\n]*\|\s*(?:curl|wget|nc)\b"),
         "environment/secret exfiltration",
         "Piping the environment or a *_TOKEN/*_SECRET value to the network "
         "exfiltrates credentials."),
    # ---- HIGH: prompt-injection that overrides governance ---------------------
    Rule("prompt-injection-override", HIGH,
         _rx(r"ignore\s+(?:all\s+|any\s+)?(?:the\s+)?(?:previous|prior|above|earlier|preceding)\s+"
             r"(?:instructions?|prompts?|rules?|directions?)"
             r"|disregard\s+(?:the\s+|all\s+|any\s+)?(?:system|governance|safety|previous|above)"
             r"|override\s+(?:the\s+)?(?:system|governance|safety|guardrails?|instructions?)"
             r"|you\s+are\s+now\s+(?:an?\s+)?(?:unrestricted|jailbroken|root|admin|dan\b)"
             r"|\bnew\s+system\s+prompt\b|\bexfiltrat\w*"),
         "prompt-injection / governance override",
         "Phrasing that tries to override the agent's system/governance rules is a "
         "prompt-injection attack."),
    # ---- MEDIUM: suspicious, human should look --------------------------------
    Rule("stealth-instruction", MEDIUM,
         _rx(r"\bwithout\s+(?:asking|telling|informing|notifying)\s+(?:the\s+)?(?:user|human|operator|maintainer)"
             r"|\bsilently\b|\bdo\s+not\s+(?:tell|inform|log|report|mention)\b"
             r"|\b(?:hide|conceal)\s+(?:this|these|the|it|your)\b|\bbypass(?:ing)?\b"),
         "stealth / do-not-tell instruction",
         "Instructing the agent to act silently or hide activity from the operator "
         "warrants human review."),
    Rule("insecure-transport", MEDIUM,
         _rx(r"\bcurl\b[^\n]*\s(?:-k|--insecure)\b|\bchmod\s+0?777\b|\bsudo\b"),
         "insecure flag (curl -k / chmod 777 / sudo)",
         "Disabling TLS verification, world-writable perms, or sudo in a skill body "
         "is worth a second look."),
]

# Permission tokens that grant an over-broad envelope. HIGH — an agent should
# never be handed a wildcard or admin-equivalent capability by a community skill.
BROAD_PERMISSION = _rx(r"^\*$|^\*:|:\*$|\ball\b|\*\*"
                       r"|\b(?:admin|cluster-admin|clusteradmin|root|superuser|privileged|god)\b")

# Sidecars / permissions that grant container-escape surface. MEDIUM — legitimate
# (e.g. the container-build skill) but must be signed off by a human.
PRIVILEGED_SIDECAR = _rx(r"^(?:dockerd|docker|containerd|podman|dind)$")
PRIVILEGED_PERMISSION = _rx(r"^exec:(?:docker|containerd|podman|dind)$|:privileged$")

SHA40 = re.compile(r"^[0-9a-f]{40}$")


@dataclass
class Finding:
    file: str
    line: int
    severity: str
    rule: str
    title: str
    message: str
    # Set True when this MEDIUM finding's owning skill is recorded in the
    # reviewed-skills baseline at its current content hash (human already signed
    # off; does not count toward the blocking `medium` total). HIGH is never
    # baselined.
    baselined: bool = False


@dataclass
class Report:
    findings: list[Finding] = field(default_factory=list)

    def add(self, *a, **k) -> None:
        self.findings.append(Finding(*a, **k))

    @property
    def high(self) -> int:
        return sum(1 for f in self.findings if f.severity == HIGH)

    @property
    def medium(self) -> int:
        """Un-baselined MEDIUM findings — the count the PR gate blocks on."""
        return sum(1 for f in self.findings
                   if f.severity == MEDIUM and not f.baselined)

    @property
    def medium_reviewed(self) -> int:
        """MEDIUM findings acknowledged by the reviewed-skills baseline."""
        return sum(1 for f in self.findings
                   if f.severity == MEDIUM and f.baselined)


def _line_of(text: str, idx: int) -> int:
    return text.count("\n", 0, idx) + 1


def load_allowlist(root: Path) -> list[str]:
    f = root / ".github" / "security" / "egress-allowlist.txt"
    hosts: list[str] = []
    if f.exists():
        for raw in f.read_text().splitlines():
            line = raw.split("#", 1)[0].strip()
            if line:
                hosts.append(line.lower())
    return hosts


def host_allowed(host: str, allow: list[str]) -> bool:
    host = host.lower().rstrip(".")
    return any(host == a or host.endswith("." + a) for a in allow)


# --- Reviewed-skills baseline (persistent MEDIUM sign-off, ISI-5790) -----------
REVIEWED_BASELINE = PurePosixPath(".github/security/reviewed-skills.txt")


def skill_dir_of(file_rel: str) -> str | None:
    """Return the owning `skills/<name>` dir for a finding's repo-relative file.

    All scanned content lives under skills/<name>/; a finding on
    skills/foo/bar.md or skills/foo/skill.yaml both belong to skill `skills/foo`.
    """
    parts = PurePosixPath(file_rel).parts
    if len(parts) >= 2 and parts[0] == "skills":
        return str(PurePosixPath(parts[0], parts[1]))
    return None


def skill_content_hash(root: Path, skill_dir_rel: str) -> str:
    """SHA-256 over EVERY regular file under skills/<name>/ (path + bytes).

    Hashing the whole directory — not just skill.yaml — means adding or editing
    any aux file (README, *.sh, *.py dropped beside the manifest) changes the
    hash and re-demands sign-off, closing the F4 aux-file coverage gap for the
    baseline. Deterministic: entries sorted by POSIX relpath.
    """
    base = root / skill_dir_rel
    h = hashlib.sha256()
    if not base.is_dir():
        return h.hexdigest()
    files = sorted((p for p in base.rglob("*") if p.is_file()),
                   key=lambda p: p.relative_to(base).as_posix())
    for p in files:
        rel = p.relative_to(base).as_posix()
        h.update(rel.encode("utf-8"))
        h.update(b"\0")
        h.update(p.read_bytes())
        h.update(b"\0")
    return h.hexdigest()


def load_reviewed(root: Path) -> set[tuple[str, str]]:
    """Parse reviewed-skills.txt into a set of (skill-dir, content-hash) pairs.

    Line format: `<skill-dir> <sha256-hex>   # optional note`. Blank lines and
    `#` comments are ignored. A sign-off matches only when BOTH the skill dir
    and its current content hash are present — an edited skill (new hash) is not
    matched, so its MEDIUM finding re-blocks until re-reviewed.
    """
    f = root / ".github" / "security" / "reviewed-skills.txt"
    out: set[tuple[str, str]] = set()
    if not f.exists():
        return out
    for raw in f.read_text().splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        cols = line.split()
        if len(cols) >= 2:
            out.add((cols[0].rstrip("/"), cols[1].lower()))
    return out


def apply_baseline(root: Path, rep: Report) -> None:
    """Mark MEDIUM findings whose owning skill is recorded at its current hash."""
    reviewed = load_reviewed(root)
    if not reviewed:
        return
    hashes: dict[str, str] = {}
    for f in rep.findings:
        if f.severity != MEDIUM:
            continue
        sd = skill_dir_of(f.file)
        if sd is None:
            continue
        if sd not in hashes:
            hashes[sd] = skill_content_hash(root, sd)
        if (sd, hashes[sd]) in reviewed:
            f.baselined = True


def baseline_lines(root: Path, rep: Report) -> list[str]:
    """`<skill-dir> <hash>` lines for every skill carrying a MEDIUM finding.

    Used by --emit-baseline so a maintainer can record a sign-off after review.
    """
    dirs: dict[str, None] = {}
    for f in rep.findings:
        if f.severity != MEDIUM:
            continue
        sd = skill_dir_of(f.file)
        if sd is not None:
            dirs[sd] = None
    return [f"{sd} {skill_content_hash(root, sd)}" for sd in sorted(dirs)]


# Capture the REAL host: skip any `userinfo@` authority prefix so
# `https://raw.githubusercontent.com@evil.example/x` is scanned as evil.example,
# not the allowlisted-looking userinfo. (ISI-3276 F1: userinfo egress bypass.)
URL_RX = re.compile(r"https?://(?:[^/@\s]*@)?([A-Za-z0-9._-]+)", re.IGNORECASE)


def scan_text(rep: Report, path: str, text: str, allow: list[str]) -> None:
    """Apply text rules + egress-allowlist to a body string."""
    for rule in TEXT_RULES:
        for m in rule.pattern.finditer(text):
            rep.add(path, _line_of(text, m.start()), rule.severity,
                    rule.id, rule.title, rule.message)
    # Network egress to non-allowlisted hosts (skip common docs hosts already in
    # the allowlist file). Localhost/example are ignored.
    for m in URL_RX.finditer(text):
        host = m.group(1)
        if host.lower() in ("localhost", "127.0.0.1", "example.com", "example.org"):
            continue
        if not host_allowed(host, allow):
            rep.add(path, _line_of(text, m.start()), MEDIUM, "egress-non-allowlisted",
                    "network egress to non-allowlisted host",
                    f"Skill body references '{host}', which is not in "
                    ".github/security/egress-allowlist.txt.")


def scan_manifest(rep: Report, abspath: Path, path: str, allow: list[str]) -> None:
    """Parse a skill.yaml and scan its body + structured grants.

    abspath is read from disk; path is the repo-relative name used in findings.
    """
    raw = abspath.read_text()
    try:
        doc = yaml.safe_load(raw)
    except yaml.YAMLError as e:
        rep.add(path, 1, HIGH, "unparseable-yaml", "manifest is not valid YAML",
                f"Could not parse the Skill manifest: {e}")
        return
    if not isinstance(doc, dict):
        return
    spec = doc.get("spec") or {}
    source = spec.get("source") or {}

    inline = source.get("inline")
    if isinstance(inline, str) and inline.strip():
        scan_text(rep, path, inline, allow)

    # git source: enforce SHA-pinned ref (CRD §5.3.6 — a moving branch/tag lets a
    # force-push silently swap the executed body). Unpinned = MEDIUM supply-chain.
    git = source.get("git") or {}
    ref = git.get("ref")
    if isinstance(ref, str) and ref and not SHA40.match(ref.strip()):
        rep.add(path, 1, MEDIUM, "unpinned-git-ref",
                "git-sourced skill is not pinned to a commit SHA",
                f"source.git.ref='{ref}' is a moving reference; pin to a 40-char "
                "commit SHA so a force-push cannot swap the executed body.")

    for perm in spec.get("permissions") or []:
        p = str(perm).strip()
        if BROAD_PERMISSION.search(p):
            rep.add(path, 1, HIGH, "over-broad-permission",
                    "over-broad permission grant",
                    f"permission '{p}' grants a wildcard/admin-equivalent envelope; "
                    "skills must request the narrowest capability they need.")
        elif PRIVILEGED_PERMISSION.search(p):
            rep.add(path, 1, MEDIUM, "privileged-permission",
                    "privileged (container-escape) permission",
                    f"permission '{p}' grants container-runtime access; requires "
                    "human security sign-off.")

    requires = spec.get("requires") or {}
    for sc in requires.get("sidecars") or []:
        if PRIVILEGED_SIDECAR.match(str(sc).strip()):
            rep.add(path, 1, MEDIUM, "privileged-sidecar",
                    "privileged sidecar (container-in-container)",
                    f"sidecar '{sc}' runs a container runtime (escape surface); "
                    "requires human security sign-off.")


def discover(root: Path) -> tuple[list[Path], list[Path]]:
    # Only skill content is the attack surface. Scope strictly to skills/ so the
    # repo's own docs (CONTRIBUTING.md etc., which quote attack signatures as
    # examples) are never scanned. No skills/ dir → nothing to scan.
    #
    # ponytail: KNOWN COVERAGE CEILING (ISI-3276 F2/F3/F4). This static scan sees
    # ONLY the in-repo text: `source.inline` bodies + `skills/**/*.md`. It does
    # NOT (a) fetch and scan a `source.git` remote body — a git-sourced skill's
    # executed payload lives in another repo and is invisible here (F2); (b) catch
    # two-step download-then-exec that fetches from an allowlisted user-content
    # host like raw.githubusercontent.com (F3); (c) scan aux files (*.sh/*.py/…)
    # dropped alongside skill.yaml (F4). These are covered by the human sign-off
    # gate, NOT the scanner: git-sourced and privileged skills must get a
    # maintainer's `skill-security-reviewed` label (see CONTRIBUTING.md).
    base = root / "skills"
    if not base.is_dir():
        return [], []
    manifests = sorted(base.rglob("skill.yaml"))
    bodies = sorted(base.rglob("*.md"))
    return manifests, bodies


def run(root: Path) -> Report:
    rep = Report()
    allow = load_allowlist(root)
    manifests, bodies = discover(root)
    for m in manifests:
        scan_manifest(rep, m, str(m.relative_to(root)), allow)
    for b in bodies:
        # markdown under skills/ is a git-source body the agent reads → scan it
        scan_text(rep, str(b.relative_to(root)), b.read_text(errors="replace"), allow)
    apply_baseline(root, rep)
    return rep


def emit_annotations(rep: Report) -> None:
    for f in rep.findings:
        if f.severity == HIGH:
            level = "error"
        elif f.baselined:
            # Already signed off in the reviewed-skills baseline → informational.
            level = "notice"
        else:
            level = "warning"
        suffix = " [reviewed: acknowledged by reviewed-skills.txt]" if f.baselined else ""
        title = f"[{f.severity}] {f.title}{suffix}"
        # newlines in annotation messages must be escaped for the workflow command
        msg = f.message.replace("\n", " ") + suffix
        print(f"::{level} file={f.file},line={f.line},title={title}::{msg}")


def write_summary(rep: Report) -> None:
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    lines = ["## Skill security scan", ""]
    if not rep.findings:
        lines.append("✅ No security findings.")
    else:
        hdr = f"**{rep.high} HIGH** · **{rep.medium} MEDIUM**"
        if rep.medium_reviewed:
            hdr += f" · _{rep.medium_reviewed} MEDIUM already reviewed (baseline)_"
        lines.append(hdr)
        lines += ["", "| Severity | Rule | File:Line | Finding | Status |",
                  "|---|---|---|---|---|"]
        for f in sorted(rep.findings,
                        key=lambda x: (x.severity != HIGH, x.baselined, x.file)):
            status = "✅ reviewed (baseline)" if f.baselined else "needs action"
            lines.append(
                f"| {f.severity} | `{f.rule}` | `{f.file}:{f.line}` | {f.title} | {status} |")
        if rep.high:
            lines += ["", "❌ HIGH findings block this PR. Remove the offending "
                      "content or a maintainer must edit the submission."]
        if rep.medium:
            lines += ["", "⚠️ Un-baselined MEDIUM findings require human security "
                      "sign-off before merge: a maintainer either applies the "
                      "`skill-security-reviewed` label (fast path) or records the "
                      "sign-off persistently by adding the skill to "
                      "`.github/security/reviewed-skills.txt` "
                      "(`skill_security_scan.py --emit-baseline .`)."]
        if rep.medium_reviewed and not rep.medium:
            lines += ["", "ℹ️ All MEDIUM findings are on skills already signed off "
                      "in `.github/security/reviewed-skills.txt` at their current "
                      "content — no per-PR action needed."]
    body = "\n".join(lines) + "\n"
    if path:
        with open(path, "a") as fh:
            fh.write(body)
    else:
        print(body, file=sys.stderr)


def write_outputs(rep: Report) -> None:
    path = os.environ.get("GITHUB_OUTPUT")
    if path:
        with open(path, "a") as fh:
            fh.write(f"high={rep.high}\nmedium={rep.medium}\n")


def main(argv: list[str]) -> int:
    strict = "--strict-exit" in argv
    emit = "--emit-baseline" in argv
    args = [a for a in argv[1:] if not a.startswith("-")]
    root = Path(args[0]).resolve() if args else Path.cwd()
    rep = run(root)
    if emit:
        # Print reviewed-skills.txt lines for every skill currently carrying a
        # MEDIUM finding. A maintainer reviews the skill(s), then commits these
        # lines to .github/security/reviewed-skills.txt to record the sign-off.
        lines = baseline_lines(root, rep)
        if not lines:
            print("# No skills currently carry a MEDIUM finding — nothing to baseline.")
        else:
            print("# Generated by skill_security_scan.py --emit-baseline")
            print("# Review each skill before committing; a line records a human sign-off.")
            for ln in lines:
                print(ln)
        return 0
    emit_annotations(rep)
    write_summary(rep)
    write_outputs(rep)
    if strict:
        if rep.high:
            return 2
        if rep.medium:
            return 3
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
