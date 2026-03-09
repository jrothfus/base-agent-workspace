# How it works

## 1. Initialization
- Give details for initialization including repo name, repo url, and base branch

### 1.1 Pull Repo
We pull the repo into `.agent-workspace/base-repo`

### 1.2 Run Init Scripts
- `generate-workspace-ids.sh`: generates a list of unique ids and puts them into `.agent-workspace/worktree-ids.json`. These will be used to make unique worktree folders later on
- `protect-base-folder.sh`: protects the base workspace folder from being deleted on accident (unless you use sudo commands)

## 2. Starting a task

### Prompt Agent to "start a new task"
Give the agent something to work on and ask it to start this as a new task. This will trigge the `start_task` skill inside `.agent_skills/start_task`

### Start Task Script
The start task skill will cause the Agent to call the `start_task.py` inside `.scripts`, and pass it a short name that describes the task (~7 words or less)
It does the following:
- Grabs the list of ids from `.agent-workspace/worktree-ids.json`
- Attempts to create a folder inside `.agent-workspace/locks`
- If making the directory doesn't succeed it tries every id until one does
    - If no ID's work we temporarily generate a new unique id and mkdir that id
- At this point we have **acquired a lock** on this id
    - Attempting to create a directory in the filesystem is an atomic operation that fails if an existing folder already exists. This makes it a perfect, long term lock.
- It looks inside `.agent-workspace/worktrees` to see if a folder with that unique id exists, and if it doesn't it copies the base repo at `.agent-workspace/base-repo` into a new folder with that unique id. Before it does this it git pulls the base repo to make sure it's up to date.
- Once we have this new worktree folder we do a git pull to make sure its up to date.
- Now we use the short name given to the script to create a symbolic link at the root directory of this workspace

Once this is done we will have an isolated repo (we call these worktrees) for the agent to do its work, we know that only this AI agent is working on this worktree, and we will have a symbolic link to the working folder that makes it more human-navigatable.

## 3. Ending a task

### Prompt Agent to "end this task"
When you want to finish/close out a task (this would be after you've pushed/merged code or decided you didn't want to), we tell the agent "ok, close out this task". That will cause the agent to use the `end_task` skill at `.agent_skills/end_task`.


### End Task Script
The end task skill calls the `end_task.py` script inside `.scripts`
- Checks out the base branch for this worktree
- git pulls
- runs git status and removes any leftover files
- deletes the lock folder for the unique id for the given worktree (remember the name of the worktree folder is the id)
- At this point we have unlocked the lock on this worktree and another agent is free to take it over