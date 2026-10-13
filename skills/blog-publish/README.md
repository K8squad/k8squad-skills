# `blog-publish` Skill  🔒 [sec]

Publish or update a prepared article on a blogging platform — WordPress, Ghost,
Hashnode, or Medium — through the granted `blog-platform` MCP server, then read
back basic post metadata. This skill **never embeds a credential**: the platform
API token lives on the MCP server's `credentialSecretRef` and the platform
projects it per-Run as `KSQUAD_MCP_BLOG_PLATFORM_TOKEN`.

- **Focus:** content
- **Category:** content
- **Source:** inline — the skill body is the publishing playbook the agent reads
- **Attach to roles:** Content Writer (publishing-authorized)
- **Permissions (least-privilege):** `content:publish`, `content:read`
- **MCP tools:** `blog-platform` — a board-provisioned `MCPServer` fronting the
  WordPress / Ghost / Hashnode / Medium APIs, with its API token on
  `credentialSecretRef` (projected as `KSQUAD_MCP_BLOG_PLATFORM_TOKEN`, env-only,
  ADR-045 D5). The skill can only *narrow* the server's tool envelope, never
  widen it (trust boundary D8).
- **Toolchains:** none

## What the body does

Validates a finished article (body, slug, canonical URL, tags), confirms the
target blog with the user, then calls the `blog-platform` MCP `create_post` /
`update_post` tool. Defaults `status` to `draft` so a human reviews in the
platform editor before go-live, confirms before the first publish of a session,
echoes the returned post id/URL, and reads post metadata on request. It carries
no credential and makes no raw-HTTP call — all access is through the granted MCP
tools.

## Gate

**🔒 [sec] — go-live gated on a board-provisioned credential.** This skill is
authored now with an **empty Secret reference** per the ISI-5754 §7 ratified
decision: the board provisions the `blog-platform` `MCPServer` + credential
Secret (the "mcp-blog-platform" ask; converging on the self-service credential
vault, WS-9 ISI-5777) before go-live.

Until then this Skill is **intentionally NOT listed in the root
`kustomization.yaml`** — its `mcpToolRefs: [blog-platform]` is dangling, and a
dangling ref rejects the Skill at admission. WS-8 (ISI-5775) wires it into the
catalog once the gate clears.

- **Unblock owner:** BOARD (Henrik) — provision the `blog-platform` MCPServer +
  Secret, then WS-8 adds the kustomization entry.

## Pair with

- [`blog-engine`](../blog-engine) — writes and optimizes the article to publish.
- [`doc-convert`](../doc-convert) — export the same article to docx/pdf for
  non-web distribution.

## Install

> Do **not** apply until the `blog-platform` MCPServer + Secret exist in the
> namespace, or admission will reject the Skill.

```sh
kubectl apply -f skills/blog-publish/skill.yaml
```

## Wire it

```yaml
# Role.spec.defaultSkills[] — granted to publishing-authorized agents
defaultSkills:
  - name: blog-publish

# Agent.spec.skillRefs[] — granted to one agent (overrides role defaults)
skillRefs:
  - name: blog-publish
```
