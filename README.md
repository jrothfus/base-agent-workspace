# base-agent-workspace
To support a workflow where we have multiple agents working on the same repo, 
and want to avoid them running into each other. 

## Read GETTING_STARTED.md
The below is just information about how the repo works, read GETTING_STARTED.md 
to learn how to start developing.

## The Intended Workflow:
- Ask for an AI agent to do a task
- Agent git pulls selected repo into a new folder inside this workspace
- Switched and pulls the selected base branch (as described in `.agent-workspace/config.json`)
- Creates a new branch
- Does work to solve bug/task/ticket/issue 
- AI prompts developer for review
- Developer reviews code (feel free to use another agent to review the code)
- Either Developer or AI commits and pushes to branch, creates a PR

## Skills
In the top level of this workspace there are skills for your AI agents:

### Neccesary
- `start_task`: outlines how to clone, switch to a branch, and start its work
- `end_task`: outlines how to clean up from a task
- `git_skill`: outlines how to deal with git commands (how to do commit messages, how to structure PRs, how to make branch names)

### Extras
- `acli-jira`: a skill for the atlassian CLI, specifically for jira. This makes it easier to pull tickets directly and start work quicker.

### Agent Skills in Repo
You can have agent skills in the repo (specififed by `repo` inside `.agent-workspace/config.json`)

