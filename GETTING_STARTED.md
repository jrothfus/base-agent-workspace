# Getting Started with base-agent-workspace

## First Time Setup

### 1. Initialize the workspace

Run the initialization script:

```bash
./init-workspace.sh
```

This will:
- Pull the base repository
- Generate unique worktree IDs
- Protect the base folder from accidental deletion

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

Run `start-task` from the workspace root with a short description:

```bash
bash start-task fix login bug
```

To also launch an AI agent with a prompt, add `--` followed by the prompt:

```bash
bash start-task fix login bug -- fix the broken login redirect after OAuth callback
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

After `start-task` runs, your terminal is inside the worktree (e.g. `fix-login-bug/`). When you're done:

```bash
bash ../end-task
```

### From anywhere else

Run `end-task` from the workspace root (or any other directory):

```bash
bash end-task
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
| Initialize workspace | `bash init-workspace.sh` |
| Start a task | `bash start-task <description>` |
| Start a task with an AI prompt | `bash start-task <description> -- <prompt>` |
| End a task (from inside worktree) | `bash ../end-task` |
| End a task (from workspace root) | `bash end-task` |
| Clean stuck locks | `bash clean-locks.sh` |

## Troubleshooting

### All worktrees are locked

If all worktrees are in use the system will temporarily create a new one. Alternatively, run:

```bash
bash clean-locks.sh
```

This removes locks for worktrees that are no longer actively being used.
