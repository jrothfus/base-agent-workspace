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

## Starting Your First AI Task

### 1. Ask your AI agent to start a task

Simply say to your AI:

```
Start a new task to [describe your task here]
```

Example:
```
Start a new task to fix the login button styling issue
```

Or Ask it to handle a jira ticket (must be logged into the ACLI)
```
Start a new task with ticket [number]
```

The AI will:
- Pull ticket details (if applicable)
- Acquire a lock on an available worktree
- Create or reuse an isolated working folder
- Switch to the base branch and pull latest changes
- Create a new task branch
- Create a symbolic link with your task description

### 2. Let the AI work

The AI will work in its isolated environment at:
- `.agent-workspace/worktrees/{unique-id}/`
- Or via the symbolic link at the workspace root

### 3. Review the changes

After the AI completes its work, review the code in the worktree folder. You can:
- Use another AI agent to review the code
- Manually inspect the changes
- Run tests

### 4. Commit and push

Tell your AI:

```
Commit and push these changes, then create a PR
```

### 5. End the task

When done (after merging or abandoning the work):

```
End this task and clean up
```

The AI will:
- Switch back to base branch
- Pull latest changes
- Clean up uncommitted files
- Release the lock for other agents to use

## Quick Command Reference

| Action | Command |
|--------|---------|
| Initialize workspace | `./init-workspace.sh` |
| Start a task | Ask AI: "Start a new task to [task]" |
| End a task | Ask AI: "End this task" |
| Clean stuck locks | `./clean-locks.sh` |

## Troubleshooting

### All worktrees are locked

If all worktrees are in use, the system will temporarily create a new one. Alternatively, run:

```bash
./clean-locks.sh
```

This removes locks for worktrees that aren't actively being used.

### Need to manually start/end tasks

Start task:
```bash
python3 .scripts/start_task.py "short task description"
```

End task (from within a worktree):
```bash
python3 ../.scripts/end_task.py
```