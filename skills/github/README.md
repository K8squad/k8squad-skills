# `github` Skill

Remote git / PR / issue operations via the GitHub MCP.

- **Focus:** dev
- **Category:** default
- **Source:** git — `github.com/K8squad/k8squad-skills` path `skills/github`, pinned to commit `bf3bc86`
- **Attach to roles:** Coder, Code Reviewer, DevOps
- **Permissions (least-privilege):** `scm:read`, `scm:write`, `pr:write`, `issue:write`
- **MCP tools:** `github-mcp` (streamable-http)
- **Toolchains:** `gh@2.62` (ships in the cluster default catalog)

## Prerequisites (fail-closed)

This skill resolves against live capability-plane objects — the Run is
rejected at admission until all of them check out:

1. **An `MCPServer` named `github-mcp`** in the skill's namespace (see
   [`examples/bmad-team/02b-mcpservers.yaml`](https://github.com/K8squad/K8squad/tree/main/examples/bmad-team)
   in the main repo for a ready template: streamable-http transport,
   GitHub Copilot MCP endpoint, `toolFilter: allow ["*"] / deny ["delete_*"]`).
   A dangling `mcpToolRefs` entry rejects the Skill at admission.
2. **Discovery succeeded** — `status.observedTools` non-empty and
   `ToolsDiscovered=True`. The control-plane discovery controller probes the
   server (`initialize` → `tools/list`) on create and every
   `discovery.intervalMinutes` (default 10). Until the first probe succeeds,
   Runs referencing this skill stay Pending (ADR-042 staleness — never admit
   against an unknown tool surface).
3. **The token Secret** referenced by `MCPServer.spec.credentialSecretRef`
   (e.g. `github-mcp-token`, key `token`). It is projected into the Run pod
   only as an env var (`KSQUAD_MCP_GITHUB_MCP_TOKEN`) — never into any file
   the runtime reads (ADR-045 D5). A missing Secret sets
   `CredentialsValid=False` and blocks the Run.
4. **The toolchain catalog**: enable it at install time
   (`--set tools.defaultCatalog.enabled=true`) so `gh@2.62` resolves; an
   unknown `name@version` rejects the Run at admission.

The skill can only *narrow* the server's envelope: `mcpToolRefs` selects
which server to grant — it carries no filter of its own, so a skill can
never widen `MCPServer.spec.toolFilter` (trust boundary D8). The effective
tool set is computed at Run assembly: server `allow` globs (empty = all
observed tools) minus `deny` globs; an empty effective set fails closed.

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
  `ksquad.skill.source.sha`, `ksquad.mcp.server`.
- Prometheus metrics on the operator: `ksquad_skill_loads_total`,
  `ksquad_tool_calls_total`, `ksquad_mcp_call_duration_seconds`,
  `ksquad_tool_usage_pipeline_up`.
