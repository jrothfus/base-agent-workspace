# Atlassian CLI (acli) - Jira Integration

## Overview
Guide for using the Atlassian CLI (`acli`) to interact with Jira from the command line. This skill covers viewing, creating, searching, and managing Jira work items for the Postman app project.

> **IMPORTANT:** This is the ONLY supported method for interacting with Jira. Do NOT use any Jira MCP server, Jira REST API, or other Jira integration tools. ALL Jira operations MUST go through the `acli` CLI tool described in this skill.

## When to Use This Skill

**Use this skill ANY time Jira is mentioned**, including but not limited to:
- User mentions a Jira ticket ID (e.g., `SGI-1121`, `SGI-1234`, `PROJ-456`)
- User asks to "pull information from a ticket" or "get ticket details"
- User asks to "look up", "check", "view", or "read" a Jira ticket
- User asks to create, update, or manage Jira tickets
- User says "jira", "ticket", "issue", "work item", or "story" in context of project management
- Documenting completed work in Jira
- Tracking bugs, tasks, and features
- Automating Jira ticket creation in workflows
- Linking code changes to Jira tickets
- Searching for existing tickets or checking ticket status

## Installation & Setup

### Check Installation
```bash
which acli
# Output: /opt/homebrew/bin/acli (or similar)
```

### Authentication
```bash
acli auth
# Follow prompts to authenticate with Atlassian
```

## Command Structure

### Basic Structure
```bash
acli [service] [resource] [action] [flags]
```

**Services:**
- `jira` - Jira Cloud commands
- `confluence` - Confluence Cloud commands
- `admin` - Admin commands

**Common Jira Resources:**
- `workitem` - Jira work items (issues)
- `project` - Jira projects
- `board` - Jira boards
- `sprint` - Jira sprints

## Jira Work Item Commands

### Create a Work Item

#### Basic Creation
```bash
acli jira workitem create \
  --project "PROJECT_KEY" \
  --type "Task" \
  --summary "Brief description of the task" \
  --description "Detailed description of what needs to be done"
```

#### Common Issue Types
- `Task` - General work item
- `Bug` - Bug report
- `Story` - User story
- `Epic` - Large feature or initiative
- `Subtask` - Child task of another issue

#### With Additional Options
```bash
acli jira workitem create \
  --project "SGI" \
  --type "Task" \
  --summary "Add title to SDK Gen Editor" \
  --description "Full description here" \
  --assignee "user@example.com" \
  --label "frontend,ui,enhancement"
```

#### Using Files for Description
```bash
# From text file
acli jira workitem create \
  --project "SGI" \
  --type "Task" \
  --summary "Task summary" \
  --description-file "description.txt"

# From file with both summary and description
acli jira workitem create \
  --project "SGI" \
  --type "Task" \
  --from-file "workitem.txt"
```

#### Using JSON for Complex Creation
```bash
# Generate template JSON
acli jira workitem create --generate-json

# Create from JSON
acli jira workitem create --from-json "workitem.json"
```

### Search Work Items
```bash
# Basic search
acli jira workitem search

# Search with JQL (Jira Query Language)
acli jira workitem search --jql "project = SGI AND status = 'In Progress'"

# Search and output as JSON
acli jira workitem search --json
```

### View Work Item Details
```bash
acli jira workitem view SGI-1234
```

### Edit Work Item
```bash
acli jira workitem edit SGI-1234 \
  --summary "Updated summary" \
  --description "Updated description"
```

### Assign Work Item
```bash
# Assign to specific user
acli jira workitem assign SGI-1234 --assignee "user@example.com"

# Self-assign
acli jira workitem assign SGI-1234 --assignee "@me"
```

### Transition Work Item
```bash
# Move through workflow (e.g., To Do -> In Progress -> Done)
acli jira workitem transition SGI-1234 --to "In Progress"
```

### Add Comment
```bash
acli jira workitem comment add SGI-1234 --comment "Update on progress"
```

### Link Work Items
```bash
acli jira workitem link SGI-1234 SGI-1235 --type "relates to"
```

## Postman-Specific Projects

### SGI Project (SDK Generator)
Project key: `SGI`

**Common use cases:**
- SDK generation features
- SDK UI improvements
- SDK data handling
- API client SDK integrations

**Example:**
```bash
acli jira workitem create \
  --project "SGI" \
  --type "Task" \
  --summary "Add new SDK language support" \
  --description "Add support for generating Go SDKs from collections"
```

### Creating Tickets for Code Changes
When documenting completed work:

```bash
acli jira workitem create \
  --project "SGI" \
  --type "Task" \
  --summary "Add title to SDK Gen Editor Overview tab" \
  --description "Added a large, left-aligned title to the SDK Gen Editor Overview tab that displays the entity name followed by 'SDK'.

Changes Made:
- Updated Overview.jsx to include a centered title section
- Title uses Aether design tokens for consistent styling
- Layout matches collections workbench pattern

Files Modified:
- src/renderer/runtime-repl/sdk-gen/workbench/Overview.jsx

This improves visual consistency between SDK Gen Editor and Collections Editor."
```

## Common Flags Reference

### Create Work Item Flags
```bash
-p, --project string            Project key (required)
-t, --type string              Issue type (required)
-s, --summary string           Issue summary (required)
-d, --description string       Issue description
    --description-file string  Read description from file
-a, --assignee string          Assignee email or '@me' for self-assign
-l, --label strings            Comma-separated labels
    --parent string            Parent issue ID (for subtasks)
-e, --editor                   Open text editor for input
-f, --from-file string         Read from file
    --from-json string         Read from JSON file
    --generate-json            Generate JSON template
    --json                     Output in JSON format
```

