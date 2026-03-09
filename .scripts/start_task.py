#!/usr/bin/env python3
"""
Start a new task by setting up an isolated worktree with a unique lock ID.
"""
import json
import os
import re
import secrets
import shutil
import string
import subprocess
import sys
from pathlib import Path
from typing import List, Optional


class TaskStarterError(Exception):
    """Base exception for task starter errors."""
    pass


class TaskStarter:
    """Manages task workspace initialization."""
    
    def __init__(self, workspace_root: Path, task_short_name: str):
        self.workspace_root = workspace_root
        self.task_short_name = task_short_name
        
        self.agent_workspace_dir = workspace_root / ".agent-workspace"
        self.config_path = self.agent_workspace_dir / "config.json"
        self.worktree_ids_path = self.agent_workspace_dir / "worktree-ids.json"
        self.start_task_commands_path = self.agent_workspace_dir / "start-task-commands.json"
        self.locks_dir = self.agent_workspace_dir / "locks"
        self.worktrees_dir = self.agent_workspace_dir / "worktrees"
        self.base_repo_dir = self.agent_workspace_dir / "base-repo"
        
        self.lock_id: Optional[str] = None
        self.lock_dir: Optional[Path] = None
        self.keep_lock = False
        
    def validate_workspace(self) -> None:
        """Validate that workspace structure exists."""
        if not self.agent_workspace_dir.is_dir():
            raise TaskStarterError(
                f"Missing .agent-workspace directory at {self.agent_workspace_dir}"
            )
        
        if not self.config_path.is_file():
            raise TaskStarterError(f"Missing config file at {self.config_path}")
        
        if not self.worktree_ids_path.is_file():
            raise TaskStarterError(
                f"Missing worktree ids file at {self.worktree_ids_path}"
            )
        
        # Create required directories
        self.locks_dir.mkdir(parents=True, exist_ok=True)
        self.worktrees_dir.mkdir(parents=True, exist_ok=True)
    
    def load_config(self) -> tuple[str, str]:
        """Load and validate configuration.
        
        Returns:
            Tuple of (repo_url, base_branch)
        """
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        repo = config.get('repo', {})
        repo_url = repo.get('url')
        base_branch = config.get('base_branch')
        
        if not isinstance(repo_url, str) or not repo_url.strip():
            raise TaskStarterError('config repo.url must be a non-empty string')
        
        if not isinstance(base_branch, str) or not base_branch.strip():
            raise TaskStarterError('config base_branch must be a non-empty string')
        
        return repo_url.strip(), base_branch.strip()
    
    def load_preset_ids(self) -> List[str]:
        """Load preset worktree IDs from JSON file."""
        with open(self.worktree_ids_path, 'r', encoding='utf-8') as f:
            ids = json.load(f)
        
        if not isinstance(ids, list):
            raise TaskStarterError('worktree-ids.json must contain a JSON array')
        
        return [
            item.strip()
            for item in ids
            if isinstance(item, str) and item.strip()
        ]
    
    @staticmethod
    def normalize_task_name(raw_name: str) -> str:
        """Normalize task name to lowercase alphanumeric with hyphens."""
        # Convert to lowercase and replace non-alphanumeric with hyphens
        normalized = re.sub(r'[^a-z0-9]+', '-', raw_name.lower())
        # Remove leading/trailing hyphens and collapse multiple hyphens
        normalized = re.sub(r'^-+|-+$', '', normalized)
        normalized = re.sub(r'-+', '-', normalized)
        
        if not normalized:
            normalized = "task"
        
        # Limit to 64 characters
        return normalized[:64]
    
    @staticmethod
    def generate_temp_id() -> str:
        """Generate a random 12-character ID."""
        alphabet = string.ascii_lowercase + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(12))
    
    def acquire_lock(self, preset_ids: List[str]) -> str:
        """Acquire a lock by finding an available ID.
        
        Args:
            preset_ids: List of preset IDs to try first
            
        Returns:
            The acquired lock ID
        """
        # Try preset IDs first
        for candidate_id in preset_ids:
            lock_path = self.locks_dir / candidate_id
            try:
                lock_path.mkdir(parents=False, exist_ok=False)
                return candidate_id
            except FileExistsError:
                continue
        
        # Generate random IDs until we find an available one
        while True:
            candidate_id = self.generate_temp_id()
            lock_path = self.locks_dir / candidate_id
            try:
                lock_path.mkdir(parents=False, exist_ok=False)
                return candidate_id
            except FileExistsError:
                continue
    
    def cleanup_lock(self) -> None:
        """Clean up lock directory on exit if keep_lock is False."""
        if not self.keep_lock and self.lock_dir and self.lock_dir.is_dir():
            try:
                self.lock_dir.rmdir()
            except OSError:
                pass
    
    def setup_base_repo(self, repo_url: str, base_branch: str) -> None:
        """Clone or update the base repository."""
        git_dir = self.base_repo_dir / ".git"
        
        if not git_dir.is_dir():
            print(f"Cloning {repo_url}...")
            subprocess.run(
                ["git", "clone", repo_url, str(self.base_repo_dir)],
                check=True
            )
        
        print(f"Updating base repository to {base_branch}...")
        subprocess.run(
            ["git", "-C", str(self.base_repo_dir), "fetch", "origin"],
            check=True
        )
        subprocess.run(
            ["git", "-C", str(self.base_repo_dir), "checkout", base_branch],
            check=True
        )
        subprocess.run(
            ["git", "-C", str(self.base_repo_dir), "pull", "--ff-only", "origin", base_branch],
            check=True
        )
    
    def setup_worktree(self, base_branch: str) -> Path:
        """Create or update worktree for this task.
        
        Args:
            base_branch: The base branch to checkout
            
        Returns:
            Path to the worktree directory
        """
        worktree_dir = self.worktrees_dir / self.lock_id
        git_dir = worktree_dir / ".git"
        
        if not git_dir.is_dir():
            if worktree_dir.exists():
                raise TaskStarterError(
                    f"{worktree_dir} exists but is not a git repository"
                )
            
            print(f"Creating worktree {self.lock_id}...")
            shutil.copytree(self.base_repo_dir, worktree_dir)
        
        print(f"Updating worktree to {base_branch}...")
        subprocess.run(
            ["git", "-C", str(worktree_dir), "fetch", "origin"],
            check=True
        )
        subprocess.run(
            ["git", "-C", str(worktree_dir), "checkout", base_branch],
            check=True
        )
        subprocess.run(
            ["git", "-C", str(worktree_dir), "pull", "--ff-only", "origin", base_branch],
            check=True
        )
        
        return worktree_dir
    
    def run_startup_commands(self, worktree_dir: Path) -> None:
        """Run startup commands from configuration if they exist."""
        if not self.start_task_commands_path.is_file():
            return
        
        with open(self.start_task_commands_path, 'r', encoding='utf-8') as f:
            payload = json.load(f)
        
        commands = payload.get('commands', [])
        if not isinstance(commands, list):
            raise TaskStarterError(
                'start-task-commands.json commands must be an array'
            )
        
        for command in commands:
            if not isinstance(command, dict):
                continue
            
            if command.get('enabled') is not True:
                continue
            
            name = command.get('name', 'Unnamed command')
            run_value = command.get('run')
            continue_on_error = bool(command.get('continue_on_error', False))
            
            if not isinstance(run_value, str) or not run_value.strip():
                print(f"Skipping invalid command entry: {name}")
                continue
            
            print(f"Running startup command: {name}")
            result = subprocess.run(
                run_value,
                shell=True,
                cwd=worktree_dir
            )
            
            if result.returncode != 0:
                print(
                    f"Startup command failed ({result.returncode}): {name}",
                    file=sys.stderr
                )
                if not continue_on_error:
                    sys.exit(result.returncode)
    
    def create_symlink(self, worktree_dir: Path) -> Path:
        """Create a symlink to the worktree directory.
        
        Args:
            worktree_dir: Path to the worktree
            
        Returns:
            Path to the created symlink
        """
        safe_task_name = self.normalize_task_name(self.task_short_name)
        symlink_path = self.workspace_root / safe_task_name
        
        # If symlink path exists, append lock ID to make it unique
        if symlink_path.exists() or symlink_path.is_symlink():
            symlink_path = self.workspace_root / f"{safe_task_name}-{self.lock_id}"
        
        symlink_path.symlink_to(worktree_dir)
        return symlink_path
    
    def start(self) -> None:
        """Main entry point to start a task."""
        try:
            # Validation
            self.validate_workspace()
            
            # Load configuration
            repo_url, base_branch = self.load_config()
            preset_ids = self.load_preset_ids()
            
            # Acquire lock
            self.lock_id = self.acquire_lock(preset_ids)
            self.lock_dir = self.locks_dir / self.lock_id
            
            # Setup repositories
            self.setup_base_repo(repo_url, base_branch)
            worktree_dir = self.setup_worktree(base_branch)
            
            # Run startup commands
            self.run_startup_commands(worktree_dir)
            
            # Create symlink
            symlink_path = self.create_symlink(worktree_dir)
            
            # Keep the lock
            self.keep_lock = True
            
            # Print success information
            print("\nTask workspace is ready")
            print(f"Lock ID: {self.lock_id}")
            print(f"Worktree: {worktree_dir}")
            print(f"Shortcut: {symlink_path}")
            
            # Open VS Code at the symlink path (user-friendly name)
            print(f"\nOpening VS Code at {symlink_path}")
            subprocess.run(
                ["code", str(symlink_path)],
                check=False  # Don't fail if VS Code isn't installed
            )
            
        except Exception:
            self.cleanup_lock()
            raise


def main() -> None:
    """Main entry point."""
    if len(sys.argv) < 2 or not sys.argv[1]:
        print("Usage: start_task.py <short-task-name>", file=sys.stderr)
        sys.exit(1)
    
    task_short_name = sys.argv[1]
    
    script_dir = Path(__file__).parent.resolve()
    workspace_root = script_dir.parent
    
    starter = TaskStarter(workspace_root, task_short_name)
    
    try:
        starter.start()
    except TaskStarterError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}", file=sys.stderr)
        sys.exit(e.returncode)
    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        starter.cleanup_lock()
        sys.exit(130)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        starter.cleanup_lock()
        sys.exit(1)


if __name__ == "__main__":
    main()
