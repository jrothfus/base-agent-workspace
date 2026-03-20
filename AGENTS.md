# Agent Context for base-agent-workspace

This workspace provides **isolated task worktrees** with a full **superpowers skills library** for disciplined AI-driven development.

## Source of Truth

- Repo URL and base branch: `.agent-workspace/config.json`
- Skills: `.claude/skills/` (injected at task start from `.agent_skills/` and `.superpowers/skills/`)
- Agents: `.claude/agents/` (injected from `.superpowers/agents/`)

## Standard Agent Workflow

Task setup and teardown are handled by the human — the agent does NOT run start or end task scripts.

1. The human starts a task with `python3 start-task.py` — you are already inside the prepared worktree.
2. Read `.agent-workspace/config.json` to understand the repo and base branch.
3. Create a new task branch from the current base branch.
4. **Check for applicable skills before acting** — brainstorming for features, systematic-debugging for bugs.
5. Follow skill workflows: brainstorm → write plan → execute with TDD → review → finish.
6. Prompt developer for review.
7. After approval, commit/push and open a PR.
8. The human ends the task with `python3 end-task.py`.

## Skills

### Superpowers Skills (auto-injected)
brainstorming, writing-plans, subagent-driven-development, executing-plans, test-driven-development, systematic-debugging, verification-before-completion, requesting-code-review, receiving-code-review, finishing-a-development-branch, dispatching-parallel-agents, using-git-worktrees, using-superpowers, writing-skills

### Workspace Skills (in `.agent_skills/`)
- **acli-jira**: Jira workflows via Atlassian CLI
- **memory**: Persistent memory across sessions

## Worktree Overrides

- **using-git-worktrees**: SKIP — your worktree is already set up.
- **finishing-a-development-branch**: ADAPTED — push and PR, but do NOT clean up the worktree.

## Agent Guardrails

- Do not work directly on base branch.
- Do not reuse another task branch/folder for a new ticket.
- Do not run `.scripts/start_task.py` or `.scripts/end_task.py`.
- Keep changes scoped to the requested task.
- Ask for review before final PR actions.
- Prefer small, reviewable commits.
- If a skill applies, you must use it.
