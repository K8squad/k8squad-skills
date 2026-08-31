# k8squad-skills

The canonical catalog of predefined **`Skill`** custom resources for
[K8squad](https://github.com/K8squad/K8squad). A `Skill` is a CRD-authorized
capability envelope (`ksquad.io/v1alpha1`, `api/v1alpha1/skill_types.go`): it is
registered by an operator/admin and grants a squad agent a tool or capability.
The envelope is authored here and is **never self-widened** by a fetched skill
body (trust boundary D8, arch §5.3.6).

This repo is the source of truth for the reusable Skills. The
[`examples/bmad-team/`](https://github.com/K8squad/K8squad/tree/main/examples/bmad-team)
squad references this catalog rather than re-inlining the definitions.

## Catalog

Each skill lives in its own directory under `skills/<name>/` with a `skill.yaml`
(the CR) and a `README.md` (purpose, roles, permissions, wiring).

### Defaults

| Skill | Focus | Purpose |
|-------|-------|---------|
| [`bmad`](skills/bmad) | method | The BMAD phased-workflow method (inline). |
| [`github`](skills/github) | dev | Remote git / PR / issue ops via the GitHub CLI (`gh`). |
| [`dynatrace`](skills/dynatrace) | debug | Dynatrace control-plane (dtctl) for observability — agent body git-sourced from upstream `dynatrace-oss/dtctl`. |
| [`dt-dql-essentials`](skills/dt-dql-essentials) | debug | DQL syntax / pitfalls / query optimization — git-sourced from upstream `Dynatrace/dynatrace-for-ai`. |
| [`graphical`](skills/graphical) | dev | Diagram / SVG asset rendering. |

### Dev / debug set (9 core + 1 optional — from ISI-3271)

| Skill | Focus | Purpose |
|-------|-------|---------|
| [`code-search`](skills/code-search) | dev | Semantic + structural (AST) code navigation. |
| [`kubectl-debug`](skills/kubectl-debug) | debug | Read-only cluster introspection + ephemeral debug. |
| [`go-build-test`](skills/go-build-test) | dev+debug | `go build/vet/test` (-run, -race) + dockerd sidecar. |
| [`git-workflow`](skills/git-workflow) | dev+debug | Local git incl. `git bisect`. |
| [`golangci-lint`](skills/golangci-lint) | dev | Run the repo's lint gate locally. |
| [`otel-observability-query`](skills/otel-observability-query) | debug | Read-only trace/log/span query (Dynatrace DQL). |
| [`container-build`](skills/container-build) | dev+debug | docker/buildkit build/run/inspect. |
| [`delve-pprof`](skills/delve-pprof) | debug | Live-process debug (dlv) + profiling (pprof). |
| [`psql-inspect`](skills/psql-inspect) | debug | Read-only psql into the coordination/run-source DB. |
| [`http-grpc-probe`](skills/http-grpc-probe) | debug _(optional)_ | curl/grpcurl probing of live endpoints. |

## The capability plane (how a Skill actually resolves)

With the Skills & tools implementation landed (ISI-3280 Epics A–C, ADRs
042–045), a Skill is not a standalone artifact — it resolves at admission and
Run assembly against live cluster objects. Everything below is **fail-closed**.

A skill grants tools through **two independent paths**, and most skills need
only one:

- **Toolchains** (`requires.toolchains`, §5.3.2) — a CLI pack staged as an
  init container, e.g. `gh@2.98`, `dtctl@1.0`, `node@22`. This is the path
  **every skill in this catalog uses**: `github` drives `gh`, `dynatrace`/
  `otel-observability-query` drive `dtctl`, `graphical` drives `node`. A CLI
  tool does not need an MCPServer.
- **`mcpToolRefs` → `MCPServer`** — for a network tool surface reachable
  **only over MCP** (a hosted service that speaks the protocol, not a CLI).
  No catalog skill currently needs this, but the platform supports it and the
  semantics are documented below so authors of MCP-backed skills know the
  rules.

### `mcpToolRefs` → `MCPServer` (ADR-042)

`spec.mcpToolRefs[]` entries are `{name, namespace?}` refs (empty namespace =
the Skill's own). Resolution:

- **Dangling ref** → the **Skill is rejected at admission** (validating
  webhook), and re-checked at Run assembly in case the admission cache is
  stale — same outcome.
- The MCPServer's tool surface must be **discovered**: the control-plane
  discovery controller runs the MCP handshake (`initialize` → `tools/list`)
  on create/spec-change and every `discovery.intervalMinutes` (default 10),
  recording `status.observedTools` and the `Ready` / `CredentialsValid` /
  `EgressAllowed` / `ToolsDiscovered` conditions. A Run referencing a server
  with an empty `observedTools` stays **Pending** — Runs never admit against
  an unknown tool surface (ADR-042 staleness).
- **Credentials**: `MCPServer.spec.credentialSecretRef` names a BYO Secret
  (default key `token`). It is projected into the Run pod **only as an env
  var** — `KSQUAD_MCP_<UPPER(NAME)>_TOKEN` (e.g. server `github-mcp` →
  `KSQUAD_MCP_GITHUB_MCP_TOKEN`). Secret material never lands in a file the
  runtime reads, in status, or in logs (ADR-045 D5). A missing Secret sets
  `CredentialsValid=False` and blocks the Run without deleting the server —
  rotation never requires re-apply.
- **stdio servers with an `image`** are staged as sidecar containers in Run
  pods of Runs whose skills reference them; streamable-http servers are wired
  into the runtime's native MCP config (ADR-044 step 6).

### `toolFilter` — skills only narrow, never widen (D8)

The **server** owns the tool envelope: `MCPServer.spec.toolFilter.allow`
(globs; empty = all observed tools) minus `.deny` (globs subtracted). At
v1alpha1 a Skill's `mcpToolRefs` entry carries **no filter of its own** — the
skill's act is *selecting* a server, which can only ever grant a subset of
what that server already allows. A fetched git body never sees envelope
authority at all.

Fail-closed corners (all reject the Run / the MCPServer):

- exact-string overlap between `allow` and `deny` → MCPServer admission
  rejected (CEL);
- glob overlap that empties the effective allow set → Run assembly fails
  closed instead of passing silently;
- `egressRef` unresolvable → `EgressAllowed=False` → Run blocked.

### `requires.toolchains` → the Toolchain catalog (ADR-043)

`name@version` refs resolve against the cluster default catalog (Toolchain
objects in the control-plane namespace), enabled with one Helm flag:

```sh
helm install k8squad ... --set tools.defaultCatalog.enabled=true
```

The curated set this catalog's skills pin against:

| Toolchain | Version | RBAC |
|-----------|---------|------|
| `kubectl@1.36` | 1.36 | read-only core+apps, namespace scope |
| `git@2.45` | 2.45 | none |
| `gh@2.98` | 2.98 | none |
| `go@1.26` | 1.26 | none |
| `node@22` | 22 | none |
| `dtctl@1.0` | 1.0 | none |
| `docker-cli@29` | 29 | none |
| `helm@3.21` | 3.21 | none |

Resolution rules (all enforced at **Run admission** via the same resolver Run
assembly uses):

- unknown `name` or `version` → Run rejected with an actionable message
  naming the demanding skill (e.g. "toolchain go@1.25 not found; catalog
  carries 1.26" — enable the default catalog, define the Toolchain, or align
  the version pin);
- the same toolchain name at two versions across one Run's skills → Run
  rejected (§5.3.4 — no silent latest-wins);
- team-namespace Toolchains may **narrow** catalog entries (subset versions,
  subset RBAC) but never widen; a team namespace cannot originate Kubernetes
  authority.

**BYO long-tail tools**: skills referencing tools outside the curated default
catalog (`ripgrep`, `ast-grep`, `delve`, `golangci-lint`, `grpcurl`,
`postgres-client`) are admitted only when your cluster defines the matching
team-namespace `Toolchain` objects (no `rbac` block — ADR-043 long-tail path).
This repo ships ready-to-apply manifests under [`toolchains/`](toolchains/) —
see [**Install long-tail Toolchains**](#install-long-tail-toolchains) below.

### SHA pinning (§5.3.6)

Every `git`-sourced skill pins `ref` to an **immutable commit SHA** — never a
floating branch. A Run resolves its skills to immutable revisions, so a
force-push to this repo cannot silently alter in-flight behavior; moving refs
are admitted only behind the explicit, audited `ksquad.io/trusted-dev`
posture. The self-referential `ref` fields in this catalog are pinned to real
merge commits and re-pinned to the new merge commit on each release.

Two skills source their agent-facing body from **upstream Dynatrace repos**
rather than this catalog — [`dynatrace`](skills/dynatrace) from
`dynatrace-oss/dtctl` (`skills/dtctl`) and
[`dt-dql-essentials`](skills/dt-dql-essentials) from
`Dynatrace/dynatrace-for-ai` (`skills/dt-dql-essentials`), both Apache-2.0.
They follow the same pinning discipline: an immutable upstream commit SHA,
re-pinned deliberately after reviewing the upstream diff. The fetched body is
untrusted input (D8) — it can never widen the `permissions` /
`mcpToolRefs` envelope authored here.

### What usage reporting you get for free (ISI-3288 / ISI-3352)

Skill authors instrument nothing. The platform emits:

- **OTel spans** (GenAI semconv v1.40): `skill.load`, and `gen_ai.tool.call`
  per tool call carrying `gen_ai.tool.name` and
  `gen_ai.tool.call.arguments` (hex sha256 of the arguments — hashed, never
  raw), plus `ksquad.run.id`, `ksquad.agent.name`, `ksquad.skill.name`,
  `ksquad.skill.source.sha`, `ksquad.mcp.server`, `ksquad.outcome`.
- **Prometheus metrics** on the operator `/metrics`: 
  `ksquad_skill_loads_total`, `ksquad_tool_calls_total`,
  `ksquad_mcp_call_duration_seconds` (histogram), and
  `ksquad_tool_usage_pipeline_up` (the pipeline liveness marker — its
  presence in an exposition proves the pipeline is wired and scrapeable).

The OTelConfig watcher can toggle the pipeline at runtime; the default
posture is emit.

## Install long-tail Toolchains

The skills in this catalog that use long-tail tools (`code-search`, `delve-pprof`,
`golangci-lint`, `http-grpc-probe`, `psql-inspect`) require cluster-local `Toolchain`
objects. This repo ships them under `toolchains/`. Two tiers:

| Tier | Tools | How to install |
|------|-------|----------------|
| **Cluster default catalog** (admin, once) | `kubectl`, `git`, `gh`, `go`, `node`, `dtctl`, `docker-cli`, `curl`, `helm`, … | `helm install k8squad ... --set tools.defaultCatalog.enabled=true` |
| **Long-tail BYO** (team namespace) | `ripgrep`, `ast-grep`, `delve`, `golangci-lint`, `grpcurl`, `postgres-client` | `kubectl apply -k toolchains/ -n <team-namespace>` |

Apply the long-tail set into your team namespace:

```sh
kubectl apply -k toolchains/ -n <team-namespace>
```

Or reference via a kustomize remote in your own overlay:

```yaml
# kustomization.yaml
bases:
- github.com/K8squad/k8squad-skills//toolchains
namespace: my-squad
```

Each manifest is a data-only `Toolchain` CR with no `rbac` block. The version
pins in `toolchains/` exactly match what the skills declare in
`requires.toolchains` — a mismatch fails Run admission fail-closed.

## Install

Apply one skill:

```sh
kubectl apply -f skills/kubectl-debug/skill.yaml
```

Apply the whole catalog with Kustomize (set the target namespace in
`kustomization.yaml`, default `bmad-squad`):

```sh
kubectl apply -k .
```

> Skills require the K8squad CRDs to be installed first (Helm chart, step 1 of
> the quickstart). See the [Getting Started guide](https://github.com/K8squad/K8squad).

## Wire skills to agents

Skills attach at two levels — grant broad-value skills as **role defaults** and
specialist ones **per agent**:

```yaml
apiVersion: ksquad.io/v1alpha1
kind: Role
metadata: { name: coder, namespace: bmad-squad }
spec:
  defaultSkills:          # granted to every agent assuming this role
    - name: code-search
    - name: go-build-test
    - name: git-workflow
---
apiVersion: ksquad.io/v1alpha1
kind: Agent
metadata: { name: coder-01, namespace: bmad-squad }
spec:
  skillRefs:              # granted to this agent (overrides the role defaults)
    - name: delve-pprof
```

## Role → Skill attachment matrix

Recommended defaults (from ISI-3271; least-privilege — the PM/CEO/UX/etc. roles
lean on the `bmad` / `github` / `graphical` defaults only):

| Role | Recommended skills |
|------|--------------------|
| **Coder** | code-search, go-build-test, git-workflow, golangci-lint, delve-pprof, psql-inspect, kubectl-debug, github |
| **Code Reviewer** | code-search, golangci-lint, go-build-test, git-workflow, github |
| **Test Architect** | go-build-test, code-search, git-workflow, kubectl-debug, psql-inspect, otel-observability-query |
| **DevOps** | kubectl-debug, container-build, git-workflow, psql-inspect, otel-observability-query, github |
| **Observability** | otel-observability-query, kubectl-debug, delve-pprof, dynatrace, dt-dql-essentials |
| **Architect** | code-search, graphical |
| **Graphical Designer** | graphical |
| **Challenger** | code-search |
| **All roles** | bmad |

## Trust & least-privilege notes

- **Every `git`-sourced `ref` is pinned to an immutable commit SHA** — floating
  branches are rejected outside the explicit trusted-dev posture (arch
  §5.3.6). Catalog releases re-pin the self-referential SHAs to each merge
  commit.
- **`permissions[]` are least-privilege and read-first.** `kubectl-debug`,
  `otel-observability-query`, and `psql-inspect` carry no write/apply/delete
  verbs. A git-sourced body cannot widen this envelope (D8).
- **`dockerd`-sidecar skills** (`go-build-test`, `container-build`) only resolve
  where `AgentRuntime.capabilities` grants the sidecar (arch §5.3.3/§5.3.4).
- **Toolchain refs split in two tiers**: the curated catalog set
  (`kubectl@1.36`, `git@2.45`, `gh@2.98`, `go@1.26`, `node@22`, `dtctl@1.0`,
  `docker-cli@29`, `curl@8`, `helm@3.21`, …) resolves with
  `tools.defaultCatalog.enabled=true`; everything
  else is BYO via team-namespace Toolchains. Mixing versions of one toolchain
  across a Run's skills fails closed at admission (§5.3.4).

## License

Apache License 2.0 — see [LICENSE](LICENSE).
