# `tech-docs` Skill

Author structured engineering documents — Architecture Decision Records (ADRs),
operational runbooks, design docs, and READMEs — in the BMAD house style.
**Text-only**: it reads the codebase and context already in the workspace and
writes Markdown. It runs no tools, calls no external API, and holds no
credential.

- **Focus:** content
- **Category:** content
- **Source:** inline — the skill body is the documentation playbook the agent
  reads (reuses the BMAD doc conventions)
- **Attach to roles:** Content Writer, Architect, DevOps
- **Permissions (least-privilege):** `fs:read`, `fs:write:workspace`,
  `content:write`
- **MCP tools:** none
- **Toolchains:** none — pure prompt transformation, tool-agnostic

## What the body does

Drafts to the right template per document type — ADR (context / decision /
consequences / alternatives, sequentially numbered with supersede links),
runbook (trigger → diagnosis → remediation → rollback → verification →
escalation, written for a 3 a.m. page), design doc, or README. It gathers
context from the actual code and existing records first so documents reflect
what is there, makes every runbook command show expected output, and cross-links
related ADRs/runbooks/tickets by id. Anything it could not verify is flagged as
an open question rather than asserted.

## Gate

**None** — ships immediately; text-only, no credential, no network call.

## Pair with

- [`bmad`](../bmad) — the BMAD workflow that produces the specs these docs
  record.
- [`doc-convert`](../doc-convert) — export an ADR or runbook to docx/pdf.
- [`blog-engine`](../blog-engine) — turn a design doc into a public blog post.

## Install

```sh
kubectl apply -f skills/tech-docs/skill.yaml
```

## Wire it

```yaml
# Role.spec.defaultSkills[] — granted to all agents of the role
defaultSkills:
  - name: tech-docs

# Agent.spec.skillRefs[] — granted to one agent (overrides role defaults)
skillRefs:
  - name: tech-docs
```
