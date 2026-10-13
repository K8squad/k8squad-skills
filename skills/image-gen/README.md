# `image-gen` Skill

Generate and edit blog-quality imagery — hero images, inline illustrations,
social preview / OG cards — through a granted image-generation MCP server
(Gemini for editorial/illustration, fal.ai / FLUX for photoreal + typography).
Claude acts as creative director, constructing a six-component prompt.

- **Focus:** design
- **Category:** design
- **Source:** inline — the body is the creative-director playbook (ported from
  the local `blog-image` + `flux-best-practices` skills)
- **Attach to roles:** Graphic Designer, Content Writer
- **Permissions (least-privilege):** `image:generate`, `asset:write` (writes
  images under `images/`)
- **MCP tools:** `gemini-image`, `fal` — the generation providers. Carries **no
  credential**; tokens live on each MCP server's `credentialSecretRef` and are
  projected per-Run (`KSQUAD_MCP_GEMINI_TOKEN` / `KSQUAD_MCP_FAL_TOKEN`).
- **Toolchains:** `node@22` (cluster default catalog) — composites real title
  text onto generated art for crisp OG cards

## What the body does

Picks a domain mode (Editorial / Product / Landscape / UI-Web / Infographic /
Abstract), constructs a Subject+Action+Context+Composition+Lighting+Style
prompt, generates variants, screens for artifacts, composites OG-card text
locally, and writes `images/{slug}-{placement}.{png|webp}` with accessible alt
text. Respects brand/IP (no real logos, characters, or public figures).

## Gate

**Credential-gated.** Ships authored now with **empty provider secret refs**;
go-live requires the **board** to provision the Gemini + fal.ai MCP servers and
their credential Secrets (`KSQUAD_MCP_GEMINI_TOKEN`, `KSQUAD_MCP_FAL_TOKEN`).
Until then the `mcpToolRefs` are dangling, so this skill is **intentionally NOT
listed in `kustomization.yaml`** (a dangling ref rejects the Skill at
admission). WS-8 (ISI-5775) wires it in once the gate clears. No secret ever
lives in this repo (ISI-5754 §7).

## Pair with

- [`dataviz`](../dataviz) — vector charts (no raster generation needed).
- [`video-gen`](../video-gen) — animate a generated still.
- [`slides-deck`](../slides-deck) — embed generated imagery in a deck.

## Install

```sh
# Authored for review; do NOT apply until the board provisions the image
# providers and WS-8 wires it into the catalog.
kubectl apply -f skills/image-gen/skill.yaml
```

## Wire it

```yaml
# Role.spec.defaultSkills[] — granted to all agents of the role
defaultSkills:
  - name: image-gen

# Agent.spec.skillRefs[] — granted to one agent (overrides role defaults)
skillRefs:
  - name: image-gen
```
