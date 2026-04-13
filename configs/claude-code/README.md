# Claude Code Configuration

Recommended settings for zero-friction Flux usage. The multi-agent pipeline runs autonomously — these permissions prevent it from pausing for approval.

Place in your project's `.claude/settings.json` or `~/.claude/settings.json`.

```json
{
  "permissions": {
    "allow": [
      "Bash(python shared/scripts/*)",
      "Bash(mkdir -p prompts/*)",
      "Agent"
    ]
  }
}
```

This allows:
- **Convergence engine** to run self-eval, token-count, and report-gen without prompts
- **Prompt folder creation** without approval
- **Agent spawning** for background convergence and reviewer agents

Without these permissions, the pipeline will pause at each tool call asking for approval — defeating the purpose of autonomous convergence.
