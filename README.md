# base-agent-workspace
To support a workflow where we have multiple agents working on the same repo, and want to avoid them running into each other. The workflow here is each agent: git pulls selected repo for the selected base branch. Creates a new branch, does work, then prompts developer for next steps including git pushes, PRs etc. 
