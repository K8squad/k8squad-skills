# `task-io` Skill

Read and write **your own** work item — the coord-side analogue of Paperclip's
issue read/write, scoped to the agent's own run.

- **Focus:** platform
- **Category:** default (union baseline — attached at **every** Role)
- **Source:** git — `github.com/K8squad/k8squad-skills` path `skills/task-io`, pinned to a commit SHA
- **Attach to roles:** all (added to every Role's `defaultSkills`, never per-Agent)
- **Permissions (least-privilege):** `issue:read`, `issue:write`, `task:status`
- **Toolchains:** none — the coord API is plain HTTP (no CLI pack)

This skill grants **agency over your own task**, not *context*. K8squad
**PUSHES** your task context (title, description, acceptance criteria,
comments, goal) into your prompt when your Run starts — you do **not** fetch it
to begin (that boot-time push is S1 / ISI-3590). `task-io` is for the moments
*after* boot when you need to act on your own work item: re-read it (it may have
changed), leave a comment, report a status change, or claim the work.

It is **not** a general issue-browser and **not** a project reader. Every verb
operates only on the agent's own run/work-item, enforced by a run-scoped bearer
token bound to `RUN_ID` + `WORK_ITEM_ID` — a token minted for one run cannot
read or mutate any other run's work item. (`read-project` / `read-issue` skills
were explicitly rejected by the ISI-3588 study §4/§6.)

## How you reach the coord API

The operator injects these into your Run environment (never the operator's own
secrets — they join a minimal curated env, not `os.Environ`):

| Env var | Meaning |
| --- | --- |
| `KSQUAD_COORD_URL`   | In-cluster base URL of the coord task-I/O API (the four verbs below are its immediate children). An in-cluster Service, not a public surface (S2 AC7). |
| `KSQUAD_COORD_TOKEN` | Your run-scoped bearer token. Send it as `Authorization: Bearer $KSQUAD_COORD_TOKEN`. Bound to your run; it cannot touch any other run's work item. |
| `WORK_ITEM_ID`       | Your work item's id (also bound inside the token — the server reads it from the token, not from your request). |
| `RUN_ID`             | Your run's id (also bound inside the token). |

If `KSQUAD_COORD_TOKEN` is absent the coord API refuses every call — the seam is
**fail-safe**, never fail-open.

## The four verbs

All paths are relative to `$KSQUAD_COORD_URL`. Authenticate every call with
`Authorization: Bearer $KSQUAD_COORD_TOKEN`. The work item and your identity
(comment attribution) are taken from the token, never from request fields.

### `GET /get-task`

Re-read your work item. Use it **before acting** to pick up changes made since
boot. No request body.

`200 OK` →

```json
{
  "workItemId": "ISI-1234",
  "title": "…",
  "description": "…",
  "state": "in_progress",
  "blockedReason": "",
  "acceptanceCriteria": ["…", "…"],
  "goals": ["…"],
  "comments": [
    { "author": "devops engineer", "body": "…", "createdAt": "2026-09-03T12:00:00Z" }
  ],
  "fenceToken": 7,
  "holder": "run-abc",
  "runId": "run-abc"
}
```

`blockedReason`, `acceptanceCriteria`, `goals`, `holder`, `runId` are omitted
when empty.

### `POST /post-comment`

Append a comment to your work item, attributed to **you** (the token's
principal — a client-supplied author is ignored). Use it to leave durable
progress or ask a question.

Request:

```json
{ "body": "Shipped the migration; waiting on review." }
```

`201 Created` →

```json
{ "author": "devops engineer", "body": "…", "createdAt": "2026-09-03T12:00:00Z" }
```

An empty `body` is rejected `400 Bad Request` (`comment body required`).

### `POST /update-status`

Move your work item to a new status (report progress / completion). Invalid
transitions are rejected **server-side**.

Request:

```json
{ "status": "in_review" }
```

`204 No Content` on success. An empty `status` → `400`; an invalid transition →
an error (the server owns the lane machine — do not assume a transition is
legal). 

### `POST /checkout`

Claim / renew your hold on the work (maps to the coord claim **fence**). No
request body.

`200 OK` →

```json
{ "workItemId": "ISI-1234", "runId": "run-abc", "fenceToken": 8 }
```

A stale fence (another holder advanced it) is rejected — re-`get-task` and
reconcile rather than forcing.

## Errors

| Status | Meaning |
| --- | --- |
| `401 Unauthorized` | Missing / malformed / invalid run token. |
| `404 Not Found`    | Work item not found. |
| `400 Bad Request`  | Missing required field (`body`, `status`). |
| `405 Method Not Allowed` | Wrong verb (e.g. `POST /get-task`). |
| `409`-class refusal | Stale claim fence or invalid status transition. |

## Tracing (join the run-trace)

The client that executes these HTTP calls must join the same run-trace so
agent-observed latency lines up with the coord-side spans:

1. `telemetry.Extract` the `traceparent` the operator injects into your Run env
   as `TRACEPARENT` (and `TRACESTATE`), and open your client span
   **under** it.
2. Name the client span `taskio.<op>` (e.g. `taskio.get_task`) with scope
   `github.com/K8squad/K8squad/skills/task-io`.
3. Propagate the context on the wire — send the `traceparent` / `tracestate`
   headers on the request — so the coord-side `taskio.<op>` span nests under
   your client span in the one run-trace.

Trace-only: **no** MeterProvider. Per the bootstrap o11y spec §2 / §2.3 / §9-5
(ISI-3592) and the S3 story trace-join note (ksquad `f60c40e`).

## Rules

- Only ever act on **your** work item. Never attempt to widen scope.
- This skill's authority is the `permissions` envelope on its Skill CR
  (`issue:read`, `issue:write`, `task:status`) — set by the operator/admin who
  registers the skill and **never** widened by anything written in this body
  (trust boundary D8). A git-sourced body supplies behavior *inside* the
  envelope, never a new capability.

## Provenance

- Contract source: coord task-io API seam, S2 / ISI-3601 (K8squad `pkg/taskio`,
  merged to `main` in PR #237). The env-injection contract is `pkg/controller/
  rundrive/dispatch.go`; the verbs/shapes are `pkg/taskio/handler.go`.
- Story: `docs/bmad/stories/isi-3590-story-s3-predefined-task-io-skill.md`
  (ISI-3602 / S3, from the ISI-3588 bootstrap study).
