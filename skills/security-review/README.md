# `security-review` Skill

A guided threat-model and security review for a change or feature —
text-only attacker-perspective reasoning that decides what the scanner
skills should then confirm.

- **Focus:** security
- **Category:** security
- **Source:** inline (self-contained body in the CR)
- **Attach to roles:** Code Reviewer, Architect, Challenger, DevOps
- **Permissions (least-privilege):** `fs:read`
- **Toolchains:** none (text-only reasoning)

## Install

```sh
kubectl apply -f skills/security-review/skill.yaml
```

## Wire it

Grant to every agent under a role (default) or to a single agent:

```yaml
# Role.spec.defaultSkills[] — granted to all agents of the role
defaultSkills:
  - name: security-review

# Agent.spec.skillRefs[] — granted to one agent (overrides role defaults)
skillRefs:
  - name: security-review
```

> **Note:** ported from the local `security-review` Claude Code skill
> (ISI-5754 §3.6). No scanner or toolchain — it pairs with sast-scan,
> secret-scan, vuln-scan, and iac-scan, which verify the findings it surfaces.
