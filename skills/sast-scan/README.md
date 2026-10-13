# `sast-scan` Skill

Static application security testing with semgrep — injection, authz,
crypto-misuse, and taint-flow defects found in source before they ship.

- **Focus:** security
- **Category:** security
- **Source:** inline (self-contained body in the CR)
- **Attach to roles:** Code Reviewer, Coder, Architect
- **Permissions (least-privilege):** `fs:read`, `exec:semgrep`
- **Toolchains:** `semgrep@1`

## Install

```sh
kubectl apply -f skills/sast-scan/skill.yaml
```

> Requires the `semgrep` long-tail toolchain in the target namespace:
> `kubectl apply -k toolchains/ -n <team-namespace>`

## Wire it

Grant to every agent under a role (default) or to a single agent:

```yaml
# Role.spec.defaultSkills[] — granted to all agents of the role
defaultSkills:
  - name: sast-scan

# Agent.spec.skillRefs[] — granted to one agent (overrides role defaults)
skillRefs:
  - name: sast-scan
```
