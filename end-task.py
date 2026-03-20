#!/usr/bin/env python3
"""
End a task: detect the active worktree (from cwd or interactive selection),
then delegate cleanup to .scripts/end_task.py.
"""
import json
import os
import subprocess
import sys
from pathlib import Path


def is_known_worktree_id(worktree_ids_path: Path, name: str) -> bool:
    if not worktree_ids_path.is_file():
        return False
    with open(worktree_ids_path, "r", encoding="utf-8") as f:
        ids = json.load(f)
    return name in ids


def find_symlink_for_worktree(workspace_root: Path, worktree_dir: str) -> str | None:
    for item in workspace_root.iterdir():
        if item.is_symlink():
            try:
                if str(item.resolve()) == worktree_dir:
                    return item.name
            except (OSError, RuntimeError):
                continue
    return None


def discover_active_tasks(
    workspace_root: Path, locks_dir: Path
) -> tuple[list[str], list[str]]:
    """Return parallel lists of (display_names, task_paths) for active locks."""
    names: list[str] = []
    paths: list[str] = []

    if not locks_dir.is_dir():
        return names, paths

    for lock_entry in sorted(locks_dir.iterdir()):
        if not lock_entry.is_dir():
            continue

        lock_id = lock_entry.name
        worktree_dir = str(workspace_root / ".agent-workspace" / "worktrees" / lock_id)

        symlink_name = find_symlink_for_worktree(workspace_root, worktree_dir)

        if symlink_name:
            names.append(symlink_name)
            paths.append(str(workspace_root / symlink_name))
        else:
            names.append(lock_id)
            paths.append(worktree_dir)

    return names, paths


def select_task_interactively(names: list[str], paths: list[str]) -> list[str]:
    if len(names) == 1:
        print(f"Active task: {names[0]}")
        confirm = input("End this task? [y/N] ").strip()
        if confirm.lower() != "y":
            print("Aborted.", file=sys.stderr)
            sys.exit(1)
        return [paths[0]]

    print("Active tasks:")
    for i, name in enumerate(names):
        print(f"  {i + 1}) {name}")
    print(f"  a) All of the above")
    print()

    while True:
        choice = input(f"Select task to end [1-{len(names)}, a=all]: ").strip().lower()
        if choice == "a":
            confirm = input(f"End all {len(names)} tasks? [y/N] ").strip()
            if confirm.lower() != "y":
                print("Aborted.", file=sys.stderr)
                sys.exit(1)
            return list(paths)
        if choice.isdigit() and 1 <= int(choice) <= len(names):
            return [paths[int(choice) - 1]]
        print(f"Invalid selection. Enter a number between 1 and {len(names)}, or 'a' for all.")


def end_single_task(workspace_root: Path, task_path: str) -> int:
    result = subprocess.run(
        [sys.executable, str(workspace_root / ".scripts" / "end_task.py"), task_path],
    )
    return result.returncode


def main() -> None:
    workspace_root = Path(__file__).resolve().parent
    worktree_ids_path = workspace_root / ".agent-workspace" / "worktree-ids.json"
    locks_dir = workspace_root / ".agent-workspace" / "locks"

    end_all = "--all" in sys.argv[1:]
    task_paths: list[str] = []
    cwd_basename = Path.cwd().name

    if end_all:
        names, paths = discover_active_tasks(workspace_root, locks_dir)
        if not names:
            print("No active tasks found.", file=sys.stderr)
            sys.exit(1)
        print(f"Ending all {len(names)} active tasks: {', '.join(names)}")
        task_paths = paths
    elif is_known_worktree_id(worktree_ids_path, cwd_basename):
        task_paths = [str(Path.cwd())]
    else:
        names, paths = discover_active_tasks(workspace_root, locks_dir)
        if not names:
            print("No active tasks found.", file=sys.stderr)
            sys.exit(1)
        task_paths = select_task_interactively(names, paths)

    failed = 0
    for task_path in task_paths:
        print()
        returncode = end_single_task(workspace_root, task_path)
        if returncode != 0:
            failed += 1

    if failed:
        print(f"\n{failed} of {len(task_paths)} task(s) failed to end.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
