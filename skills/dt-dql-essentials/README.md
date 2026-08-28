# `dt-dql-essentials` Skill

Core DQL (Dynatrace Query Language) syntax, pitfalls, query patterns, and
query optimization — the knowledge pack an agent loads before writing,
building, fixing, or optimizing a DQL query.

- **Focus:** debug
- **Category:** default
- **Source:** git — `github.com/Dynatrace/dynatrace-for-ai` path
  `skills/dt-dql-essentials`, pinned to commit `08ef3f38d5daeb0e687ac4baf505658906282814`
  (Apache-2.0, (c) Dynatrace — sourced upstream, not vendored, so the catalog
  tracks upstream fixes by re-pinning the SHA)
- **Attach to roles:** Observability, Test Architect, DevOps
- **Permissions (least-privilege):** `observability:read`, `telemetry:query`
- **MCP tools:** none — this is a pure knowledge skill; it carries no
  `mcpToolRefs` (so it never adds a dangling-ref admission surface) and pairs
  with whatever Dynatrace query capability the Run already holds
- **Toolchains:** none — the DQL knowledge is tool-agnostic. Agents that also
  carry the [`dynatrace`](../dynatrace) skill run the queries through the
  `dtctl` CLI toolchain; where the platform provides a `dynatrace-mcp`
  `MCPServer`, the same knowledge drives its `query_*` tools

## What the fetched body teaches

The upstream `SKILL.md` (agentskills.io format) routes the agent to the right
reference file per task: field namespaces and data models, query optimization
(filter early, bucket filters, short time ranges, field selection, sampling,
cardinality — less data scanned = cheaper queries), smartscape topology
navigation, `summarize`/`makeTimeseries` bucketing, iterative and conditional
expressions, operators, and string matching, plus a full DQL command/function
index.

## Prerequisites

None of its own — this skill carries knowledge, not a tool. It declares no
`mcpToolRefs` and no toolchain, so it always resolves at admission and adds no
capability-plane surface of its own.

To actually *run* the DQL this skill teaches, pair it with a Dynatrace query
capability in the same Run:

- the [`dynatrace`](../dynatrace) skill (executes DQL via the `dtctl@1.0` CLI
  toolchain), or
- a platform-provided `dynatrace-mcp` `MCPServer` exposing `query_*` tools.

The `observability:read` / `telemetry:query` permissions here scope the
knowledge to read-first use; the paired capability enforces its own grant.

## Install

```sh
kubectl apply -f skills/dt-dql-essentials/skill.yaml
```

## Wire it

```yaml
# Role.spec.defaultSkills[] — granted to all agents of the role
defaultSkills:
  - name: dt-dql-essentials

# Agent.spec.skillRefs[] — granted to one agent (overrides role defaults)
skillRefs:
  - name: dt-dql-essentials
```

> **Note:** git-sourced. The `ref` is pinned to an immutable **commit SHA**
> on the upstream repo (never a floating branch, arch §5.3.6) — a force-push
> upstream cannot alter the behavior of an in-flight Run. Re-pin deliberately
> to a newer upstream commit to pick up DQL reference updates, and review the
> upstream diff when you do.
