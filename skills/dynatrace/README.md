# `dynatrace` Skill

Dynatrace control-plane observability via the `dtctl` CLI.

- **Focus:** debug
- **Category:** default
- **Source:** git — `github.com/K8squad/k8squad-skills` path `skills/dynatrace`, pinned to commit `bf3bc86`
- **Attach to roles:** Observability
- **Permissions (least-privilege):** `observability:read`, `telemetry:query`
- **Toolchains:** `dtctl@1.0` (ships in the cluster default catalog)

This skill drives Dynatrace through the `dtctl` CLI toolchain — it does
**not** require an `MCPServer`. `dtctl` speaks to the Dynatrace API directly,
authenticated by a BYO token env var, so there is no MCP sidecar to run or
discover.

## Prerequisites (fail-closed)

This skill resolves against live capability-plane objects — the Run is
rejected at admission until they check out:

1. **The toolchain catalog** is enabled at install time
   (`--set tools.defaultCatalog.enabled=true`) so `dtctl@1.0` resolves; an
   unknown `name@version` rejects the Run at admission. The pack is staged as
   an init container (§5.3.2); version conflicts across a Run's skills fail
   closed (§5.3.4).
2. **A Dynatrace API token** for `dtctl` — a BYO scoped token Secret projected
   into the Run pod **only as an env var** (e.g. `DT_API_TOKEN`), never into
   any file the runtime reads (ADR-045 D5). A missing token leaves `dtctl`
   unauthenticated and the skill's query permissions inert.

The CRD-authorized `permissions` envelope (`observability:read`,
`telemetry:query`) is set by the operator/admin who registers the skill and is
never widened by the fetched skill body (trust boundary D8).

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
