# start-task-commands.json

`start-task-commands.json` defines shell commands that run automatically inside a newly prepared worktree before the agent begins work. Place the file at:

```
.agent-workspace/start-task-commands.json
```

If the file is not present, startup proceeds silently with no commands run. Use `start-task-commands.EXAMPLE.json` in this directory as a starting point.

---

## Top-level structure

```json
{
    "version": 1,
    "description": "Human-readable note about this config (ignored by the runner)",
    "commands": [ ... ]
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `version` | number | no | Schema version, currently `1` |
| `description` | string | no | Free-text note, ignored at runtime |
| `commands` | array | yes | Ordered list of command entries to run |

---

## Command entry

Each item in `commands` is an object with the following fields:

```json
{
    "name": "Install dependencies",
    "run": "yarn install",
    "enabled": true,
    "continue_on_error": false,
    "on_fail": { ... }
}
```

| Field | Type | Default | Description |
|---|---|---|---|
| `name` | string | `"Unnamed command"` | Label used in log output |
| `run` | string | — | Shell command to execute in the worktree root |
| `enabled` | boolean | — | Must be `true` for the command to run; set to `false` to skip without deleting |
| `continue_on_error` | boolean | `false` | If `true`, a non-zero exit code is logged but execution continues to the next command |
| `on_fail` | object | — | Optional recovery block to run if this command fails (see below) |

Commands are run in order. If a command is skipped (`enabled: false`) or has an invalid/empty `run` value, it is silently skipped.

---

## on_fail block

If a command fails (non-zero exit code), you can specify a recovery block to attempt before deciding whether to halt:

```json
"on_fail": {
    "continue_on_success": true,
    "commands": [
        {
            "name": "Install yarn and retry",
            "run": "npm install -g yarn && yarn install",
            "enabled": true
        }
    ]
}
```

| Field | Type | Default | Description |
|---|---|---|---|
| `commands` | array | `[]` | List of command entries to run as recovery. Supports the same fields as top-level commands (including nested `on_fail`). |
| `continue_on_success` | boolean | `false` | If `true` and all recovery commands succeed, execution continues to the next top-level command. If `false`, startup halts after recovery regardless of outcome. |

---

## Failure decision tree

```
command runs
├── success → continue to next command
└── failure
      ├── on_fail present?
      │     ├── yes → run on_fail.commands
      │     │         ├── all succeeded AND continue_on_success=true → continue to next command
      │     │         └── otherwise → check continue_on_error
      │     └── no  → check continue_on_error
      └── continue_on_error?
            ├── true  → log warning, continue to next command
            └── false → abort task startup (exit 1)
```

---

## Example

```json
{
    "version": 1,
    "description": "Set up a Node.js project",
    "commands": [
        {
            "name": "Clean build artifacts",
            "run": "yarn clean",
            "enabled": true,
            "continue_on_error": true
        },
        {
            "name": "Install dependencies",
            "run": "yarn install",
            "enabled": true,
            "continue_on_error": false,
            "on_fail": {
                "continue_on_success": true,
                "commands": [
                    {
                        "name": "Install yarn globally and retry",
                        "run": "npm install -g yarn && yarn install",
                        "enabled": true
                    }
                ]
            }
        },
        {
            "name": "Build project",
            "run": "yarn build",
            "enabled": true,
            "continue_on_error": false
        }
    ]
}
```

In this example:
- `yarn clean` is allowed to fail (e.g. clean script not defined) without halting setup.
- `yarn install` will attempt recovery via `npm install -g yarn && yarn install` if it fails. If recovery succeeds, setup continues to the build step. If recovery also fails, startup aborts.
- `yarn build` must succeed or startup aborts.
