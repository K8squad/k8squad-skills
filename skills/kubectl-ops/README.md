# `kubectl-ops` Skill

The write superset of `kubectl-debug` — apply / patch / scale / rollout /
delete against live cluster state.

- **Focus:** ops
- **Category:** ops-iac
- **Source:** inline (self-contained body in the CR)
- **Attach to roles:** ProxOps, DevOps _(ops-only — a write skill)_
- **Permissions (least-privilege):** `k8s:get`, `k8s:list`, `k8s:watch`, `k8s:apply`, `k8s:patch`, `k8s:scale`, `k8s:delete`
- **Toolchains:** `kubectl@1.36`
- **Sidecars:** none

## Gating

This is a mutation skill. Per the ratified catalog policy (ISI-5754 §7
decision #2) it is attached only to operations roles and never self-widens its
envelope (trust boundary D8). Destructive verbs (`delete`, `scale 0`,
`rollout undo`) require explicit user confirmation — see the skill body.

> **RBAC go-live note:** the curated `kubectl@1.36` toolchain ships with
> read-only RBAC. Granting the write verbs above requires the operator to
> provision a write-capable RBAC binding for the ops role's Run service
> account in the target namespace (cluster-admin action, out of band). Until
> then the write verbs are refused at runtime — fail-closed.

## Install

```sh
kubectl apply -f skills/kubectl-ops/skill.yaml
```

## Wire it

Grant to an ops role (default) or a single ops agent:

```yaml
# Role.spec.defaultSkills[] — e.g. ProxOps / DevOps
defaultSkills:
  - name: kubectl-ops

# Agent.spec.skillRefs[]
skillRefs:
  - name: kubectl-ops
```
