#!/usr/bin/env python3
"""
Start a new task: parse arguments, set up the worktree via .scripts/start_task.py,
optionally open an IDE, and optionally launch claude with a prompt.
"""
import json
import subprocess
import sys
from pathlib import Path


def main() -> None:
    workspace_root = Path(__file__).resolve().parent

    description_parts: list[str] = []
    prompt_parts: list[str] = []
    saw_separator = False

    for arg in sys.argv[1:]:
        if arg == "--":
            saw_separator = True
        elif not saw_separator:
            description_parts.append(arg)
        else:
            prompt_parts.append(arg)

    if not description_parts:
        print(
            "Usage: python3 start-task.py <description> [-- <agent prompt>]",
            file=sys.stderr,
        )
        print(
            '  Example: python3 start-task.py "fix login bug" -- "implement OAuth login flow"',
            file=sys.stderr,
        )
        sys.exit(1)

    description = " ".join(description_parts)
    prompt = " ".join(prompt_parts)

    # Set terminal tab title (works on most terminals across platforms)
    sys.stdout.write(f"\033]0;{description}\007")
    sys.stdout.flush()

    result = subprocess.run(
        [sys.executable, str(workspace_root / ".scripts" / "start_task.py"), description],
        capture_output=True,
        text=True,
    )

    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)

    if result.returncode != 0:
        sys.exit(result.returncode)

    symlink_path = None
    for line in result.stdout.splitlines():
        if line.startswith("SYMLINK_PATH="):
            symlink_path = line.split("=", 1)[1]

    if not symlink_path:
        print("Error: could not determine symlink path from start_task output", file=sys.stderr)
        sys.exit(1)

    config_path = workspace_root / ".agent-workspace" / "config.json"
    ide = "none"
    if config_path.is_file():
        with open(config_path, "r", encoding="utf-8") as f:
            ide = json.load(f).get("ide", "none")

    if ide == "vscode":
        print(f"\nOpening VS Code at {symlink_path}")
        subprocess.Popen(
            ["code", symlink_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    if prompt:
        print(f"Starting claude in {symlink_path}")
        print("When done, run: python3 ../end-task.py")
        print()
        subprocess.run(["claude", prompt], cwd=symlink_path)
    else:
        print("Workspace ready. When done, run: python3 ../end-task.py")


if __name__ == "__main__":
    main()
