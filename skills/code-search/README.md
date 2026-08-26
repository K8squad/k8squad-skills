# `code-search` Skill

Fast semantic + structural (AST) code navigation (ripgrep + ast-grep).

- **Focus:** dev
- **Category:** dev-debug
- **Source:** git — `github.com/K8squad/k8squad-skills` path `skills/code-search`, pinned to a commit SHA
- **Attach to roles:** Coder, Code Reviewer, Architect, Test Architect, Challenger
- **Permissions (least-privilege):** `fs:read`
- **Toolchains:** `ripgrep@14`, `ast-grep@0.38`

## Install

```sh
kubectl apply -f skills/code-search/skill.yaml
```

## Wire it

Grant to every agent under a role (default) or to a single agent:

```yaml
# Role.spec.defaultSkills[] — granted to all agents of the role
defaultSkills:
  - name: code-search

# Agent.spec.skillRefs[] — granted to one agent (overrides role defaults)
skillRefs:
  - name: code-search
```

> **Note:** git-sourced. The `ref` must be pinned to an immutable **commit SHA**
> (never a floating branch, arch §5.3.6). The value shipped here is a placeholder —
> pin it to a merged commit of this repo before production use.
