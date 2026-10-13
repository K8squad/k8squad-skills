# `slides-deck` Skill

Author presentation decks from an outline or blog post and export them to PPTX
and PDF. Markdown (Marp) is the single source of truth; `marp` renders slides
and PDF, `pandoc` is an alternate PDF path for richer typesetting.

- **Focus:** design
- **Category:** design
- **Source:** inline — the body is the deck-authoring + export playbook (ported
  from the local `python-pptx` / `marp` skills; local files only, no network)
- **Attach to roles:** Graphic Designer, Content Writer
- **Permissions (least-privilege):** `slides:render`, `asset:write` (writes
  `deck.md` / `.pptx` / `.pdf` under `decks/`)
- **MCP tools:** none — deterministic local rendering, no credential
- **Toolchains:** `marp@4` (provides `marp`), `pandoc@3` (provides `pandoc`,
  `weasyprint`, `typst`) — both long-tail CRs, applied per-namespace via
  `kubectl apply -k toolchains/`

## What the body does

Shapes a narrative arc (title, agenda, one-idea-per-slide, section dividers,
closing CTA), authors Marp Markdown with front-matter and `---` separators and
presenter notes in HTML comments, then exports `--pptx` / `--pdf` / `--html`.
Verifies slide count and embedded-chart resolution, and documents the Google
Slides path (export PPTX, then import). Writes outputs under `decks/{slug}/`.

## Gate

**None.** Ships immediately — deterministic local rendering, no credential, no
network call. Requires the `marp` and `pandoc` long-tail toolchain images
(ISI-5768 WS-1) to be present in the target namespace.

## Pair with

- [`dataviz`](../dataviz) / [`image-gen`](../image-gen) — produce charts/media,
  then embed them in the deck.

## Install

```sh
kubectl apply -f skills/slides-deck/skill.yaml
# plus the long-tail toolchains the skill requires:
kubectl apply -k toolchains/   # brings in marp@4, pandoc@3
```

## Wire it

```yaml
# Role.spec.defaultSkills[] — granted to all agents of the role
defaultSkills:
  - name: slides-deck

# Agent.spec.skillRefs[] — granted to one agent (overrides role defaults)
skillRefs:
  - name: slides-deck
```
