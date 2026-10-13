# `proxmox-api` Skill

Proxmox VE node / VM / container operations via `pvesh`, `qm`, and `pct` —
read the API and drive VM/CT lifecycle.

- **Focus:** ops
- **Category:** ops-iac
- **Source:** inline (self-contained body in the CR)
- **Attach to roles:** ProxOps _(ops-only — a write skill)_
- **Permissions (least-privilege):** `exec:pvesh`, `exec:qm`, `exec:pct`, `net:egress:proxmox`
- **Toolchains:** `proxmox-cli@8`
- **Sidecars:** none

## Gating & credentials

A mutation skill — attached only to the ProxOps role (ISI-5754 §7
decision #2). Read verbs (`pvesh get`, `qm/pct list|config|status`) are safe;
lifecycle verbs mutate real infrastructure, and `destroy` / `move-disk
--delete` / snapshot-delete / `set --delete` are destructive and require
explicit user confirmation (see the skill body).

The skill **never embeds the token**: the Proxmox API token is projected
per-Run by the platform as an environment variable (the credential-vault
go-live gate, WS-9 / ISI-5777). Until the board provisions it, the mutating
actions are inert.

> **Egress go-live note:** `net:egress:proxmox` resolves against an
> `EgressPolicy` the operator defines for the Proxmox host API endpoints;
> without it the Run is blocked fail-closed.

## Install

```sh
kubectl apply -f skills/proxmox-api/skill.yaml
```

## Wire it

```yaml
# Role.spec.defaultSkills[] — ProxOps
defaultSkills:
  - name: proxmox-api
```
