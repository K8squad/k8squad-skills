# `otel-observability-query` Skill

Read-only trace/log/span query via MCP (Dynatrace DQL).

- **Focus:** debug
- **Category:** dev-debug
- **Source:** git — `github.com/K8squad/k8squad-skills` path `skills/otel-query`, pinned to a commit SHA
- **Attach to roles:** Observability, Coder, Test Architect, DevOps
- **Permissions (least-privilege):** `dt:query:logs`, `dt:query:spans`, `dt:query:metrics`
- **MCP tools:** `dynatrace-dql`

## Install

```sh
kubectl apply -f skills/otel-observability-query/skill.yaml
```

## Wire it

Grant to every agent under a role (default) or to a single agent:

```yaml
# Role.spec.defaultSkills[] — granted to all agents of the role
defaultSkills:
  - name: otel-observability-query

# Agent.spec.skillRefs[] — granted to one agent (overrides role defaults)
skillRefs:
  - name: otel-observability-query
```

> **Note:** git-sourced. The `ref` must be pinned to an immutable **commit SHA**
> (never a floating branch, arch §5.3.6). The value shipped here is a placeholder —
> pin it to a merged commit of this repo before production use.
