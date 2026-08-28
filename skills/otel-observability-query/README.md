# `otel-observability-query` Skill

Read-only trace/log/span query via MCP (Dynatrace DQL).

- **Focus:** debug
- **Category:** dev-debug
- **Source:** git — `github.com/K8squad/k8squad-skills` path `skills/otel-observability-query`, pinned to commit `bf3bc86`
- **Attach to roles:** Observability, Coder, Test Architect, DevOps
- **Permissions (least-privilege):** `dt:query:logs`, `dt:query:spans`, `dt:query:metrics`
- **MCP tools:** `dynatrace-mcp` (stdio sidecar; read-only `query_*`/`list_*`/`get_*` envelope)

## Prerequisites (fail-closed)

1. **An `MCPServer` named `dynatrace-mcp`** in the skill's namespace — the
   same server the [`dynatrace`](../dynatrace) skill uses (template in
   [`examples/bmad-team/02b-mcpservers.yaml`](https://github.com/K8squad/K8squad/tree/main/examples/bmad-team)).
   A dangling `mcpToolRefs` entry rejects the Skill at admission.
2. **Discovery succeeded** — `status.observedTools` non-empty and
   `ToolsDiscovered=True` (control-plane `initialize` → `tools/list` probe).
   Until then, Runs referencing this skill stay Pending (ADR-042 staleness).
3. **The API token Secret** behind `MCPServer.spec.credentialSecretRef` —
   projected per-Run as an env var only (ADR-045 D5).

The server's `toolFilter` (`query_*`, `list_*`, `get_*`) is the ceiling:
this skill's queries can only run tools inside that envelope (D8 — skills
narrow, never widen).

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

> **Note:** git-sourced. The `ref` is pinned to an immutable **commit SHA**
> (never a floating branch, arch §5.3.6) — a force-push to this repo cannot
> alter the behavior of an in-flight Run. Each catalog release re-pins the
> self-referential `ref` fields to the release merge commit.

## Usage instrumentation (free)

Skill/tool usage is reported automatically — nothing to opt into:

- OTel spans: `skill.load` and `gen_ai.tool.call` (GenAI semconv:
  `gen_ai.tool.name`, `gen_ai.tool.call.arguments` = hex sha256 of the args),
  carrying `ksquad.run.id`, `ksquad.agent.name`, `ksquad.skill.name`,
  `ksquad.skill.source.sha`, `ksquad.mcp.server`.
- Prometheus metrics on the operator: `ksquad_skill_loads_total`,
  `ksquad_tool_calls_total`, `ksquad_mcp_call_duration_seconds`,
  `ksquad_tool_usage_pipeline_up`.
