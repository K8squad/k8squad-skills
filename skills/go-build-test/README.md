# `go-build-test` Skill

Go build / vet / test (-run, -race) with a dockerd sidecar for integration suites.

- **Focus:** dev+debug
- **Category:** dev-debug
- **Source:** inline (self-contained body in the CR)
- **Attach to roles:** Coder, Test Architect, Code Reviewer
- **Permissions (least-privilege):** `fs:read`, `fs:write:workspace`, `exec:go`
- **Toolchains:** `go@1.25`
- **Sidecars:** `dockerd`

## Install

```sh
kubectl apply -f skills/go-build-test/skill.yaml
```

## Wire it

Grant to every agent under a role (default) or to a single agent:

```yaml
# Role.spec.defaultSkills[] — granted to all agents of the role
defaultSkills:
  - name: go-build-test

# Agent.spec.skillRefs[] — granted to one agent (overrides role defaults)
skillRefs:
  - name: go-build-test
```
