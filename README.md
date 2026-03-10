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
Optional agent skills are available in `.agent_skills/`:

- `acli-jira`: a skill for the Atlassian CLI, specifically for Jira. Makes it easier to pull ticket details at the start of a task.

### Agent Skills in Repo
You can have agent skills in the repo (specified by `repo` inside `.agent-workspace/config.json`)