## Best Practices

### Writing Good Issue Summaries
- Keep it concise (one line)
- Use action verbs (Add, Fix, Update, Remove)
- Be specific about what changed
- Example: "Add title to SDK Gen Editor Overview tab"

### Writing Good Descriptions
Include:
1. **Context**: What problem does this solve?
2. **Changes Made**: Bullet list of changes
3. **Files Modified**: List of affected files
4. **Impact**: How does this improve the product?

**Template:**
```
## Context
Brief explanation of why this change was needed.

## Changes Made
- First change
- Second change
- Third change

## Files Modified
- path/to/file1.js
- path/to/file2.tsx

## Impact
How this improves the user experience or developer experience.
```

### Using Labels Effectively
Common label patterns:
- **Component**: `frontend`, `backend`, `api`, `ui`
- **Type**: `bug`, `enhancement`, `refactor`, `docs`
- **Priority**: `critical`, `high`, `medium`, `low`
- **Area**: `sdk-gen`, `collections`, `workbench`

Example:
```bash
--label "frontend,ui,enhancement,sdk-gen"
```

### Linking to Code
Include in description:
- Branch names
- PR/MR numbers
- Commit hashes (if applicable)
- File paths

## Advanced Usage

### Bulk Create Issues
```bash
acli jira workitem create-bulk --from-json "issues.json"
```

### Working with Custom Fields
Some projects may have custom fields. Use `--generate-json` to see available fields:

```bash
acli jira workitem create --project "SGI" --generate-json > template.json
# Edit template.json to add custom field values
acli jira workitem create --from-json "template.json"
```

### JSON Output for Scripting
```bash
# Get issue details as JSON
acli jira workitem view SGI-1234 --json | jq '.fields.status.name'

# Search and process results
acli jira workitem search --jql "project = SGI" --json | jq '.issues[].key'
```

### Integration with Git
Create issues from commit messages:

```bash
# Example script
ISSUE=$(acli jira workitem create \
  --project "SGI" \
  --type "Task" \
  --summary "$(git log -1 --pretty=%s)" \
  --json | jq -r '.key')

echo "Created issue: $ISSUE"
```

## Troubleshooting

### Authentication Issues
```bash
# Re-authenticate
acli auth

# Check authentication status
acli jira workitem search
```

### Permission Issues
- Ensure you have "Create Issues" permission in the project
- Check that the issue type is available in the project
- Verify project key is correct

### Finding Project Keys
```bash
# List all projects
acli jira project list
```

### Finding Issue Types
```bash
# View project details including issue types
acli jira project view PROJECT_KEY
```

## Common Workflows

### Documenting a Completed Feature
```bash
# 1. Create the ticket
ISSUE=$(acli jira workitem create \
  --project "SGI" \
  --type "Task" \
  --summary "Feature summary" \
  --description "Detailed description" \
  --assignee "@me" \
  --json | jq -r '.key')

# 2. Transition to In Progress
acli jira workitem transition "$ISSUE" --to "In Progress"

# 3. Add comments as you work
acli jira workitem comment add "$ISSUE" --comment "Implementation complete"

# 4. Mark as Done
acli jira workitem transition "$ISSUE" --to "Done"

echo "Completed: https://postmanlabs.atlassian.net/browse/$ISSUE"
```

### Creating Bug Reports
```bash
acli jira workitem create \
  --project "SGI" \
  --type "Bug" \
  --summary "Brief bug description" \
  --description "## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: macOS
- Version: 12.0.0
- Browser: Chrome 120" \
  --label "bug,sdk-gen"
```

## Example: Real-World Usage

### Creating SGI-1110
```bash
acli jira workitem create \
  --project "SGI" \
  --type "Task" \
  --summary "Add title to SDK Gen Editor Overview tab" \
  --description "Added a large, left-aligned title to the SDK Gen Editor Overview tab that displays the entity name followed by 'SDK' (e.g., 'My Collection SDK'), or 'Generate an SDK' when no entity is selected.

Changes Made:
- Updated Overview.jsx to include a centered title section above the SDKSection component
- Title uses Aether design tokens for consistent styling (text-size-xxxl, text-weight-bold)
- Layout matches the collections workbench overview tab pattern with centered content container and 800px max width
- Title is left-aligned within the centered container

Files Modified:
- src/renderer/runtime-repl/sdk-gen/workbench/Overview.jsx

This improves the visual consistency between the SDK Gen Editor and the Collections Editor, providing better context to users about which entity they're generating SDKs for."
```

**Result:** Created SGI-1110 at https://postmanlabs.atlassian.net/browse/SGI-1110

## Help Commands

```bash
# General help
acli --help

# Jira help
acli jira --help

# Work item help
acli jira workitem --help

# Specific command help
acli jira workitem create --help
```

## Related Documentation
- Official acli docs: Run `acli help` or visit Atlassian documentation
- Jira Query Language (JQL): For advanced searching
- Atlassian API: For custom integrations

## Common Pitfalls
1. **Wrong project key** - Double-check the project key is correct
2. **Missing required fields** - Use `--generate-json` to see all fields
3. **Invalid issue type** - Not all issue types are available in all projects
4. **Authentication expired** - Re-run `acli auth` if commands fail
5. **Description formatting** - Use quotes and escape special characters properly
