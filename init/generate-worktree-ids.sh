#!/usr/bin/env bash
set -euo pipefail

TARGET_DIR="${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
AGENT_WORKSPACE_DIR="$TARGET_DIR/.agent-workspace"
CONFIG_PATH="$AGENT_WORKSPACE_DIR/config.json"
WORKTREE_IDS_PATH="$AGENT_WORKSPACE_DIR/worktree-ids.json"

if [[ ! -d "$AGENT_WORKSPACE_DIR" ]]; then
  echo "Error: .agent-workspace directory not found: $AGENT_WORKSPACE_DIR" >&2
  exit 1
fi

if [[ ! -f "$CONFIG_PATH" ]]; then
  echo "Error: config file not found: $CONFIG_PATH" >&2
  exit 1
fi

max_count="$(python3 - "$CONFIG_PATH" <<'PY'
import json
import sys

path = sys.argv[1]

with open(path, 'r', encoding='utf-8') as file_handle:
    config = json.load(file_handle)

value = config.get('max_number_of_worktrees')
if not isinstance(value, int) or value < 1:
    raise SystemExit(1)

print(value)
PY
)" || {
  echo "Error: max_number_of_worktrees must be a positive integer in $CONFIG_PATH" >&2
  exit 1
}

python3 - "$WORKTREE_IDS_PATH" "$max_count" <<'PY'
import json
import secrets
import string
import sys

output_path = sys.argv[1]
count = int(sys.argv[2])

alphabet = string.ascii_lowercase + string.digits
ids = []
for _ in range(count):
    ids.append(''.join(secrets.choice(alphabet) for _ in range(12)))

with open(output_path, 'w', encoding='utf-8') as file_handle:
    json.dump(ids, file_handle, indent=2)
    file_handle.write('\n')
PY

echo "Generated $max_count worktree IDs in: $WORKTREE_IDS_PATH"