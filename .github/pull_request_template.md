<!--
Thanks for contributing a Skill! Please read CONTRIBUTING.md first.
A Skill is executed by a K8squad agent against real infrastructure, so PRs go
through automated schema validation + a security scan and a maintainer review.
-->

## What does this skill do?

<!-- One or two sentences: what capability does it grant and when is it used? -->

## Skill checklist

- [ ] `skills/<name>/skill.yaml` is a valid `ksquad.io/v1alpha1` Skill.
- [ ] The new skill is listed in the root `kustomization.yaml`.
- [ ] A `skills/<name>/README.md` describes the skill for humans.
- [ ] The `permissions` list is the **narrowest** envelope the skill needs.
- [ ] If `source.type: git`, `source.git.ref` is pinned to a **40-char commit SHA**
      (not a branch or tag).
- [ ] I ran the checks locally and they pass:
      `python3 .github/scripts/skill_security_scan.py .` and
      `python3 .github/scripts/test_skill_security_scan.py`.

## Security justification

<!-- Required. Justify anything a reviewer should scrutinize. -->

- **Permissions requested and why:**
- **Privileged sidecars (dockerd/containerd/podman), if any, and why:**
- **Network hosts the skill reaches (must be in `.github/security/egress-allowlist.txt`):**

<!--
Reviewer note: HIGH security findings block this PR. MEDIUM findings require a
maintainer to review the flagged skill and apply the `skill-security-reviewed`
label before merge.
-->
