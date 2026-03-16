# base-agent-workspace

Multi-agent task isolation workspace with [Superpowers](https://github.com/obra/superpowers) integration.

## What This Does

Each AI agent gets an **isolated worktree** (cloned from a cached base repo for speed) and a full **Superpowers skills library** that enforces disciplined development: brainstorming → planning → TDD → code review → PR.

Multiple agents can work on the same repo simultaneously without conflicts.

## Read GETTING_STARTED.md

The below is information about how the repo works. Read `GETTING_STARTED.md` to start developing.

## The Workflow

1. Run `bash start-task "fix login bug" -- "fix the broken OAuth redirect"`.
2. Agent is placed in an isolated worktree with all skills injected.
3. Agent follows the Superpowers workflow: brainstorm the approach → write an implementation plan → execute with TDD → verify → create PR.
4. Developer reviews. Agent commits and pushes.
5. Run `bash end-task` to clean up.

## What Gets Injected Into Each Worktree

When `start-task` prepares a worktree, it symlinks:

| Target | Source | Purpose |
|--------|--------|---------|
| `.claude/skills/<name>` | `.agent_skills/<name>` | Your custom skills (acli-jira, memory, etc.) |
| `.claude/skills/<name>` | `.superpowers/skills/<name>` | Superpowers skills (TDD, debugging, planning, etc.) |
| `.claude/agents/<name>` | `.superpowers/agents/<name>` | Superpowers agents (code-reviewer) |
| `.claude/commands/<name>` | `.superpowers/commands/<name>` | Superpowers commands |

The same skills are also injected into `.codex/skills/` and `.openclaw/skills/`.

## Skills

### Superpowers Skills (14 skills)

**Workflow:** brainstorming, writing-plans, subagent-driven-development, executing-plans, dispatching-parallel-agents

**Quality:** test-driven-development, systematic-debugging, verification-before-completion

**Collaboration:** requesting-code-review, receiving-code-review, finishing-a-development-branch, using-git-worktrees

**Meta:** using-superpowers, writing-skills

### Custom Skills (in `.agent_skills/`)

- `acli-jira`: Jira workflows via Atlassian CLI
- `memory`: Persistent memory across sessions

Add your own skills by creating a folder in `.agent_skills/` with a `SKILL.md` file.

### Agent Skills From Target Repo

If the repo you're working on has its own agent skills (specified by `repo` inside `.agent-workspace/config.json`), those are available too.

## Updating Superpowers

Superpowers is a git submodule. To update:

```bash
git submodule update --remote .superpowers
```

## Architecture

See `HOW_IT_WORKS.md` for the task isolation system (locks, worktrees, startup commands).
