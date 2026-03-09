````skill
# Start Task Workflow

## Overview
Use this skill when the user asks to begin a **new implementation task** in this workspace.

This workflow is script-driven. The agent must call `.scripts/start_task.py` so lock acquisition and worktree preparation are always consistent.

## Trigger Phrases
Match this skill when prompts are similar to:
- "Can you start a new task"
- "can you solve this issue for me"
- "can we do this ticket"

Also trigger on close variants like:
- "start work on this"
- "pick up this bug"
- "let’s work this Jira"
- "create a branch for this task"

## Goal
Start an isolated task worktree by invoking the shared start-task script, then continue implementation in that prepared folder.

## Source of Truth
The script reads and enforces workspace configuration from:
1. `.agent-workspace/config.json`
2. `.agent-workspace/worktree-ids.json`
3. `.agent-workspace/start-task-commands.json`

## Required Execution

1. **Pick a short task name (<= 7 words)**
   - Convert the request into a concise name, e.g. `fix auth retry`.

2. **Run the script from workspace root**
   - Command:
     ```bash
     ./.scripts/start_task.py "<short-task-name>"
     ```

3. **Use script output as the source of truth**
   - The script returns:
     - lock id
     - worktree path
     - symlink/shortcut path at workspace root
   - Continue all task work in that created worktree (or via the symlink).

4. **Begin implementation**
   - Summarize the ticket scope and assumptions.
   - Implement only requested changes in the newly prepared task folder.

## Guardrails
- Always call `.scripts/start_task.py`; do not manually reimplement lock/worktree logic.
- Keep the provided short name concise and descriptive.
- If the script fails, report stderr/output and do not continue implementation setup steps manually.
- Keep scope tight to the requested ticket/issue.

## Quick Command Reference
```bash
./.scripts/start_task.py "<short-task-name>"
```

## Completion Signal
This skill is complete when:
- `.scripts/start_task.py` succeeds
- A lock id has been acquired
- A worktree exists under `.agent-workspace/worktrees/<lock-id>`
- A root symlink has been created for navigation
- Agent confirms the path it will use for implementation
````