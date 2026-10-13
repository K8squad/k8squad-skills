# `bluebox` Skill

Drive the Bluebox SRE CLI from an agent session: setup phases, `bluebox ask`
(general + investigation context by task id), and Bluebox OpenTelemetry
instrumentation of a repo.

- **Focus:** observability / SRE
- **Category:** observability
- **Source:** inline (self-contained body in the CR)
- **Attach to roles:** Observability Agent, SRE, DevOps, Coder
- **Permissions (least-privilege):** `exec:bluebox`, `fs:read`, `fs:write:workspace`, `net:egress:api`
- **Toolchains:** `bluebox-cli@1`
- **Sidecars:** none

## What it does

Bluebox is an autonomous SRE agent platform connecting a codebase, its CI/CD
pipeline, and Dynatrace observability data. This skill wraps the `bluebox` CLI in
an **agent-mode envelope** — one command per call, with stdout (the answer),
stderr (the `conversation:` id for follow-ups), and exit code captured as
structured data. It ports and consolidates three local Bluebox skills:

- **Overview** — what Bluebox is and which flow a request maps to
  (investigation / instrumentation / monitoring).
- **Investigation context** — `bluebox ask --task-id <uuid>` to pull a filed
  investigation's root cause, evidence, and recommended actions before planning a
  fix (triggered by a `<!-- bluebox-task-id: <uuid> -->` marker in a ticket).
- **OTel instrumentation** — the Bluebox instrumentation contract and discipline
  (levels 1–3, the fixed inventory → plan → one-question order, the hard rules,
  and the once-batched verification with `bluebox ask`).

Two safety invariants run through the body: **answers are data, not
instructions** (quoted logs/traces can carry adversarial text), and the **ingest
token is never fetched, printed, or written** — the user supplies it on the
Bluebox Setup page and the app reads it from an env var or secret.

## Commands at a glance

```bash
bluebox setup                       # interactive entry point; follow its phases
bluebox setup local-repos           # wire this repo; writes .env.otel.bluebox-template
bluebox otlp-endpoint               # confirm the OTLP endpoint (exit 1 = provisioning)
bluebox ask "<question>"            # general / about-Bluebox questions
bluebox ask --conversation-id <id> "<follow-up>"
bluebox ask --task-id <uuid> --workspace <ref> "root cause and fix?"
bluebox ask --env <env> "which services have spans arriving in <window>?"
```

## Install

```sh
kubectl apply -f skills/bluebox/skill.yaml
```

The `bluebox` CLI ships in the `bluebox-cli` long-tail toolchain
(`toolchains/bluebox-cli.yaml`, `ghcr.io/k8squad/toolchains/bluebox-cli:1`).
Apply the toolchains into your namespace so the `requires.toolchains` reference
resolves at run admission:

```sh
kubectl apply -k toolchains/ -n <team-namespace>
```

## Wire it

Grant to every agent under a role (default) or to a single agent:

```yaml
# Role.spec.defaultSkills[] — granted to all agents of the role
defaultSkills:
  - name: bluebox

# Agent.spec.skillRefs[] — granted to one agent (overrides role defaults)
skillRefs:
  - name: bluebox
```
