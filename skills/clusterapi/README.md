# `clusterapi` Skill

Cluster API (CAPI / CAPMOX) lifecycle via `clusterctl` plus `kubectl` on CAPI
custom resources — init, generate, describe, move, upgrade.

- **Focus:** ops
- **Category:** ops-iac
- **Source:** inline (self-contained body in the CR)
- **Attach to roles:** ProxOps, DevOps _(ops-only — a write skill)_
- **Permissions (least-privilege):** `exec:clusterctl`, `k8s:get`, `k8s:list`, `k8s:apply`, `k8s:patch`, `k8s:delete`
- **Toolchains:** `clusterctl@1.9`, `kubectl@1.36`
- **Sidecars:** none

## Gating

A management-cluster mutation skill — attached only to operations roles
(ISI-5754 §7 decision #2). `clusterctl move`, `upgrade apply`, and deleting a
Cluster / control-plane / Machine CR are destructive and require explicit user
confirmation (see the skill body). Provider versions are pinned; bumping or
adding a provider is a separate, reviewed change.

> **RBAC go-live note:** CAPI CR verbs resolve against the ops role's Run
> service-account RBAC in the management-cluster namespace; the operator
> provisions that binding out of band. `clusterctl` targets the management
> cluster context, never a workload cluster's own API.

## Install

```sh
kubectl apply -f skills/clusterapi/skill.yaml
```

## Wire it

```yaml
# Role.spec.defaultSkills[] — e.g. ProxOps / DevOps
defaultSkills:
  - name: clusterapi
```
