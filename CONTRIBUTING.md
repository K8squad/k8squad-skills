# Contributing a Skill

Thank you for contributing to the K8squad Skill catalog. A `Skill` is a granted
capability that a K8squad agent will **read as a prompt and execute against real
infrastructure**. That makes every submission a potential prompt-injection, RCE,
or data-exfiltration vector, so community PRs are held to a security review bar.

Please read this before opening a PR.

> Adding a **toolchain** (the versioned CLI packs a skill's
> `requires.toolchains` resolves against) rather than a skill? See
> [Adding a toolchain](docs/adding-a-toolchain.md).

## What a Skill is

Each skill lives in `skills/<name>/`:

```
skills/<name>/
  skill.yaml   # the Skill custom resource (ksquad.io/v1alpha1)
  README.md    # human-facing description of what the skill does
```

`skill.yaml` must be a valid `Skill` per the `ksquad.io/v1alpha1` CRD
([schema in the main repo](https://github.com/K8squad/K8squad/blob/main/config/crd/bases/ksquad.io_skills.yaml)).
Minimal shape:

```yaml
apiVersion: ksquad.io/v1alpha1
kind: Skill
metadata:
  name: <name>
  namespace: bmad-squad
spec:
  source:
    type: inline          # or: git
    inline: |             # required when type=inline
      # <name>
      <the skill body the agent reads>
  mcpToolRefs:            # optional: MCP servers this skill is granted
    - name: <mcpserver>   # must exist in the namespace at admission
  permissions:            # the narrowest capability envelope the skill needs
    - <capability>
  requires:               # optional toolchains / sidecars
    toolchains: [<pack@version>]
```

New skills must also be listed in the root `kustomization.yaml`.

### Capability-plane requirements (fail-closed)

Your skill resolves against live cluster objects — keep these true or Runs
will be rejected at admission:

- **`mcpToolRefs[].name` must resolve to an existing `MCPServer`** in the
  skill's namespace (or the ref's explicit `namespace`). A dangling ref
  rejects the Skill itself at admission. The skill can only *narrow* the
  server's envelope — `mcpToolRefs` carries no filter fields, so it can
  never widen `MCPServer.spec.toolFilter` (trust boundary D8). Document the
  expected server name/shape in your README (see
  `examples/bmad-team/02b-mcpservers.yaml` in the main repo for templates).
- **`requires.toolchains` entries resolve as `name@version`** against the
  cluster Toolchain catalog. Prefer the curated set shipped by
  `tools.defaultCatalog.enabled=true` (`kubectl@1.36`, `git@2.45`, `gh@2.98`,
  `go@1.26`, `node@22`, `dtctl@1.0`, `helm@3.21`); anything else is BYO and
  your README must say which `Toolchain` objects the operator must define.
  An unknown `name@version`, or two versions of one toolchain across a Run's
  skills, rejects the Run with an actionable message.
- **`source.git.ref` must be a 40-character commit SHA** (also a MEDIUM
  security-review trigger below) — Runs resolve skills to immutable
  revisions; a force-push cannot alter an in-flight Run.
- **Credentials never appear in the skill** — servers reference Secrets via
  `credentialSecretRef`; the platform projects them per-Run as env vars
  (`KSQUAD_MCP_<NAME>_TOKEN`), never as files (ADR-045 D5).
- **You instrument nothing.** Skill loads, tool calls, and MCP call
  durations are reported automatically as GenAI-semconv OTel spans
  (`skill.load`, `gen_ai.tool.call`) and `ksquad_*` Prometheus metrics —
  see the root README for the full list.

## Automated checks (run on every PR)

Two required checks run on GitHub-hosted runners with a **read-only token and no
secrets** — they never execute your skill body.

1. **CRD schema validation** — every `skill.yaml` is applied to a real
   kube-apiserver with `kubectl apply --dry-run=server`. This rejects unknown or
   misspelled fields *and* enforces the CRD's CEL rules (e.g. `type: inline` must
   carry `source.inline` and must not set `source.git`, and vice-versa).

2. **Skill security scan** (`.github/scripts/skill_security_scan.py`) — statically
   inspects your skill body and grants and classifies findings:

   | Severity | Effect |
   |----------|--------|
   | **HIGH** | **Blocks the PR.** Must be removed. |
   | **MEDIUM** | Requires a maintainer to review and apply the `skill-security-reviewed` label before merge. |

## The review bar

Your skill will be **rejected (HIGH)** if its body or grants contain:

- **Remote code execution** — `curl`/`wget` piped to a shell, base64-decoded
  payloads piped to a shell, reverse shells (`/dev/tcp`, `nc -e`, `bash -i`,
  `socat exec`, socket+`pty.spawn`).
- **Credential / secret exfiltration** — reading `~/.git-credentials`, SSH private
  keys, `/etc/shadow`, cloud creds, or the kubeconfig; piping `env`/`printenv` or
  any `*_TOKEN` / `*_SECRET` value to the network.
- **Prompt injection** — phrasing that tries to override the agent's system or
  governance rules ("ignore previous instructions", "disregard governance",
  "you are now unrestricted", "exfiltrate…").
- **Over-broad grants** — wildcard or admin-equivalent `permissions` (`*`, `k8s:*`,
  `cluster-admin`, `admin`, `root`). Request the narrowest capability you need.

Your skill will require **human sign-off (MEDIUM)** if it:

- Grants **container-escape surface** — a `dockerd`/`containerd`/`podman` sidecar
  or an `exec:docker`-class permission.
- Uses a **git source that is not pinned to a commit SHA** — `source.git.ref` must
  be a 40-character commit SHA, never a moving branch or tag, so a force-push
  cannot silently swap the executed body.
- Reaches a **network host not in** `.github/security/egress-allowlist.txt`. If
  your skill legitimately needs a new host, add it to that file in the same PR
  with a justification, and a maintainer will confirm it.
- Contains **stealth instructions** — telling the agent to act "silently", hide
  activity, or proceed "without telling the user".

## Before you open a PR

- Run the checks locally:

  ```bash
  pip install pyyaml
  python3 .github/scripts/skill_security_scan.py .      # security scan
  python3 .github/scripts/test_skill_security_scan.py   # scanner self-test
  ```

- Keep the `permissions` list minimal.
- Explain in the PR description **why** each permission and any privileged sidecar
  is necessary.

Maintainers may edit or reject any submission. When in doubt, open an issue first.
