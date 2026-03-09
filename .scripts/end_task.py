#!/usr/bin/env python3
"""
End a task by cleaning up the worktree and releasing the lock.
"""
import json
import subprocess
import sys
from pathlib import Path
from typing import Optional


class TaskEnderError(Exception):
    """Base exception for task ender errors."""
    pass


class TaskEnder:
    """Manages task workspace cleanup."""
    
    def __init__(self, workspace_root: Path, task_path: str):
        self.workspace_root = workspace_root
        self.task_path_str = task_path
        
        self.agent_workspace_dir = workspace_root / ".agent-workspace"
        self.config_path = self.agent_workspace_dir / "config.json"
        self.locks_dir = self.agent_workspace_dir / "locks"
        
        self.worktree_dir: Optional[Path] = None
        self.symlink_path: Optional[Path] = None
        self.lock_id: Optional[str] = None
        
    def validate_workspace(self) -> None:
        """Validate that workspace structure exists."""
        if not self.config_path.is_file():
            raise TaskEnderError(f"Missing config file at {self.config_path}")
    
    def load_config(self) -> str:
        """Load and validate configuration.
        
        Returns:
            The base branch name
        """
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        base_branch = config.get('base_branch')
        
        if not isinstance(base_branch, str) or not base_branch.strip():
            raise TaskEnderError('config base_branch must be a non-empty string')
        
        return base_branch.strip()
    
    def resolve_task_path(self) -> None:
        """Resolve the task path to a worktree directory.
        
        Sets self.worktree_dir, self.symlink_path, and self.lock_id
        """
        task_path = Path(self.task_path_str)
        
        # Check if it's a symlink
        if task_path.is_symlink():
            self.symlink_path = task_path
            self.worktree_dir = task_path.resolve()
        elif task_path.is_dir():
            self.symlink_path = None
            self.worktree_dir = task_path.resolve()
        else:
            raise TaskEnderError(
                f"{self.task_path_str} does not exist or is not a directory/symlink"
            )
        
        # Verify it's a git repository
        git_dir = self.worktree_dir / ".git"
        if not git_dir.is_dir():
            raise TaskEnderError(f"{self.worktree_dir} is not a git repository")
        
        # The lock ID is the basename of the worktree directory
        self.lock_id = self.worktree_dir.name
    
    def checkout_and_update(self, base_branch: str) -> None:
        """Checkout base branch and pull latest changes.
        
        Args:
            base_branch: The base branch to checkout
        """
        print(f"Checking out base branch: {base_branch}")
        subprocess.run(
            ["git", "-C", str(self.worktree_dir), "checkout", base_branch],
            check=True
        )
        
        print("Pulling latest changes...")
        subprocess.run(
            ["git", "-C", str(self.worktree_dir), "pull", "--ff-only", "origin", base_branch],
            check=True
        )
    
    def cleanup_worktree(self) -> None:
        """Clean up any leftover files in the worktree."""
        print("Cleaning up leftover files...")
        
        # Show status first
        subprocess.run(
            ["git", "-C", str(self.worktree_dir), "status"],
            check=True
        )
        
        # Reset to HEAD
        subprocess.run(
            ["git", "-C", str(self.worktree_dir), "reset", "--hard", "HEAD"],
            check=True
        )
        
        # Remove untracked files
        subprocess.run(
            ["git", "-C", str(self.worktree_dir), "clean", "-fd"],
            check=True
        )
    
    def remove_symlinks(self) -> None:
        """Remove symlinks pointing to this worktree."""
        # Remove the explicitly provided symlink if it exists
        if self.symlink_path and self.symlink_path.is_symlink():
            print(f"Removing symlink: {self.symlink_path}")
            self.symlink_path.unlink()
        
        # Scan workspace root for any other symlinks pointing to this worktree
        for item in self.workspace_root.iterdir():
            if item.is_symlink():
                try:
                    target = item.resolve()
                    if target == self.worktree_dir:
                        print(f"Removing symlink: {item}")
                        item.unlink()
                except (OSError, RuntimeError):
                    # Skip broken or circular symlinks
                    continue
    
    def release_lock(self) -> None:
        """Release the lock by deleting the lock folder."""
        lock_dir = self.locks_dir / self.lock_id
        
        if lock_dir.is_dir():
            print(f"Releasing lock: {lock_dir}")
            try:
                lock_dir.rmdir()
            except OSError as e:
                raise TaskEnderError(f"Failed to remove lock directory: {e}")
        else:
            print(f"Warning: Lock directory not found at {lock_dir} (already released?)")
    
    def end(self) -> None:
        """Main entry point to end a task."""
        # Validation
        self.validate_workspace()
        
        # Load configuration
        base_branch = self.load_config()
        
        # Resolve task path
        self.resolve_task_path()
        
        print(f"Ending task for worktree: {self.worktree_dir}")
        print(f"Lock ID: {self.lock_id}")
        
        # Checkout and update
        self.checkout_and_update(base_branch)
        
        # Clean up worktree
        self.cleanup_worktree()
        
        # Remove symlinks
        self.remove_symlinks()
        
        # Release lock
        self.release_lock()
        
        print(f"Task ended. Worktree {self.lock_id} is now available for reuse.")


def main() -> None:
    """Main entry point."""
    if len(sys.argv) < 2 or not sys.argv[1]:
        print("Usage: end_task.py <task-folder-or-symlink-path>", file=sys.stderr)
        sys.exit(1)
    
    task_path = sys.argv[1]
    
    script_dir = Path(__file__).parent.resolve()
    workspace_root = script_dir.parent
    
    ender = TaskEnder(workspace_root, task_path)
    
    try:
        ender.end()
    except TaskEnderError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}", file=sys.stderr)
        sys.exit(e.returncode)
    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
