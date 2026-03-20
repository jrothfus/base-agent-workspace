# How it works

## 1. Initialization
- Give details for initialization including repo name, repo url, and base branch

### 1.1 Pull Repo
We pull the repo into `.agent-workspace/base-repo`

### 1.2 Run Init Scripts
- `dependencies-check.py`: verifies required dependencies are available
- `generate-worktree-ids.py`: generates a list of unique ids and puts them into `.agent-workspace/worktree-ids.json`. These will be used to make unique worktree folders later on
- `protect-base-folder.py`: protects the base workspace folder from being deleted on accident (unless you use sudo commands)
- `sync-agent-skills.py`: syncs agent skills into the workspace

## 2. Starting a task

### Run `python3 start-task.py`
From the workspace root, run:
```bash
python3 start-task.py <description>
# or with an AI prompt:
python3 start-task.py <description> -- <agent prompt>
```

### What the script does
The `start-task.py` script calls `.scripts/start_task.py` under the hood:
- Grabs the list of ids from `.agent-workspace/worktree-ids.json`
- Attempts to create a folder inside `.agent-workspace/locks`
- If making the directory doesn't succeed it tries every id until one does
    - If no IDs work we temporarily generate a new unique id and mkdir that id
- At this point we have **acquired a lock** on this id
    - Attempting to create a directory in the filesystem is an atomic operation that fails if an existing folder already exists. This makes it a perfect, long term lock.
- It looks inside `.agent-workspace/worktrees` to see if a folder with that unique id exists, and if it doesn't it copies the base repo at `.agent-workspace/base-repo` into a new folder with that unique id. Before it does this it git pulls the base repo to make sure it's up to date.
- Once we have this new worktree folder we do a git pull to make sure its up to date.
- Runs any startup commands defined in `.agent-workspace/start-task-commands.json` (if the file exists)
- Injects skill, agent, and command symlinks into the worktree's `.claude/`, `.codex/`, and `.openclaw/` directories (sourced from `.agent_skills/` and `.superpowers/`)
- Uses the description to create a symbolic link at the root directory of this workspace

Once setup is complete, the script:
- Opens VS Code at the symlink path
- `cd`s into the symlink directory
- Runs `claude "<prompt>"` if a prompt was provided (you remain in the worktree directory after claude exits)

## 3. Ending a task

### Run `python3 end-task.py`
From inside the worktree (the most common case after `start-task.py`):
```bash
python3 ../end-task.py
```

Or from anywhere else (workspace root, another directory):
```bash
python3 end-task.py
```
When run from outside a worktree it lists all active tasks by their symlink name (or ID if no symlink exists) and prompts you to pick one.

### What the script does
The `end-task.py` script calls `.scripts/end_task.py`:
- Checks out the base branch for this worktree and git pulls
- Runs git reset and removes any leftover uncommitted files
- Removes the symlink from the workspace root
- Deletes the lock folder for the unique id (releasing the lock so another task can use this worktree)