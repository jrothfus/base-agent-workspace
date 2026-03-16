# Agent Workspace with Superpowers

You are working inside an **isolated task worktree** managed by this workspace. Your worktree was created by the human running `start-task` and will be cleaned up by `end-task`. You do NOT manage the worktree lifecycle.

You have **superpowers** — a full skills library covering brainstorming, planning, TDD, debugging, code review, and more. These skills are loaded into your `.claude/skills/` directory and you MUST check for applicable skills before every action.

## Skill-First Protocol

**Before ANY response or action, check if a skill applies.** Even a 1% chance means you must invoke it.

Use the `Skill` tool to load skills. Available skills include:

### Workflow Skills
- **brainstorming** — Socratic design refinement before writing code
- **writing-plans** — Break specs into bite-sized implementation tasks (2-5 min each)
- **subagent-driven-development** — Execute plans via fresh subagent per task with two-stage review
- **executing-plans** — Batch execution with human checkpoints (alternative to subagent-driven)
- **dispatching-parallel-agents** — Concurrent subagent workflows

### Quality Skills
- **test-driven-development** — RED-GREEN-REFACTOR cycle (mandatory during implementation)
- **systematic-debugging** — Root cause analysis before attempting fixes
- **verification-before-completion** — Evidence before claims, always
- **requesting-code-review** — Pre-review checklist
- **receiving-code-review** — Responding to feedback

### Completion Skills
- **finishing-a-development-branch** — Push branch and create PR when done (see override below)

### Meta Skills
- **using-superpowers** — Full skill protocol reference
- **writing-skills** — Guide for creating new skills

### Workspace Skills (in `.agent_skills/`)
- **acli-jira** — Jira workflows via Atlassian CLI
- **memory** — Persistent memory across sessions

## Worktree Lifecycle Override

**IMPORTANT:** This workspace already manages worktree creation and cleanup. You MUST follow these overrides:

### `using-git-worktrees` — SKIP
Your worktree is already set up. Do NOT create additional worktrees or git worktrees. You are already in the correct isolated directory.

### `finishing-a-development-branch` — ADAPTED
When work is complete:
- **DO** verify tests pass
- **DO** push the branch and create a PR (if appropriate)
- **DO NOT** remove or clean up the worktree — the human runs `end-task` for that
- **DO NOT** merge locally — PRs are the standard integration path

## Standard Workflow

1. Read `.agent-workspace/config.json` to understand the repo and base branch.
2. Create a new task branch from the current base branch.
3. **Check for applicable skills** — brainstorming for new features, systematic-debugging for bugs.
4. Follow the skill workflow: brainstorm → write plan → execute (with TDD) → review → finish.
5. Prompt the developer for review before final PR actions.

## Guardrails

- **Do NOT** run `start-task` or `end-task` scripts — these are for the human only.
- **Do NOT** work directly on the base branch — always create a task branch.
- **Do NOT** reuse another task's branch or folder for a new ticket.
- **Do NOT** skip skills — if one applies, you must use it.
- Keep changes scoped to the requested task.
- Ask for review before final PR actions.
- Prefer small, reviewable commits.

## Instruction Priority

1. **Human's direct instructions** — highest priority
2. **This file (CLAUDE.md)** — workspace-level overrides
3. **Superpowers skills** — methodology and workflow
4. **Default system behavior** — lowest priority

If this file conflicts with a skill, follow this file. If the human contradicts this file, follow the human.
