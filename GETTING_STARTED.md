# Getting Started with base-agent-workspace

## First Time Setup

### 1. Initialize the workspace

Run the initialization script:

```bash
python3 init-workspace.py
```

This will:
- Initialize the Superpowers git submodule
- Pull the base repository
- Check for required dependencies
- Generate unique worktree IDs
- Protect the base folder from accidental deletion
- Sync agent skills into the workspace

### 2. Further Configure your workspace (optional)

Edit `.agent-workspace/config.json` to set your workspace details:

```json
{
    "repo": {
        "name": "your-repo-name",
        "url": "https://github.com/your-org/your-repo.git"
    },
    "base_branch": "main",
    "max_number_of_worktrees": 3
}
```

## Starting a Task

Run `start-task.py` from the workspace root with a short description:

```bash
python3 start-task.py fix login bug
```

To also launch an AI agent with a prompt, add `--` followed by the prompt:

```bash
python3 start-task.py fix login bug -- fix the broken login redirect after OAuth callback
```

The script will:
- Acquire a lock on an available worktree
- Pull the latest changes from the base branch
- Create a symbolic link in the workspace root named after your description (e.g. `fix-login-bug/`)
- Open VS Code at the symlink
- `cd` into the symlink directory
- If a prompt was given, run `claude "<prompt>"` — when claude exits you remain in the worktree directory

## Ending a Task

### From inside the worktree (most common)

After `start-task.py` runs, your terminal is inside the worktree (e.g. `fix-login-bug/`). When you're done:

```bash
python3 ../end-task.py
```

### From anywhere else

Run `end-task.py` from the workspace root (or any other directory):

```bash
python3 end-task.py
```

If there is only one active task, it will ask you to confirm. If there are multiple, it will show a numbered list:

```
Active tasks:
  1) fix-login-bug
  2) add-dark-mode

Select task to end [1-2]:
```

### What ending a task does

- Checks out the base branch and pulls latest
- Resets and cleans uncommitted files in the worktree
- Removes the symbolic link
- Releases the lock so the worktree slot is available for reuse

## Quick Command Reference

| Action | Command |
|--------|---------|
| Initialize workspace | `python3 init-workspace.py` |
| Start a task | `python3 start-task.py <description>` |
| Start a task with an AI prompt | `python3 start-task.py <description> -- <prompt>` |
| End a task (from inside worktree) | `python3 ../end-task.py` |
| End a task (from workspace root) | `python3 end-task.py` |
| Clean stuck locks | `python3 clean-locks.py` |

## Troubleshooting

### All worktrees are locked

If all worktrees are in use the system will create an additional one with a random ID. Note that these overflow worktrees persist after the task ends but won't be automatically reused by future tasks. To reclaim disk space, run:

```bash
python3 clean-locks.py
```

This removes locks for worktrees that are no longer actively being used.
