# `linkedin-publish` Skill

Publish a prepared LinkedIn post, schedule it, and read back engagement stats —
through the granted `linkedin` MCP server. The skill carries **no credential**;
the LinkedIn OAuth token lives on the MCP server and is projected per-Run as an
env var.

- **Focus:** content / social
- **Category:** social
- **Source:** inline — the body is the posting playbook the agent reads
- **Attach to roles:** Content Writer, DevRel / Social
- **Permissions (least-privilege):** `social:publish`, `social:read`
- **MCP tools:** `mcpToolRefs: [linkedin]` — publish/schedule/stats run through
  this server's tools only
- **Toolchains:** none

## 🚦 Go-live gate (ISI-5774 §7 decision #3)

**This skill is authored now but is NOT live until the board provisions a
LinkedIn credential.** Unblock owner = **BOARD (Henrik)**. No secret ever lives
in this repo. Go-live requires the operator to create, in the skill's namespace:

1. **A `linkedin` `MCPServer`** exposing the post / schedule / comment / stats
   tools, with a `credentialSecretRef` pointing at ↓.
2. **A `Secret`** holding a LinkedIn OAuth app token (an app registered on the
   LinkedIn Developer portal with the `w_member_social` / organization-post
   scopes). The platform projects it per-Run as `KSQUAD_MCP_LINKEDIN_TOKEN`,
   env-only, never a file (ADR-045 D5).

Until both objects exist, this skill is **intentionally kept out of the root
`kustomization.yaml`**: its `mcpToolRefs: [linkedin]` would be a dangling ref and
reject at admission. Wire it in (via WS-8 catalog-wiring) once credentials are
provisioned.

See `examples/bmad-team/02b-mcpservers.yaml` in the main repo for the
`MCPServer` + `credentialSecretRef` template.

## What the body does

Validates a finished post (hook, length, author URN), confirms before the first
outward-facing post, publishes now or schedules for an ISO-8601 time, puts links
in the first comment (LinkedIn deprioritizes in-body links), echoes the returned
post URN, and reports basic engagement stats on request. It writes nothing media
— pair with the design skills for assets and `social-repurpose` for the copy.

## Pair with

- [`social-repurpose`](../social-repurpose) — draft the post copy (ungated).
- [`social-stats`](../social-stats) — cross-platform engagement roll-up.

## Install (after the gate clears)

```sh
kubectl apply -f skills/linkedin-publish/skill.yaml
```

## Wire it

```yaml
skillRefs:
  - name: linkedin-publish
```
