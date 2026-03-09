````skill
# End Task Workflow

## Overview
Use this skill when the user is signaling that a task is complete and the local task workspace should be cleaned up.

## Trigger Phrases
Match this skill when prompts are similar to:
- "cleanup this task"
- "cleanup this ticket"
- "we are done with this issue"
- "Close this issue"

Also trigger on close variants like:
- "remove this task folder"
- "clean up this branch folder"
- "we're finished with this ticket"

## Goal
Clean up the task workspace by calling the `end_task.py` script, which:
- Checks out the base branch and pulls latest
- Removes any leftover uncommitted files
- Removes the symlink from the workspace root
- Releases the lock so the worktree can be reused

## End Task Steps

1. **Identify task folder**
   - Determine the exact task-specific folder path (or symlink) under this workspace.
   - This is usually the symlink at the workspace root (e.g. `<workspace-root>/<task-short-name>`).

2. **Confirm target is a task folder**
   - Ensure the target is not the workspace root or any shared/global folder.
   - Never pass `.agent-workspace`, `.agent_skills`, `.scripts`, or other shared folders.

3. **Call the end_task script**
   Run the script, passing the task folder or symlink path as the argument:
   ```bash
   .scripts/end_task.py <task-folder-or-symlink-path>
   ```
   The script will:
   - Checkout the base branch configured in `.agent-workspace/config.json`
   - `git pull` to keep the worktree up to date for the next task
   - Run `git reset --hard` and `git clean -fd` to remove leftover files
   - Remove the symlink from the workspace root
   - Delete the lock folder for the acquired worktree (releasing the lock)

4. **Report completion**
   - Confirm the task has been cleaned up and the lock released.

## Guardrails
- Always use `end_task.py` — do not manually delete folders, remove symlinks, or release locks without the script.
- Never delete the workspace root.
- Never pass `.agent-workspace`, `.agent_skills`, `.scripts`, or other shared folders to the script.
- The script requires the worktree to be a valid git repo; verify the path before calling.

## Quick Command Reference
```bash
# End a task (pass the symlink or worktree folder path)
.scripts/end_task.py <task-folder-or-symlink-path>
```

## Completion Signal
This skill is complete when the script exits successfully and the lock directory for the worktree no longer exists.
````
