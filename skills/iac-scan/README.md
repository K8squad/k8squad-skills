# `iac-scan` Skill

Infrastructure-as-code and Kubernetes misconfiguration scanning with checkov
and kube-bench — insecure Terraform/Helm/manifest defaults and CIS cluster
hardening gaps found before they ship.

- **Focus:** security
- **Category:** security
- **Source:** inline (self-contained body in the CR)
- **Attach to roles:** DevOps, Architect, Code Reviewer
- **Permissions (least-privilege):** `fs:read`, `exec:checkov`, `exec:kube-bench`
- **Toolchains:** `checkov@3` (provides `checkov` and `kube-bench`)

## Install

```sh
kubectl apply -f skills/iac-scan/skill.yaml
```

> Requires the `checkov` long-tail toolchain in the target namespace:
> `kubectl apply -k toolchains/ -n <team-namespace>`. The image ships both
> `checkov` and `kube-bench`.

## Wire it

Grant to every agent under a role (default) or to a single agent:

```yaml
# Role.spec.defaultSkills[] — granted to all agents of the role
defaultSkills:
  - name: iac-scan

# Agent.spec.skillRefs[] — granted to one agent (overrides role defaults)
skillRefs:
  - name: iac-scan
```

> **Note:** pairs with the Ops/IaC skills (ISI-5754 §3.1, WS-2) — scan the
> same Terraform/Helm/manifest definitions those skills author.
