# `vuln-scan` Skill

Container-image and filesystem CVE scanning with trivy and grype — vulnerable
OS packages and language dependencies found before release.

- **Focus:** security
- **Category:** security
- **Source:** inline (self-contained body in the CR)
- **Attach to roles:** DevOps, Code Reviewer, Architect
- **Permissions (least-privilege):** `fs:read`, `exec:trivy`, `exec:grype`
- **Toolchains:** `trivy@0.58`, `grype@0.87`

## Install

```sh
kubectl apply -f skills/vuln-scan/skill.yaml
```

> Requires the `trivy` and `grype` long-tail toolchains in the target
> namespace: `kubectl apply -k toolchains/ -n <team-namespace>`

## Wire it

Grant to every agent under a role (default) or to a single agent:

```yaml
# Role.spec.defaultSkills[] — granted to all agents of the role
defaultSkills:
  - name: vuln-scan

# Agent.spec.skillRefs[] — granted to one agent (overrides role defaults)
skillRefs:
  - name: vuln-scan
```
