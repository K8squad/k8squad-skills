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

### 4 defaults

| Skill | Focus | Purpose |
|-------|-------|---------|
| [`bmad`](skills/bmad) | method | The BMAD phased-workflow method (inline). |
| [`github`](skills/github) | dev | Remote git / PR / issue ops via the GitHub MCP. |
| [`dynatrace`](skills/dynatrace) | debug | Dynatrace control-plane (dtctl) for observability. |
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
| **Observability** | otel-observability-query, kubectl-debug, delve-pprof, dynatrace |
| **Architect** | code-search, graphical |
| **Graphical Designer** | graphical |
| **Challenger** | code-search |
| **All roles** | bmad |

## Trust & least-privilege notes

- **Pin every `git`-sourced `ref` to an immutable commit SHA** — floating
  branches are rejected outside an explicit dev posture (arch §5.3.6). The SHAs
  shipped here are placeholders; pin them to a merged commit before production.
- **`permissions[]` are least-privilege and read-first.** `kubectl-debug`,
  `otel-observability-query`, and `psql-inspect` carry no write/apply/delete
  verbs. A git-sourced body cannot widen this envelope (D8).
- **`dockerd`-sidecar skills** (`go-build-test`, `container-build`) only resolve
  where `AgentRuntime.capabilities` grants the sidecar (arch §5.3.3/§5.3.4).
- **Toolchain versions are standardized** (`go@1.25`, `kubectl@1.31`) — mixing
  versions across a Run's skills fails closed at pod assembly (arch §5.3.4).

## License

Apache License 2.0 — see [LICENSE](LICENSE).
