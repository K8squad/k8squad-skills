# `youtube-storyboard` Skill

Turn a topic, blog post, or show-notes doc into a production-ready video
package: a spoken **script**, a scene-by-scene **storyboard**, and a **shot
list**. **Text-only**: it writes the plan that a video-generation step (the
`video-gen` skill / WS-3) or a human editor then produces. It renders no video,
calls no external API, and holds no credential.

- **Focus:** content
- **Category:** content
- **Source:** inline — the skill body is the scripting/storyboarding playbook
- **Attach to roles:** Content Writer, DevRel
- **Permissions (least-privilege):** `content:write`, `asset:write` (writes the
  package under `storyboard/`)
- **MCP tools:** none
- **Toolchains:** none — pure prompt transformation, tool-agnostic

## What the body does

Extracts the hook, teaching beats, strongest data/demo moment, and CTA from the
source, then produces three aligned artifacts: a timecoded spoken script
(hook → intro → body beats → CTA at ~150 words/min), a per-scene storyboard
table (visual, on-screen text, VO line, notes), and a flattened, checkable shot
list (shot type, source, duration, asset dependency). It marks which shots need
AI generation versus live capture so production can batch them.

## Gate

**None** — ships immediately; text-only, no credential, no network call.

## Pair with

- [`blog-engine`](../blog-engine) — the written source this skill adapts.
- `video-gen` (WS-3, ISI-5770) — generates the AI shots this skill specifies.
- [`doc-convert`](../doc-convert) — export the storyboard package to docx/pdf.
- [`social-repurpose`](../social-repurpose) — the YouTube script path overlaps;
  use this skill for full storyboards, `social-repurpose` for a quick script.

## Install

```sh
kubectl apply -f skills/youtube-storyboard/skill.yaml
```

## Wire it

```yaml
# Role.spec.defaultSkills[] — granted to all agents of the role
defaultSkills:
  - name: youtube-storyboard

# Agent.spec.skillRefs[] — granted to one agent (overrides role defaults)
skillRefs:
  - name: youtube-storyboard
```
