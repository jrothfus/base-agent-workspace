# Agent Context for base-agent-workspace

This workspace is designed for AI-agent-driven development where each task is isolated to avoid agents conflicting with each other.

## Purpose

- Run one task per isolated working folder/branch.
- Keep repo state predictable for handoff and review.
- Support a clean loop: task request → implementation → human review → PR → end task.

## Source of Truth

- Repo URL and base branch are defined in `.agent-workspace/config.json`.

## Standard Agent Workflow

1. Start from this workspace root.
2. Attempt to acquire a lock for a worktree id
2. If you acquired a lock, use the matching worktree, otherwise pull/clone the selected repo into the working tree (with name matching the working tree id), and make a symblic link with short task description
3. Switch to the configured base branch and pull latest.
4. Create a new task branch.
5. Implement the bugfix/feature/ticket scope.
6. Prompt developer for review.
7. After approval, commit/push and open a PR.

## Skills Usage

### Required skills (when available)
- `start_task`: clone/switch/bootstrap task work.
- `end_task`: cleanup and close-out.

### Optional skills
- `.agent_skills/acli-jira`: Jira workflows via Atlassian CLI.

## Agent Guardrails

- Do not work directly on base branch.
- Do not reuse another task branch/folder for a new ticket.
- Keep changes scoped to the requested task.
- Ask for review before final PR actions.
- Prefer small, reviewable commits.

## Quick Start Checklist

- Read `.agent-workspace/config.json` first.
- Confirm repo folder exists (or clone it).
- Confirm current branch tracks configured base branch.
- Create a fresh task branch.
- Begin implementation.
