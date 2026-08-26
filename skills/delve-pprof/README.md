# `delve-pprof` Skill

Live-process debug (dlv) + profiling (pprof) against a pod via port-forward.

- **Focus:** debug
- **Category:** dev-debug
- **Source:** inline (self-contained body in the CR)
- **Attach to roles:** Coder, Observability
- **Permissions (least-privilege):** `fs:read`, `exec:dlv`, `exec:go-tool-pprof`, `k8s:port-forward`
- **Toolchains:** `go@1.25`, `delve@1.24`

## Install

```sh
kubectl apply -f skills/delve-pprof/skill.yaml
```

## Wire it

Grant to every agent under a role (default) or to a single agent:

```yaml
# Role.spec.defaultSkills[] — granted to all agents of the role
defaultSkills:
  - name: delve-pprof

# Agent.spec.skillRefs[] — granted to one agent (overrides role defaults)
skillRefs:
  - name: delve-pprof
```
