# `dataviz` Skill

Accessible, dark-mode-first SVG data visualization — bar, grouped bar,
lollipop, donut, line, area, and radar charts that read as one system on any
surface. Extends `graphical` with a charting grammar (one accent per view,
transparent background, source attribution, `role="img"` + `aria-label`).

- **Focus:** design
- **Category:** design
- **Source:** inline — the body is the charting playbook the agent reads
  (ported from the local `dataviz` skill; SVG-only, no network call)
- **Attach to roles:** Graphic Designer, Content Writer, Architect
- **Permissions (least-privilege):** `render:svg`, `asset:write` (writes `.svg`
  under `charts/`)
- **MCP tools:** none — carries no `mcpToolRefs`, so no dangling-ref admission
  surface and no credential
- **Toolchains:** `node@22` (ships in the cluster default catalog; only needed
  when a chart is generated from a Node/d3 script — hand-authored SVG needs none)

## What the body does

Matches the mark to the question, enforces the one-accent color rule with a
WCAG-AA contrast check on both near-black and near-white surfaces, keeps the
SVG transparent and responsive (`viewBox`, no fixed pixels, `currentColor`),
direct-labels values, and adds a source/as-of caption plus an `aria-label`
stating the headline finding. Writes `charts/{slug}.svg` and emits an inline
markup block for MDX/JSX.

## Gate

**None.** Ships immediately — SVG-only, no credential, no network call.

## Pair with

- [`graphical`](../graphical) — arbitrary diagrams/SVG outside the chart grammar.
- [`image-gen`](../image-gen) — when a raster (PNG/OG card) is needed instead.
- [`slides-deck`](../slides-deck) — embed the chart SVG into a deck.

## Install

```sh
kubectl apply -f skills/dataviz/skill.yaml
```

## Wire it

```yaml
# Role.spec.defaultSkills[] — granted to all agents of the role
defaultSkills:
  - name: dataviz

# Agent.spec.skillRefs[] — granted to one agent (overrides role defaults)
skillRefs:
  - name: dataviz
```
