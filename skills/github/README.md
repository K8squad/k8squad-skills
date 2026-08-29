# `github` Skill

Remote git / PR / issue operations via the GitHub CLI (`gh`).

- **Focus:** dev
- **Category:** default
- **Source:** git — `github.com/K8squad/k8squad-skills` path `skills/github`, pinned to commit `bf3bc86`
- **Attach to roles:** Coder, Code Reviewer, DevOps
- **Permissions (least-privilege):** `scm:read`, `scm:write`, `pr:write`, `issue:write`
- **Toolchains:** `gh@2.62` (ships in the cluster default catalog)

This skill drives GitHub through the `gh` CLI toolchain — it does **not**
require an `MCPServer`. The `gh` binary covers the full scm/pr/issue surface,
authenticated by a BYO token env var, so there is no MCP sidecar to run or
discover. (Skills that genuinely need a network tool surface reachable only
over MCP may still set `mcpToolRefs` — see the repo README capability-plane
section — but `github` doesn't.)

## Prerequisites (fail-closed)

This skill resolves against live capability-plane objects — the Run is
rejected at admission until they check out:

1. **The toolchain catalog** is enabled at install time
   (`--set tools.defaultCatalog.enabled=true`) so `gh@2.62` resolves; an
   unknown `name@version` rejects the Run at admission. The pack is staged as
   an init container (§5.3.2); version conflicts across a Run's skills fail
   closed (§5.3.4).
2. **A GitHub token** for `gh` — a BYO read-only/scoped token Secret projected
   into the Run pod **only as an env var** (`GH_TOKEN` / `GITHUB_TOKEN`), never
   into any file the runtime reads (ADR-045 D5). Wire it via the agent's
   credential projection; a missing token leaves `gh` unauthenticated and the
   skill's write permissions inert.

The CRD-authorized `permissions` envelope (`scm:*`, `pr:write`, `issue:write`)
is set by the operator/admin who registers the skill and is never widened by
the fetched skill body (trust boundary D8): a git-sourced body supplies
behavior *inside* the envelope, never a new capability.

## Install

```sh
kubectl apply -f skills/github/skill.yaml
```

## Wire it

Grant to every agent under a role (default) or to a single agent:

```yaml
# Role.spec.defaultSkills[] — granted to all agents of the role
defaultSkills:
  - name: github

# Agent.spec.skillRefs[] — granted to one agent (overrides role defaults)
skillRefs:
  - name: github
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
