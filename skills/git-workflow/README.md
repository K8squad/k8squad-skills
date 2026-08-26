# `git-workflow` Skill

Local git incl. `git bisect` — the highest-leverage regression hunter.

- **Focus:** dev+debug
- **Category:** dev-debug
- **Source:** inline (self-contained body in the CR)
- **Attach to roles:** Coder, Test Architect, Code Reviewer, DevOps
- **Permissions (least-privilege):** `fs:read`, `fs:write:workspace`, `exec:git`
- **Toolchains:** `git@2.47`

## Install

```sh
kubectl apply -f skills/git-workflow/skill.yaml
```

## Wire it

Grant to every agent under a role (default) or to a single agent:

```yaml
# Role.spec.defaultSkills[] — granted to all agents of the role
defaultSkills:
  - name: git-workflow

# Agent.spec.skillRefs[] — granted to one agent (overrides role defaults)
skillRefs:
  - name: git-workflow
```
