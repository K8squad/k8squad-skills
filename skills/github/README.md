# `github` Skill

Remote git / PR / issue operations via the GitHub MCP.

- **Focus:** dev
- **Category:** default
- **Source:** git — `github.com/K8squad/k8squad-skills` path `skills/github`, pinned to a commit SHA
- **Attach to roles:** Coder, Code Reviewer, DevOps
- **Permissions (least-privilege):** `scm:read`, `scm:write`, `pr:write`, `issue:write`
- **MCP tools:** `github-mcp`
- **Toolchains:** `gh@2.62`

## Install

```sh
kubectl apply -f skills/github/skill.yaml
```

## Wire it

Grant to every agent under a role (default) or to a single agent:

```yaml
# Role.spec.defaultSkills[] — granted to all agents of the role
defaultSkills:
  - name: github

# Agent.spec.skillRefs[] — granted to one agent (overrides role defaults)
skillRefs:
  - name: github
```

> **Note:** git-sourced. The `ref` must be pinned to an immutable **commit SHA**
> (never a floating branch, arch §5.3.6). The value shipped here is a placeholder —
> pin it to a merged commit of this repo before production use.
