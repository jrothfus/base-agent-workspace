#!/usr/bin/env python3
"""
Initialize the workspace: prompt for repo details, clone/update the base repo,
and run all init/*.py scripts.
"""
import json
import subprocess
import sys
from pathlib import Path


def prompt_with_default(label: str, default: str = "") -> str:
    while True:
        if default:
            value = input(f"{label} [{default}]: ").strip() or default
        else:
            value = input(f"{label}: ").strip()

        if value:
            return value
        print("Value is required. Please try again.")


def load_current_config(config_path: Path) -> tuple[str, str, str]:
    if not config_path.is_file():
        return "", "", ""

    with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    repo = data.get("repo") or {}
    return (
        repo.get("name", ""),
        repo.get("url", ""),
        data.get("base_branch", ""),
    )


def save_config(
    config_path: Path, repo_name: str, repo_url: str, base_branch: str
) -> None:
    config: dict = {}
    if config_path.is_file():
        with open(config_path, "r", encoding="utf-8") as f:
            existing = json.load(f)
        if isinstance(existing, dict):
            config = existing

    raw_repo = config.get("repo")
    repo: dict = raw_repo if isinstance(raw_repo, dict) else {}
    repo["name"] = repo_name
    repo["url"] = repo_url
    config["repo"] = repo
    config["base_branch"] = base_branch

    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)
        f.write("\n")


def run_init_scripts(init_dir: Path, workspace_root: Path, own_path: Path) -> None:
    scripts = sorted(init_dir.glob("*.py"))
    ran_any = False

    for script in scripts:
        full_path = script.resolve()
        if full_path == own_path:
            continue

        ran_any = True
        print(f"Running init script: {script.name}")
        result = subprocess.run(
            [sys.executable, str(full_path), str(workspace_root)],
        )
        if result.returncode != 0:
            print(f"Warning: {script.name} exited with code {result.returncode}", file=sys.stderr)

    if not ran_any:
        print(f"No init scripts found in: {init_dir}")


def main() -> None:
    workspace_root = Path(__file__).resolve().parent
    config_path = workspace_root / ".agent-workspace" / "config.json"
    agent_workspace_dir = workspace_root / ".agent-workspace"
    base_repo_dir = agent_workspace_dir / "base-repo"
    init_dir = workspace_root / "init"

    if not agent_workspace_dir.is_dir():
        print(f"Error: .agent-workspace directory not found at: {agent_workspace_dir}", file=sys.stderr)
        sys.exit(1)

    if not init_dir.is_dir():
        print(f"Error: init directory not found at: {init_dir}", file=sys.stderr)
        sys.exit(1)

    current_name, current_url, current_branch = load_current_config(config_path)

    print("Workspace init")
    print("--------------")

    repo_name = prompt_with_default("Repo name", current_name)
    repo_url = prompt_with_default("Repo URL", current_url)
    base_branch = prompt_with_default("Base branch", current_branch)

    save_config(config_path, repo_name, repo_url, base_branch)
    print(f"Updated config: {config_path}")

    print("Initializing superpowers submodule...")
    subprocess.run(
        ["git", "-C", str(workspace_root), "submodule", "update", "--init", "--recursive"],
        check=True,
    )

    if not (base_repo_dir / ".git").is_dir():
        if base_repo_dir.exists():
            print(f"Error: {base_repo_dir} exists but is not a git repository", file=sys.stderr)
            sys.exit(1)

        print(f"Cloning repo into {base_repo_dir}")
        subprocess.run(["git", "clone", repo_url, str(base_repo_dir)], check=True)

    subprocess.run(
        ["git", "-C", str(base_repo_dir), "remote", "set-url", "origin", repo_url],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(base_repo_dir), "fetch", "origin"],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(base_repo_dir), "checkout", base_branch],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(base_repo_dir), "pull", "--ff-only", "origin", base_branch],
        check=True,
    )
    print(f"Base repo synced at {base_repo_dir}")

    run_init_scripts(init_dir, workspace_root, Path(__file__).resolve())

    print("Workspace initialization complete.")


if __name__ == "__main__":
    main()
