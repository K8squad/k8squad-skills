# `social-stats` Skill

Collect engagement metrics for already-published posts across LinkedIn and X and
report them as one comparable roll-up — through the granted `linkedin` and `x`
MCP servers. **Read-only**, and carries **no credential**; each platform's token
lives on its MCP server and is projected per-Run as an env var.

- **Focus:** content / social
- **Category:** social
- **Source:** inline — the body is the collection + reporting playbook
- **Attach to roles:** Content Writer, DevRel / Social
- **Permissions (least-privilege):** `social:read`
- **MCP tools:** `mcpToolRefs: [linkedin, x]` — stats are read through these
  servers' tools only
- **Toolchains:** none

## 🚦 Go-live gate (ISI-5774 §7 decision #3)

**This skill is authored now but is NOT live until the board provisions the
LinkedIn and/or X credentials.** Unblock owner = **BOARD (Henrik)**. No secret
ever lives in this repo. Go-live requires the operator to create, in the skill's
namespace, the `linkedin` and `x` `MCPServer`s plus their `credentialSecretRef`
Secrets — the same objects the `linkedin-publish` and `x-publish` READMEs
describe. The platform projects them per-Run as `KSQUAD_MCP_LINKEDIN_TOKEN` /
`KSQUAD_MCP_X_TOKEN`, env-only (ADR-045 D5). A platform whose server is missing
is skipped and flagged "not configured" rather than failing the report.

Until those objects exist, this skill is **intentionally kept out of the root
`kustomization.yaml`**: its `mcpToolRefs` would be dangling refs and reject at
admission. Wire it in (via WS-8 catalog-wiring) once credentials are provisioned.

## What the body does

Pulls per-post metrics from each platform's MCP stats tool, normalizes them onto
a common shape (impressions / reactions / comments / shares / engagement-rate),
and produces a compact table plus per-platform and combined totals, the top posts
by engagement rate, and one line of plain-language insight. It reports only what
the APIs return — never scrapes, never fabricates a metric.

## Pair with

- [`linkedin-publish`](../linkedin-publish) / [`x-publish`](../x-publish) —
  publish the posts this skill measures.
- [`social-repurpose`](../social-repurpose) — draft the copy (ungated).

## Install (after the gate clears)

```sh
kubectl apply -f skills/social-stats/skill.yaml
```

## Wire it

```yaml
skillRefs:
  - name: social-stats
```
