# `helm-ops` Skill

Helm release lifecycle — list / status / diff, and gated install / upgrade /
rollback / uninstall.

- **Focus:** ops
- **Category:** ops-iac
- **Source:** inline (self-contained body in the CR)
- **Attach to roles:** ProxOps, DevOps _(ops-only — a write skill)_
- **Permissions (least-privilege):** `exec:helm`, `k8s:get`, `k8s:list`, `k8s:apply`, `k8s:patch`
- **Toolchains:** `helm@3.21`, `kubectl@1.36`
- **Sidecars:** none

## Gating

A mutation skill — attached only to operations roles (ISI-5754 §7
decision #2). `helm uninstall` and `helm rollback` change or remove live
release state and require explicit user confirmation (see the skill body).
Tag-only rolls use `helm upgrade --reuse-values` so other operator-set values
are preserved.

> **RBAC go-live note:** Helm renders and applies chart resources through the
> ops role's Run service account; the operator provisions the write-capable
> RBAC binding in the target namespace out of band. Until then `install` /
> `upgrade` are refused at runtime — fail-closed.

## Install

```sh
kubectl apply -f skills/helm-ops/skill.yaml
```

## Wire it

```yaml
# Role.spec.defaultSkills[] — e.g. ProxOps / DevOps
defaultSkills:
  - name: helm-ops
```
