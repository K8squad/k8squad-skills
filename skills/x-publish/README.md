# `x-publish` Skill

Publish a single tweet or a full thread to X (Twitter) and read back per-post
engagement stats — through the granted `x` MCP server. The skill carries **no
credential**; the X API v2 token lives on the MCP server and is projected
per-Run as an env var.

- **Focus:** content / social
- **Category:** social
- **Source:** inline — the body is the posting playbook the agent reads
- **Attach to roles:** Content Writer, DevRel / Social
- **Permissions (least-privilege):** `social:publish`, `social:read`
- **MCP tools:** `mcpToolRefs: [x]` — tweet/thread/stats run through this
  server's tools only
- **Toolchains:** none

## 🚦 Go-live gate (ISI-5774 §7 decision #3)

**This skill is authored now but is NOT live until the board provisions an X
credential.** Unblock owner = **BOARD (Henrik)**. No secret ever lives in this
repo. Go-live requires the operator to create, in the skill's namespace:

1. **An `x` `MCPServer`** exposing the tweet / thread / stats tools, with a
   `credentialSecretRef` pointing at ↓.
2. **A `Secret`** holding an **X API v2 paid-tier** token (write access to the
   X API v2 is a paid tier). The platform projects it per-Run as
   `KSQUAD_MCP_X_TOKEN`, env-only, never a file (ADR-045 D5).

Until both objects exist, this skill is **intentionally kept out of the root
`kustomization.yaml`**: its `mcpToolRefs: [x]` would be a dangling ref and reject
at admission. Wire it in (via WS-8 catalog-wiring) once credentials are
provisioned.

See `examples/bmad-team/02b-mcpservers.yaml` in the main repo for the
`MCPServer` + `credentialSecretRef` template.

## What the body does

Validates every tweet against the 280-char limit, confirms before the first
outward-facing post, posts a single tweet or chains a thread (each tweet replying
to the previous returned ID, with fail-stop that surfaces any partial thread to
the user), echoes the permalinks, and reports engagement stats on request. It
generates no media — pair with the design skills for assets and
`social-repurpose` for the copy.

## Pair with

- [`social-repurpose`](../social-repurpose) — draft the thread copy (ungated).
- [`social-stats`](../social-stats) — cross-platform engagement roll-up.

## Install (after the gate clears)

```sh
kubectl apply -f skills/x-publish/skill.yaml
```

## Wire it

```yaml
skillRefs:
  - name: x-publish
```
