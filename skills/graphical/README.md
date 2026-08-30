# `graphical` Skill

Diagram / SVG asset rendering.

- **Focus:** dev
- **Category:** default
- **Source:** git — `github.com/K8squad/k8squad-skills` path `skills/graphical`, pinned to commit `bf3bc86`
- **Attach to roles:** Graphical Designer, Architect
- **Permissions (least-privilege):** `render:svg`, `asset:write`
- **MCP tools:** none
- **Toolchains:** `node@22` (ships in the cluster default catalog)

## Prerequisites (fail-closed)

1. **The toolchain catalog**: enable it at install time
   (`--set tools.defaultCatalog.enabled=true`) so `node@22` resolves. An
   unknown `name@version` rejects the Run at admission with an actionable
   message; version conflicts across a Run's skills (say this skill at
   `node@22` and another at `node@20`) also fail closed — no silent
   latest-wins.

`node` declares no Kubernetes RBAC in the catalog — it is staged onto `PATH`
by an init container (digest-pinned image, read-only shared volume) with no
API grant at all.

## Install

```sh
kubectl apply -f skills/graphical/skill.yaml
```

## Wire it

Grant to every agent under a role (default) or to a single agent:

```yaml
# Role.spec.defaultSkills[] — granted to all agents of the role
defaultSkills:
  - name: graphical

# Agent.spec.skillRefs[] — granted to one agent (overrides role defaults)
skillRefs:
  - name: graphical
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
