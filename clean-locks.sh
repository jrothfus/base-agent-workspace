#!/usr/bin/env bash
#
# Clean all locks from the agent workspace
#
# This removes all lock directories to free up worktree IDs
# that may have been left behind by interrupted or crashed tasks.
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

python3 "${SCRIPT_DIR}/.scripts/clean_locks.py" "$@"
