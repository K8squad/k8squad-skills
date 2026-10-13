# `terraform` Skill

Infrastructure as code with Terraform — init / validate / plan, and gated
apply / destroy.

- **Focus:** ops
- **Category:** ops-iac
- **Source:** inline (self-contained body in the CR)
- **Attach to roles:** ProxOps, DevOps _(ops-only — a write skill)_
- **Permissions (least-privilege):** `exec:terraform`, `net:egress:cloud`
- **Toolchains:** `terraform@1.9`
- **Sidecars:** none

## Gating & credentials

A mutation skill — attached only to operations roles (ISI-5754 §7
decision #2). `apply` and `destroy` require explicit user confirmation of a
reviewed plan (see the skill body).

The skill **never embeds a credential**: provider credentials and the
remote-state backend token are projected per-Run by the platform as
environment variables (the credential-vault go-live gate, WS-9 / ISI-5777).
Until the board provisions them, apply/destroy are inert — the skill admits
and plans, but cannot mutate.

> **Egress go-live note:** `net:egress:cloud` resolves against an `EgressPolicy`
> the operator defines for the provider API endpoints; without it the Run is
> blocked fail-closed.

## Install

```sh
kubectl apply -f skills/terraform/skill.yaml
```

## Wire it

```yaml
# Role.spec.defaultSkills[] — e.g. ProxOps / DevOps
defaultSkills:
  - name: terraform
```
