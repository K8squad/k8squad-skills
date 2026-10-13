# `blog-engine` Skill

Full-lifecycle blog and newsletter authoring — plan, write, rewrite, audit, and
optimize long-form content for both search rankings (E-E-A-T, answer-first) and
AI-assistant citations (GEO/AEO). **Text-only**: it reads source material and
writes Markdown/MDX/HTML prose, outlines, briefs, and JSON-LD schema. It
generates no images or audio, calls no external API, holds no credential, and
never publishes.

- **Focus:** content
- **Category:** content
- **Source:** inline — the skill body is the authoring playbook the agent reads
  (ported from the Content Writer's local 20-command `blog` suite, reduced to
  its text-only commands: no image/audio/Google-API/NotebookLM modes, which need
  credentials or network egress this skill intentionally omits)
- **Attach to roles:** Content Writer, DevRel
- **Permissions (least-privilege):** `content:write`, `content:read`,
  `asset:write` (writes drafts under `blog/`)
- **MCP tools:** none — carries no `mcpToolRefs`, adds no dangling-ref admission
  surface, needs no credential
- **Toolchains:** none — pure prompt transformation, tool-agnostic

## Commands

`write`, `rewrite`, `outline`, `brief`, `strategy`, `calendar`, `analyze`,
`audit`, `geo`, `seo-check`, `schema`, `factcheck`, `cannibalization`,
`taxonomy`, `persona`, `update` — the text-only subset of the 20-command blog
suite. Image generation, audio/TTS, Google-API data, and NotebookLM research are
deliberately excluded because they require credentials or network egress; add
them later as separate capability-gated skills if the board provisions the
backing MCP servers.

## What the body does

Drives each mode against the 6 pillars of dual optimization — answer-first
structure, sourced evidence, scannable hierarchy, entity clarity, citation
capsules, and freshness — and scores finished posts on a 5-category / 100-point
rubric with AI-content-detection flags. Every statistic keeps its source; any
unsourced claim is marked UNVERIFIED rather than asserted.

## Gate

**None.** Ships immediately — text-only, no credential, no network call.

## Pair with

- [`doc-convert`](../doc-convert) — export the finished article to docx/pdf/html.
- [`blog-publish`](../blog-publish) — publish it to WordPress/Ghost/Hashnode/Medium.
- [`social-repurpose`](../social-repurpose) — spin derivatives for social/email.
- [`youtube-storyboard`](../youtube-storyboard) — turn the post into a video plan.

## Install

```sh
kubectl apply -f skills/blog-engine/skill.yaml
```

## Wire it

```yaml
# Role.spec.defaultSkills[] — granted to all agents of the role
defaultSkills:
  - name: blog-engine

# Agent.spec.skillRefs[] — granted to one agent (overrides role defaults)
skillRefs:
  - name: blog-engine
```
