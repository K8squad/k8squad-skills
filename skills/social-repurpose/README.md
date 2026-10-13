# `social-repurpose` Skill

Turn one long-form source — a blog post, newsletter, or YouTube show-notes doc —
into platform-optimized derivatives: an X/Twitter thread, a LinkedIn post, a
YouTube/livestream script, a Reddit discussion post, and an email newsletter
excerpt. **Text-only**: it reads source text and writes derivative text. It never
publishes, calls a social API, or holds a credential.

- **Focus:** content
- **Category:** social
- **Source:** inline — the skill body is the adaptation playbook the agent reads
  (ported from the Content Writer's local `blog-repurpose` skill; text-only, no
  publishing path)
- **Attach to roles:** Content Writer, DevRel / Social
- **Permissions (least-privilege):** `content:repurpose`, `asset:write` (writes
  derivative files under `repurposed/`)
- **MCP tools:** none — carries no `mcpToolRefs`, so it adds no dangling-ref
  admission surface and needs no credential
- **Toolchains:** none — pure prompt transformation, tool-agnostic

## What the body does

Extracts the reusable building blocks from the source (title, 5–7 key insights,
sourced statistics, quotes, thesis, TL;DR, audience) and regenerates them per
platform with each channel's conventions — thread hooks and 280-char limits for
X, pre-"see more" hooks and link-in-first-comment for LinkedIn, retention beats
and visual cues for YouTube, the 10% self-promotion rule for Reddit, and a single
CTA for email. Every statistic keeps its source attribution.

## Gate

**None.** This skill ships immediately — it is text-only, carries no credential,
and makes no network call. It is the ungated member of the Social category; the
three publishing/stats skills (`x-publish`, `linkedin-publish`, `social-stats`)
are gated on board-provisioned API credentials (ISI-5774 §7 decision #3).

## Pair with

- [`x-publish`](../x-publish) / [`linkedin-publish`](../linkedin-publish) — to
  actually post the derivatives this skill produces.
- [`social-stats`](../social-stats) — to measure how the posts performed.

## Install

```sh
kubectl apply -f skills/social-repurpose/skill.yaml
```

## Wire it

```yaml
# Role.spec.defaultSkills[] — granted to all agents of the role
defaultSkills:
  - name: social-repurpose

# Agent.spec.skillRefs[] — granted to one agent (overrides role defaults)
skillRefs:
  - name: social-repurpose
```
