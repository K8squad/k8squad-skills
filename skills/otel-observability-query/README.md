# `otel-observability-query` Skill

Read-only trace/log/span query via the `dtctl` CLI (Dynatrace DQL).

- **Focus:** debug
- **Category:** dev-debug
- **Source:** git — `github.com/K8squad/k8squad-skills` path `skills/otel-observability-query`, pinned to commit `bf3bc86`
- **Attach to roles:** Observability, Coder, Test Architect, DevOps
- **Permissions (least-privilege):** `dt:query:logs`, `dt:query:spans`, `dt:query:metrics`
- **Toolchains:** `dtctl@1.0` (ships in the cluster default catalog)

Read-only DQL querying through the `dtctl` CLI toolchain — no `MCPServer`
required. The narrow `dt:query:*` permission envelope keeps this skill to
read paths (logs/spans/metrics); it shares the same `dtctl` access path as the
[`dynatrace`](../dynatrace) skill but without any write/control verbs.

## Prerequisites (fail-closed)

1. **The toolchain catalog** is enabled at install time
   (`--set tools.defaultCatalog.enabled=true`) so `dtctl@1.0` resolves; an
   unknown `name@version` rejects the Run at admission.
2. **A Dynatrace API token** for `dtctl` — a BYO read-only scoped token Secret
   projected per-Run as an env var only (e.g. `DT_API_TOKEN`), never into any
   file the runtime reads (ADR-045 D5).

The CRD-authorized `permissions` envelope (`dt:query:logs`, `dt:query:spans`,
`dt:query:metrics`) is the read-only ceiling — set by the operator/admin and
never widened by the fetched skill body (trust boundary D8).

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
  `ksquad.skill.source.sha`.
- Prometheus metrics on the operator: `ksquad_skill_loads_total`,
  `ksquad_tool_calls_total`, `ksquad_tool_usage_pipeline_up`.
