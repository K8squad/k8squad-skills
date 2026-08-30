# `dynatrace` Skill

Dynatrace control-plane observability via the `dtctl` CLI.

- **Focus:** debug
- **Category:** default
- **Source:** git — the agent-facing body is sourced from the **upstream**
  `github.com/dynatrace-oss/dtctl` repo, path `skills/dtctl`, pinned to commit
  `592aaac22c5edda904aacd678fdb9518cb496b6d` (Apache-2.0, (c) Dynatrace).
  Sourced, not vendored: no drift, and the pin exercises the capability
  plane's external git-source exactly as designed (arch §5.3.6). Only the
  envelope (`skill.yaml`: permissions, toolchains) and this
  human-facing README live in this repo.
- **Attach to roles:** Observability
- **Permissions (least-privilege):** `observability:read`, `telemetry:query`
- **Toolchains:** `dtctl@1.0` (ships in the cluster default catalog)

This skill drives Dynatrace through the `dtctl` CLI toolchain — it does
**not** require an `MCPServer`. `dtctl` speaks to the Dynatrace API directly,
authenticated by a BYO token env var, so there is no MCP sidecar to run or
discover.

## What the fetched body teaches

The upstream `skills/dtctl/SKILL.md` (agentskills.io format) is the official
agent instruction set for operating `dtctl`: initialization
(`dtctl commands` / `inventory` / `auth status`), DQL execution via
`dtctl query` with the `references/DQL-reference.md` required reading,
agent-oriented output modes (`--agent`, `-o toon`, `--jq`), spill-file
handling with `dtctl inspect` (no Grail re-query), token-frugal log pattern
analysis, dashboards/notebooks, and the permissions/safety model
(`dtctl auth can-i`, context safety levels).

The envelope above stays read-first (`observability:read`,
`telemetry:query`); the fetched body can never widen it (trust boundary D8).
Mutating dtctl verbs the body describes (`apply`, `delete`, `share`,
`restore`) are outside this skill's grant and require the dtctl context's
own safety level to allow them.

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

## Local development install (outside k8squad)

In a Run, `dtctl` arrives via the `dtctl@1.0` toolchain (cluster default
catalog) — nothing to install. Humans bootstrapping a workstation get the
same tooling from upstream:

```sh
brew install dynatrace-oss/tap/dtctl   # macOS / Linux (Homebrew)
dtctl skills install                   # install the upstream dtctl agent skill
```

Other install paths (release binaries, `go install`, containers) are
documented upstream at
[`github.com/dynatrace-oss/dtctl`](https://github.com/dynatrace-oss/dtctl).
The wider Dynatrace agent-skills collection (DQL essentials, service /
frontend observability packs) lives at
[`github.com/Dynatrace/dynatrace-for-ai`](https://github.com/Dynatrace/dynatrace-for-ai)
— the catalog already git-sources
[`dt-dql-essentials`](../dt-dql-essentials) from it.

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

> **Note:** git-sourced from the upstream `dynatrace-oss/dtctl` repo. The
> `ref` is pinned to an immutable **commit SHA** (never a floating branch,
> arch §5.3.6) — a force-push upstream cannot alter the behavior of an
> in-flight Run. Re-pin deliberately to a newer upstream commit to pick up
> dtctl instruction updates, and review the upstream diff when you do. The
> envelope (permissions, toolchains) is authored here and is
> never self-widened by the fetched body (D8).

## Usage instrumentation (free)

Skill/tool usage is reported automatically — nothing to opt into:

- OTel spans: `skill.load` and `gen_ai.tool.call` (GenAI semconv:
  `gen_ai.tool.name`, `gen_ai.tool.call.arguments` = hex sha256 of the args),
  carrying `ksquad.run.id`, `ksquad.agent.name`, `ksquad.skill.name`,
  `ksquad.skill.source.sha`.
- Prometheus metrics on the operator: `ksquad_skill_loads_total`,
  `ksquad_tool_calls_total`, `ksquad_tool_usage_pipeline_up`.
