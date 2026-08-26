# `golangci-lint` Skill

Run the repo's static-analysis / lint gate locally.

- **Focus:** dev
- **Category:** dev-debug
- **Source:** inline (self-contained body in the CR)
- **Attach to roles:** Code Reviewer, Coder
- **Permissions (least-privilege):** `fs:read`, `exec:golangci-lint`
- **Toolchains:** `go@1.25`, `golangci-lint@2.1`

## Install

```sh
kubectl apply -f skills/golangci-lint/skill.yaml
```

## Wire it

Grant to every agent under a role (default) or to a single agent:

```yaml
# Role.spec.defaultSkills[] — granted to all agents of the role
defaultSkills:
  - name: golangci-lint

# Agent.spec.skillRefs[] — granted to one agent (overrides role defaults)
skillRefs:
  - name: golangci-lint
```
