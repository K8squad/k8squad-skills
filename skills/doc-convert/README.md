# `doc-convert` Skill

Convert a Markdown/HTML source into a shareable deliverable — Word (`.docx`),
PDF, standalone HTML, or PowerPoint (`.pptx`) — using the `pandoc` toolchain
(which also provides `weasyprint` and `typst` for high-fidelity PDF). The export
leg of the content pipeline: `blog-engine` writes the prose, `doc-convert` turns
it into a file. It runs local converters on files already in the workspace,
fetches nothing from the network, and holds no credential.

- **Focus:** content
- **Category:** content
- **Source:** inline — the skill body is the conversion playbook the agent reads
- **Attach to roles:** Content Writer, DevRel
- **Permissions (least-privilege):** `fs:read`, `fs:write:workspace`,
  `exec:pandoc`, `exec:weasyprint`, `exec:typst`, `asset:write`
- **MCP tools:** none
- **Toolchains:** `pandoc@3` — **BYO.** The operator must define the `pandoc`
  `Toolchain` object (provided by this catalog's `toolchains/pandoc.yaml`:
  `ghcr.io/k8squad/toolchains/pandoc:3`, `provides: [pandoc, weasyprint, typst]`).
  Not part of the default curated catalog, so apply `toolchains/` into your
  namespace before a Run grants this skill.

## What the body does

Picks the right converter per target format: `pandoc` for docx/html/pptx,
`weasyprint` from HTML for CSS-faithful PDF or `--pdf-engine=typst` for a fast
typographic PDF. Supports `--reference-doc` house-style templates for docx/pptx,
resolves images to local paths, verifies the output is non-empty, and reports
any content that degraded during conversion. `marp` is noted as the alternative
for slide-native theming when a richer deck is wanted.

## Gate

**None** — ships immediately. Requires only that the operator has applied the
`pandoc` toolchain (WS-1, ISI-5768) into the namespace, which this catalog
already ships under `toolchains/`.

## Pair with

- [`blog-engine`](../blog-engine) — writes the article this skill exports.
- [`tech-docs`](../tech-docs) — writes the ADRs/runbooks this skill exports.
- [`youtube-storyboard`](../youtube-storyboard) — export a storyboard package.

## Install

```sh
kubectl apply -f skills/doc-convert/skill.yaml
# plus the toolchain it resolves against:
kubectl apply -f toolchains/pandoc.yaml
```

## Wire it

```yaml
# Role.spec.defaultSkills[] — granted to all agents of the role
defaultSkills:
  - name: doc-convert

# Agent.spec.skillRefs[] — granted to one agent (overrides role defaults)
skillRefs:
  - name: doc-convert
```
