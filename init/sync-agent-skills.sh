#!/usr/bin/env bash
set -euo pipefail

WORKSPACE_ROOT="${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
SOURCE_DIR="$WORKSPACE_ROOT/.agent_skills"
TARGET_DIRS=(
  "$WORKSPACE_ROOT/.claude"
  "$WORKSPACE_ROOT/.codex"
  "$WORKSPACE_ROOT/.openclaw"
)

if [[ ! -d "$SOURCE_DIR" ]]; then
  echo "Skipping skill sync: source directory not found at $SOURCE_DIR"
  exit 0
fi

for target_dir in "${TARGET_DIRS[@]}"; do
  mkdir -p "$target_dir"

  link_path="$target_dir/skills"
  if [[ -e "$link_path" || -L "$link_path" ]]; then
    rm -rf "$link_path"
  fi

  ln -s "$SOURCE_DIR" "$link_path"
  echo "Linked skills: $link_path -> $SOURCE_DIR"
done
