# `http-grpc-probe` Skill

curl / grpcurl probing of live service endpoints (optional).

- **Focus:** debug
- **Category:** dev-debug (optional)
- **Source:** inline (self-contained body in the CR)
- **Attach to roles:** Coder, Test Architect, DevOps
- **Permissions (least-privilege):** `exec:curl`, `exec:grpcurl`, `net:egress:cluster`
- **Toolchains:** `curl@8`, `grpcurl@1.9`

## Install

```sh
kubectl apply -f skills/http-grpc-probe/skill.yaml
```

## Wire it

Grant to every agent under a role (default) or to a single agent:

```yaml
# Role.spec.defaultSkills[] — granted to all agents of the role
defaultSkills:
  - name: http-grpc-probe

# Agent.spec.skillRefs[] — granted to one agent (overrides role defaults)
skillRefs:
  - name: http-grpc-probe
```
