# `audio-music` Skill

Generate voiceover (narration/dialogue), sound effects, and music (beds,
jingles, stems) for video and content production — through a granted audio MCP
server (ElevenLabs for TTS / SFX / music) plus the local `ffmpeg` toolchain for
deterministic post-processing.

- **Focus:** design
- **Category:** design
- **Source:** inline — the body is the audio-production playbook (ported from
  the local `elevenlabs` / `music` / `acestep` skills)
- **Attach to roles:** Graphic Designer, Content Writer
- **Permissions (least-privilege):** `audio:generate`, `asset:write` (writes
  under `audio/`)
- **MCP tools:** `elevenlabs` — the generation provider. Carries **no
  credential**; the token lives on the MCP server's `credentialSecretRef`,
  projected per-Run as `KSQUAD_MCP_ELEVENLABS_TOKEN`.
- **Toolchains:** `ffmpeg@7` (provides `ffmpeg`, `ffprobe`) for loudness
  normalization, trim/fade, ducking, mixing, and transcode

## What the body does

Picks the deliverable (VO / SFX / music), prepares the request (script chunking
and pronunciation notes for VO; material/space for SFX; mood + composition plan
+ exact length for music), generates via the audio MCP tool, then uses ffmpeg
to normalize (−16 LUFS for VO over music), trim/fade, duck music under
narration, layer VO+SFX+bed, and transcode. Saves stems separately so a video
edit can re-balance. Respects IP/likeness (no unauthorized voice cloning).

## Gate

**Credential-gated.** Authored now with an **empty provider secret ref**;
go-live requires the **board** to provision the ElevenLabs MCP server and its
Secret (`KSQUAD_MCP_ELEVENLABS_TOKEN`). Until then the `mcpToolRefs` is
dangling, so this skill is **intentionally NOT listed in `kustomization.yaml`**;
WS-8 (ISI-5775) wires it in once the gate clears. The ffmpeg **processing** path
works on existing audio without any provider. No secret in repo (ISI-5754 §7).

## Pair with

- [`video-gen`](../video-gen) — mux the generated VO / music into a clip.
- [`slides-deck`](../slides-deck) — narrate a deck walkthrough.

## Install

```sh
# Authored for review; do NOT apply until the board provisions the audio
# provider and WS-8 wires it into the catalog.
kubectl apply -f skills/audio-music/skill.yaml
kubectl apply -k toolchains/   # brings in ffmpeg@7
```

## Wire it

```yaml
# Role.spec.defaultSkills[] — granted to all agents of the role
defaultSkills:
  - name: audio-music

# Agent.spec.skillRefs[] — granted to one agent (overrides role defaults)
skillRefs:
  - name: audio-music
```
