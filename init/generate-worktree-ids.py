#!/usr/bin/env python3
"""
Generate unique worktree IDs and write them to worktree-ids.json.

Reads max_number_of_worktrees from config.json and generates that many
random 12-character alphanumeric IDs.
"""
import json
import secrets
import string
import sys
from pathlib import Path


def main() -> None:
    if len(sys.argv) > 1:
        workspace_root = Path(sys.argv[1])
    else:
        workspace_root = Path(__file__).resolve().parent.parent

    agent_workspace_dir = workspace_root / ".agent-workspace"
    config_path = agent_workspace_dir / "config.json"
    worktree_ids_path = agent_workspace_dir / "worktree-ids.json"

    if not agent_workspace_dir.is_dir():
        print(
            f"Error: .agent-workspace directory not found: {agent_workspace_dir}",
            file=sys.stderr,
        )
        sys.exit(1)

    if not config_path.is_file():
        print(f"Error: config file not found: {config_path}", file=sys.stderr)
        sys.exit(1)

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    max_count = config.get("max_number_of_worktrees")
    if not isinstance(max_count, int) or max_count < 1:
        print(
            f"Error: max_number_of_worktrees must be a positive integer in {config_path}",
            file=sys.stderr,
        )
        sys.exit(1)

    alphabet = string.ascii_lowercase + string.digits
    ids = ["".join(secrets.choice(alphabet) for _ in range(12)) for _ in range(max_count)]

    with open(worktree_ids_path, "w", encoding="utf-8") as f:
        json.dump(ids, f, indent=2)
        f.write("\n")

    print(f"Generated {max_count} worktree IDs in: {worktree_ids_path}")


if __name__ == "__main__":
    main()
