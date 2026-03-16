#!/usr/bin/env bash
set -euo pipefail

SCRIPT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/$(basename "${BASH_SOURCE[0]}")"
WORKSPACE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_PATH="$WORKSPACE_ROOT/.agent-workspace/config.json"
AGENT_WORKSPACE_DIR="$WORKSPACE_ROOT/.agent-workspace"
BASE_REPO_DIR="$AGENT_WORKSPACE_DIR/base-repo"
INIT_DIR="$WORKSPACE_ROOT/init"

if [[ ! -d "$AGENT_WORKSPACE_DIR" ]]; then
  echo "Error: .agent-workspace directory not found at: $AGENT_WORKSPACE_DIR" >&2
  exit 1
fi

if [[ ! -d "$INIT_DIR" ]]; then
  echo "Error: init directory not found at: $INIT_DIR" >&2
  exit 1
fi

current_repo_name=""
current_repo_url=""
current_base_branch=""

if [[ -f "$CONFIG_PATH" ]]; then
  config_values="$(python3 - "$CONFIG_PATH" <<'PY'
import json
import sys

path = sys.argv[1]
with open(path, 'r', encoding='utf-8') as file_handle:
    data = json.load(file_handle)

repo = data.get('repo') or {}
name = repo.get('name', '')
url = repo.get('url', '')
base_branch = data.get('base_branch', '')

print(name)
print(url)
print(base_branch)
PY
)"

  current_repo_name="$(printf '%s\n' "$config_values" | sed -n '1p')"
  current_repo_url="$(printf '%s\n' "$config_values" | sed -n '2p')"
  current_base_branch="$(printf '%s\n' "$config_values" | sed -n '3p')"
fi

prompt_with_default() {
  local prompt_label="$1"
  local default_value="$2"
  local input_value=""

  while true; do
    if [[ -n "$default_value" ]]; then
      read -r -p "$prompt_label [$default_value]: " input_value
      input_value="${input_value:-$default_value}"
    else
      read -r -p "$prompt_label: " input_value
    fi

    if [[ -n "$input_value" ]]; then
      printf '%s' "$input_value"
      return 0
    fi

    echo "Value is required. Please try again."
  done
}

echo "Workspace init"
echo "--------------"

repo_name="$(prompt_with_default "Repo name" "$current_repo_name")"
repo_url="$(prompt_with_default "Repo URL" "$current_repo_url")"
base_branch="$(prompt_with_default "Base branch" "$current_base_branch")"

python3 - "$CONFIG_PATH" "$repo_name" "$repo_url" "$base_branch" <<'PY'
import json
import os
import sys

config_path = sys.argv[1]
repo_name = sys.argv[2]
repo_url = sys.argv[3]
base_branch = sys.argv[4]

config = {}
if os.path.exists(config_path):
  with open(config_path, 'r', encoding='utf-8') as file_handle:
    existing_config = json.load(file_handle)

  if isinstance(existing_config, dict):
    config = existing_config

repo = config.get("repo") if isinstance(config.get("repo"), dict) else {}
repo["name"] = repo_name
repo["url"] = repo_url

config["repo"] = repo
config["base_branch"] = base_branch

os.makedirs(os.path.dirname(config_path), exist_ok=True)
with open(config_path, 'w', encoding='utf-8') as file_handle:
    json.dump(config, file_handle, indent=4)
    file_handle.write('\n')
PY

echo "Updated config: $CONFIG_PATH"

echo "Initializing superpowers submodule..."
git -C "$WORKSPACE_ROOT" submodule update --init --recursive

if [[ ! -d "$BASE_REPO_DIR/.git" ]]; then
  if [[ -e "$BASE_REPO_DIR" ]]; then
    echo "Error: $BASE_REPO_DIR exists but is not a git repository" >&2
    exit 1
  fi

  echo "Cloning repo into $BASE_REPO_DIR"
  git clone "$repo_url" "$BASE_REPO_DIR"
fi

git -C "$BASE_REPO_DIR" remote set-url origin "$repo_url"
git -C "$BASE_REPO_DIR" fetch origin
git -C "$BASE_REPO_DIR" checkout "$base_branch"
git -C "$BASE_REPO_DIR" pull --ff-only origin "$base_branch"
echo "Base repo synced at $BASE_REPO_DIR"

ran_any_script="false"
for script_file in "$INIT_DIR"/*.sh; do
  [[ -f "$script_file" ]] || continue

  full_script_path="$(cd "$(dirname "$script_file")" && pwd)/$(basename "$script_file")"
  if [[ "$full_script_path" == "$SCRIPT_PATH" ]]; then
    continue
  fi

  ran_any_script="true"
  if [[ ! -x "$full_script_path" ]]; then
    chmod +x "$full_script_path"
  fi

  echo "Running init script: $(basename "$full_script_path")"
  "$full_script_path" "$WORKSPACE_ROOT"
done

if [[ "$ran_any_script" == "false" ]]; then
  echo "No additional shell scripts found in: $INIT_DIR"
fi

echo "Workspace initialization complete."