# Adding a toolchain

A **toolchain** is a versioned, digest-pinned pack of command-line tools that
K8squad stages onto a Run's `PATH` (`kubectl`, `git`, `helm`, `go`, …), plus the
declarative Kubernetes RBAC envelope that pack needs. Skills request toolchains
by `name@version`; the operator resolves each request against the cluster
catalog **fail-closed** — an unresolved or ambiguous request rejects the Run at
admission, never at runtime.

This guide walks a contributor through adding one. It assumes you have read
[Contributing a Skill](../CONTRIBUTING.md); a toolchain is what makes a skill's
`requires.toolchains` entry resolve.

> **Authoritative schema:** the `Toolchain` CRD lives in the main repo at
> [`config/crd/bases/ksquad.io_toolchains.yaml`](https://github.com/K8squad/K8squad/blob/main/config/crd/bases/ksquad.io_toolchains.yaml)
> (`apiVersion: ksquad.io/v1alpha1`). This page tracks that schema; when the two
> disagree, the CRD wins.

---

## Step 1 — Pick the tier

There are two places a toolchain can live, and they carry different trust.

| | **Cluster default catalog** | **Team BYO** |
|---|---|---|
| **Namespace** | control-plane namespace (`ksquad-system`) | your team namespace |
| **Who authors it** | platform admins, curated | any team, self-service |
| **Where the PR goes** | main repo, `config/helm/values.yaml` → `tools.defaultCatalog.entries` | this repo, `toolchains/` directory |
| **Can originate RBAC?** | **yes** — the authority | **no** — may only *narrow* an existing catalog entry |
| **Can grant cluster scope?** | yes, behind `tools.rbac.clusterScopeEnabled` | never |

**Rule of thumb:** if the tool is useful to every squad on the cluster and needs
Kubernetes API access, propose it for the **cluster catalog**. If it is specific
to your team, or you just need to pin a different version of an existing tool,
use **team BYO**.

The trust boundary is enforced at admission (D8 / ADR-043). A team-namespace
`Toolchain` may only **override an existing cluster-catalog entry of the same
name**, and the override may only narrow it — subset of versions with identical
images, subset of RBAC rules, `namespace` scope only. You can never *originate*
authority from a team namespace, add a version the catalog does not have, swap
an image, or widen a rule. The webhook rejects all of these with an actionable
message, e.g.:

```
team-namespace Toolchains may only override an existing cluster-catalog entry;
define ksquad-system/<name> first (the catalog is the platform-curated authority)
```

```
overrides may only narrow — subset versions with identical images,
subset RBAC rules, namespace scope
```

---

## Step 2 — Write the `Toolchain` manifest

A `Toolchain` is data-only and fully validated. Minimal shape — a PATH-staged
tool with no Kubernetes grants (this is the common case: `git`, `gh`, `go`,
`node`, `jq`, `yq`, `curl`, `make`, `python`, `uv`, `docker-cli`, `dtctl`, …):

```yaml
apiVersion: ksquad.io/v1alpha1
kind: Toolchain
metadata:
  name: kustomize                       # this is the "name" half of name@version
  namespace: bmad-squad                 # your team namespace for BYO
spec:
  versions:
    - version: "5.4"                    # the "version" half of name@version
      image: ghcr.io/acme/toolchains/kustomize@sha256:<digest>
      provides: [kustomize]             # binaries the pack puts on PATH (hint)
```

Field rules that admission enforces:

- **`spec.versions` — at least one, required.** An abstract toolchain with zero
  versions resolves nothing and fails Run admission. Each entry needs a
  non-empty `version` and a non-empty `image`; `version` strings must be unique
  within the toolchain (CEL pairwise + admission).
- **`image` — use a digest pin.** `…/kustomize@sha256:<digest>`, not a moving
  tag. A Run records the *resolved* reference in its status, so a digest pin
  guarantees a moving tag can never silently alter an in-flight Run — the same
  reproducibility discipline as a git-sourced skill's commit `ref`.
- **`provides`** is an optional documentation/staging hint listing the binaries
  the pack puts on `PATH` (e.g. `[node, npm]`). Max 64 entries.

### The optional RBAC envelope (cluster catalog only)

Most toolchains declare **no** `rbac` — they are staged onto `PATH` with no
Kubernetes API access. Add an `rbac` block only when the tool genuinely calls
the Kubernetes API (like `kubectl`). The operator — never the user — renders and
binds these rules into a per-Run `Role` bound to the managed agent
ServiceAccount, garbage-collected with the Run:

```yaml
spec:
  versions:
    - version: "1.36"
      image: ghcr.io/k8squad/toolchains/kubectl@sha256:<digest>
      provides: [kubectl]
  rbac:
    scope: namespace                    # "namespace" (default) or "cluster"
    rules:                              # standard rbacv1 PolicyRules
      - apiGroups: [""]
        resources: [pods, services, configmaps, events]
        verbs: [get, list, watch]
      - apiGroups: [apps]
        resources: [deployments, replicasets, statefulsets]
        verbs: [get, list, watch]
```

RBAC constraints:

- **Least privilege, no wildcards.** `"*"` in `apiGroups`, `resources`, or
  `verbs` is rejected at admission. Enumerate exactly what the tool needs.
- **Every rule must declare at least one verb.**
- **`scope: cluster`** renders a per-Run `ClusterRole`. It is admitted **only**
  on a cluster-catalog Toolchain **and** only when the platform opt-in
  `tools.rbac.clusterScopeEnabled=true` is set. It is rejected everywhere else,
  fail-closed. Team overrides may only carry `namespace` scope.
- **The union is additive.** When a Run's skills pull in several toolchains, the
  operator unions their RBAC into one Role; duplicate rules dedupe, nothing is
  intersected away.

---

## Step 3 — Pin `name@version` so skills resolve

A skill requests a toolchain in its `requires.toolchains` list:

```yaml
# in skills/<name>/skill.yaml
spec:
  requires:
    toolchains: [kubectl@1.36, kustomize@5.4]
```

The `name@version` string must match a `Toolchain` object exactly:

- `name` = the `Toolchain`'s `metadata.name`.
- `version` = one of its `spec.versions[].version`.

If either half does not resolve, or two skills in the same Run request two
different versions of the same toolchain, the **Run is rejected at admission**
with an actionable message. This is deliberate: a missing tool surfaces before
the squad starts, never as a mysterious `command not found` mid-Run.

---

## Step 4 — Test it end to end

1. **Apply the manifest** to a test namespace:

   ```bash
   kubectl apply -f toolchains/kustomize.yaml -n bmad-squad
   kubectl get toolchains -n bmad-squad          # shortName: tc
   ```

2. **Point a skill at it** — set `requires.toolchains: [kustomize@5.4]` on a
   skill, and make sure a squad uses that skill.

3. **Run the squad and confirm admission + staging.** A successful Run means the
   toolchain resolved and its image was staged onto `PATH`; the Run's status
   records the *resolved* image reference. Check that the tool is on `PATH`
   inside the Run and, if you declared `rbac`, that the intended API calls
   succeed and nothing broader does.

4. **Test the failure path too** — request `kustomize@9.9` (a version that does
   not exist) and confirm the Run is rejected at admission with a clear message.
   Fail-closed behavior is the point.

---

## Step 5 — PR checklist

Before opening your PR:

- [ ] Manifest validates against the CRD:
      `kubectl apply --dry-run=server -f toolchains/<name>.yaml`
- [ ] Every `image` is a **digest pin** (`@sha256:…`), not a moving tag.
- [ ] For any git-sourced reference, the ref is a **40-character commit SHA**
      (SHA pinning), never a branch or tag.
- [ ] No wildcard RBAC; each rule is least-privilege and lists at least one verb.
- [ ] For BYO: the manifest only *narrows* an existing cluster-catalog entry of
      the same name — subset versions with identical images, subset RBAC,
      `namespace` scope. No new versions, no image swaps, no widening.
- [ ] `requires.toolchains` in any companion skill exactly matches the
      `name@version` you defined.
- [ ] The PR description explains **why** the tool is needed and, for any RBAC,
      why each rule is necessary.

Two required CI checks run on GitHub-hosted runners with a **read-only token and
no secrets** — the same gates skills go through:

1. **CRD schema validation** — `kubectl apply --dry-run=server` against a real
   apiserver, enforcing the CRD's CEL rules.
2. **Static security scan** — flags over-broad grants and unpinned refs; HIGH
   findings block the PR, MEDIUM findings need a maintainer's
   `skill-security-reviewed` label.

Maintainers may edit or reject any submission. When in doubt, open an issue
first.

---

## The curated default catalog (for reference)

When `tools.defaultCatalog.enabled=true`, the chart ships these ready to use —
prefer them before adding your own:

| Toolchain | Version | RBAC |
|---|---|---|
| `kubectl` | `1.36` | read-only core + apps |
| `git` | `2.45` | none (PATH only) |
| `gh` | `2.98` | none |
| `go` | `1.26` | none |
| `node` | `22` | none (`node`, `npm`) |
| `dtctl` | `1.0` | none |
| `helm` | `3.21` | none |
| `python` | `3.12` | none (`python`, `python3`, `pip`) |
| `docker-cli` | `29` | none (client only; daemon is the `dockerd` sidecar) |
| `uv` | `0.5` | none (`uv`, `uvx`) |
| `jq` | `1.7` | none |
| `yq` | `4` | none |
| `curl` | `8` | none |
| `make` | `4` | none |

Extending this cluster catalog is an admin action — a PR to
`config/helm/values.yaml` (`tools.defaultCatalog.entries`) in the
[main repo](https://github.com/K8squad/K8squad). Adding a `cluster`-scope entry
additionally requires `tools.rbac.clusterScopeEnabled=true`.
