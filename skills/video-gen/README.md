# `video-gen` Skill

Generate short video clips from text or a reference image, edit/trim them, and
assemble a finished piece — through a granted video MCP server (HeyGen for
prompt-to-video / avatars, fal.ai for gateway models like VEO / Kling /
Seedance / MiniMax) plus the local `ffmpeg` toolchain for deterministic editing.

- **Focus:** design
- **Category:** design
- **Source:** inline — the body is the generation + editing playbook (ported
  from the local `ai-video-gen` / `create-video` / `video-toolkit` / `remotion`
  skills)
- **Attach to roles:** Graphic Designer, Content Writer
- **Permissions (least-privilege):** `video:generate`, `asset:write` (writes
  under `video/`)
- **MCP tools:** `heygen`, `fal` — the generation providers. Carries **no
  credential**; tokens live on each MCP server's `credentialSecretRef`,
  projected per-Run (`KSQUAD_MCP_HEYGEN_TOKEN` / `KSQUAD_MCP_FAL_TOKEN`).
- **Toolchains:** `ffmpeg@7` (provides `ffmpeg`, `ffprobe`) for editing;
  `node@22` (cluster default catalog) for Remotion-style programmatic assembly

## What the body does

Scopes mode (text- or image-to-video), duration, and aspect; prompts the model
with motion/camera language; downloads the clip; then uses ffmpeg to trim,
stitch, reframe (9:16 shorts), add audio, overlay lower-thirds, and compress.
Documents the Remotion/node path for templated, data-driven video. Writes
`video/{slug}.mp4`, keeping raw clips under `video/raw/`. Respects brand/IP and
likeness.

## Gate

**Credential-gated.** Authored now with **empty provider secret refs**;
go-live requires the **board** to provision the HeyGen + fal.ai MCP servers and
their Secrets (`KSQUAD_MCP_HEYGEN_TOKEN`, `KSQUAD_MCP_FAL_TOKEN`). Until then
the `mcpToolRefs` are dangling, so this skill is **intentionally NOT listed in
`kustomization.yaml`**; WS-8 (ISI-5775) wires it in once the gate clears. The
ffmpeg **editing** path works on existing clips without any provider. No secret
in repo (ISI-5754 §7).

## Pair with

- [`image-gen`](../image-gen) — generate the still that image-to-video animates.
- [`audio-music`](../audio-music) — voiceover / music track to mux in.

## Install

```sh
# Authored for review; do NOT apply until the board provisions the video
# providers and WS-8 wires it into the catalog.
kubectl apply -f skills/video-gen/skill.yaml
kubectl apply -k toolchains/   # brings in ffmpeg@7
```

## Wire it

```yaml
# Role.spec.defaultSkills[] — granted to all agents of the role
defaultSkills:
  - name: video-gen

# Agent.spec.skillRefs[] — granted to one agent (overrides role defaults)
skillRefs:
  - name: video-gen
```
