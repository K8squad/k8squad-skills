# `secret-scan` Skill

Detect committed credentials with gitleaks — keys, tokens, private keys,
and high-entropy strings in the working tree and git history.

- **Focus:** security
- **Category:** security
- **Source:** inline (self-contained body in the CR)
- **Attach to roles:** Code Reviewer, Coder, DevOps, Architect
- **Permissions (least-privilege):** `fs:read`, `exec:gitleaks`
- **Toolchains:** `gitleaks@8`

## Install

```sh
kubectl apply -f skills/secret-scan/skill.yaml
```

> Requires the `gitleaks` long-tail toolchain in the target namespace:
> `kubectl apply -k toolchains/ -n <team-namespace>`

## Wire it

Grant to every agent under a role (default) or to a single agent:

```yaml
# Role.spec.defaultSkills[] — granted to all agents of the role
defaultSkills:
  - name: secret-scan

# Agent.spec.skillRefs[] — granted to one agent (overrides role defaults)
skillRefs:
  - name: secret-scan
```

> **Note:** gitleaks already runs as a required CI gate in the main repos;
> this skill lets agents reproduce that gate locally during review.
