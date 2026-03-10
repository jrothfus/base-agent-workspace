# Agent Context for base-agent-workspace

This workspace is designed for AI-agent-driven development where each task is isolated to avoid agents conflicting with each other.

## Purpose

- Run one task per isolated working folder/branch.
- Keep repo state predictable for handoff and review.
- Support a clean loop: task request → implementation → human review → PR → end task.

## Source of Truth

- Repo URL and base branch are defined in `.agent-workspace/config.json`.

## Standard Agent Workflow

Task setup and teardown are handled by the human via bash scripts — the agent does NOT run start or end task scripts.

1. The human starts a task with `bash start-task` — the agent will already be inside the prepared worktree when invoked.
2. Read `.agent-workspace/config.json` to understand the repo and base branch.
3. Create a new task branch from the current base branch.
4. Implement the bugfix/feature/ticket scope.
5. Prompt developer for review.
6. After approval, commit/push and open a PR.
7. The human ends the task with `bash end-task` — do not run cleanup scripts.

## Skills Usage

### Optional skills
- `.agent_skills/acli-jira`: Jira workflows via Atlassian CLI.

## Agent Guardrails

- Do not work directly on base branch.
- Do not reuse another task branch/folder for a new ticket.
- Keep changes scoped to the requested task.
- Ask for review before final PR actions.
- Prefer small, reviewable commits.
- Do NOT run `.scripts/start_task.py` or `.scripts/end_task.py` — these are for human use only.

## Quick Start Checklist

- Read `.agent-workspace/config.json` first.
- Confirm current branch tracks configured base branch.
- Create a fresh task branch.
- Begin implementation.
