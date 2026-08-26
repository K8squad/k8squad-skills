# `container-build` Skill

docker / buildkit build, run, inspect — reproduce build failures locally.

- **Focus:** dev+debug
- **Category:** dev-debug
- **Source:** inline (self-contained body in the CR)
- **Attach to roles:** DevOps, Coder
- **Permissions (least-privilege):** `exec:docker`, `net:egress:registry`
- **Toolchains:** `docker-cli@27`
- **Sidecars:** `dockerd`

## Install

```sh
kubectl apply -f skills/container-build/skill.yaml
```

## Wire it

Grant to every agent under a role (default) or to a single agent:

```yaml
# Role.spec.defaultSkills[] — granted to all agents of the role
defaultSkills:
  - name: container-build

# Agent.spec.skillRefs[] — granted to one agent (overrides role defaults)
skillRefs:
  - name: container-build
```
