# `kubectl-debug` Skill

Read-only cluster introspection + ephemeral debug containers.

- **Focus:** debug
- **Category:** dev-debug
- **Source:** inline (self-contained body in the CR)
- **Attach to roles:** DevOps, Observability, Coder, Test Architect
- **Permissions (least-privilege):** `k8s:get`, `k8s:list`, `k8s:watch`, `k8s:logs`, `k8s:debug:ephemeral`
- **Toolchains:** `kubectl@1.36`

## Install

```sh
kubectl apply -f skills/kubectl-debug/skill.yaml
```

## Wire it

Grant to every agent under a role (default) or to a single agent:

```yaml
# Role.spec.defaultSkills[] — granted to all agents of the role
defaultSkills:
  - name: kubectl-debug

# Agent.spec.skillRefs[] — granted to one agent (overrides role defaults)
skillRefs:
  - name: kubectl-debug
```
