# `psql-inspect` Skill

Read-only psql into the coordination / run-source Postgres.

- **Focus:** debug
- **Category:** dev-debug
- **Source:** inline (self-contained body in the CR)
- **Attach to roles:** Coder, DevOps, Test Architect
- **Permissions (least-privilege):** `db:read`, `net:egress:postgres`
- **Toolchains:** `postgres-client@16`

## Install

```sh
kubectl apply -f skills/psql-inspect/skill.yaml
```

## Wire it

Grant to every agent under a role (default) or to a single agent:

```yaml
# Role.spec.defaultSkills[] — granted to all agents of the role
defaultSkills:
  - name: psql-inspect

# Agent.spec.skillRefs[] — granted to one agent (overrides role defaults)
skillRefs:
  - name: psql-inspect
```
