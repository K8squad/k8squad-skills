# `bmad` Skill

The BMAD method — phased squad workflow with explicit handoffs.

- **Focus:** method
- **Category:** default
- **Source:** inline (self-contained body in the CR)
- **Attach to roles:** all roles
- **Permissions (least-privilege):** `workflow:bmad`

## Install

```sh
kubectl apply -f skills/bmad/skill.yaml
```

## Wire it

Grant to every agent under a role (default) or to a single agent:

```yaml
# Role.spec.defaultSkills[] — granted to all agents of the role
defaultSkills:
  - name: bmad

# Agent.spec.skillRefs[] — granted to one agent (overrides role defaults)
skillRefs:
  - name: bmad
```
