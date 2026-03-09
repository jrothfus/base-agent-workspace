#!/usr/bin/env bash
set -euo pipefail

TARGET_DIR="${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "Error: This script only supports macOS (Darwin)." >&2
  exit 1
fi

if [[ ! -d "$TARGET_DIR" ]]; then
  echo "Error: Target directory does not exist: $TARGET_DIR" >&2
  exit 1
fi

if ls -lde "$TARGET_DIR" | grep -q "everyone deny delete"; then
  echo "Protection already enabled on: $TARGET_DIR"
  ls -lde "$TARGET_DIR"
  exit 0
fi

chmod +a "everyone deny delete" "$TARGET_DIR"

echo "Delete protection enabled on: $TARGET_DIR"
echo "Current ACLs:"
ls -lde "$TARGET_DIR"

echo
echo "Note: Root/sudo can still remove this directory intentionally."
