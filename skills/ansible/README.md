# `ansible` Skill

Configuration management with Ansible — inventory inspection, `--check`
dry-runs, and gated applying playbook runs.

- **Focus:** ops
- **Category:** ops-iac
- **Source:** inline (self-contained body in the CR)
- **Attach to roles:** ProxOps, DevOps _(ops-only — a write skill)_
- **Permissions (least-privilege):** `exec:ansible`, `net:egress:hosts`
- **Toolchains:** `ansible-core@2.17`
- **Sidecars:** none

## Gating & credentials

A mutation skill — attached only to operations roles (ISI-5754 §7
decision #2). A real (non-`--check`) playbook run requires explicit user
confirmation of the previewed diff (see the skill body).

The skill **never embeds a credential**: the SSH connection key material and
any vault password are projected per-Run by the platform (the credential-vault
go-live gate, WS-9 / ISI-5777). Until the board provisions them, the playbook
actions are inert.

> **Egress go-live note:** `net:egress:hosts` resolves against an
> `EgressPolicy` the operator defines for the managed inventory hosts; without
> it the Run is blocked fail-closed.

## Install

```sh
kubectl apply -f skills/ansible/skill.yaml
```

## Wire it

```yaml
# Role.spec.defaultSkills[] — e.g. ProxOps / DevOps
defaultSkills:
  - name: ansible
```
