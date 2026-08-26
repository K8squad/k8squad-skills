# `dynatrace` Skill

Dynatrace control-plane (dtctl) for observability.

- **Focus:** debug
- **Category:** default
- **Source:** git — `github.com/K8squad/k8squad-skills` path `skills/dynatrace`, pinned to a commit SHA
- **Attach to roles:** Observability
- **Permissions (least-privilege):** `observability:read`, `telemetry:query`
- **MCP tools:** `dynatrace-mcp`
- **Toolchains:** `dtctl@1.0`

## Install

```sh
kubectl apply -f skills/dynatrace/skill.yaml
```

## Wire it

Grant to every agent under a role (default) or to a single agent:

```yaml
# Role.spec.defaultSkills[] — granted to all agents of the role
defaultSkills:
  - name: dynatrace

# Agent.spec.skillRefs[] — granted to one agent (overrides role defaults)
skillRefs:
  - name: dynatrace
```

> **Note:** git-sourced. The `ref` must be pinned to an immutable **commit SHA**
> (never a floating branch, arch §5.3.6). The value shipped here is a placeholder —
> pin it to a merged commit of this repo before production use.
