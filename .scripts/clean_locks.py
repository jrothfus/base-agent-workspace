#!/usr/bin/env python3
"""
Clean all locks from the agent workspace.

This script removes all lock directories to free up worktree IDs
that may have been left behind by interrupted or crashed tasks.
"""

import sys
from pathlib import Path
import shutil


class LockCleaner:
    """Clean all lock directories from the agent workspace."""

    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent.parent
        self.agent_workspace_dir = self.base_dir / ".agent-workspace"
        self.locks_dir = self.agent_workspace_dir / "locks"

    def validate_environment(self) -> None:
        """Validate that the locks directory exists."""
        if not self.locks_dir.is_dir():
            print(f"Error: Locks directory not found at {self.locks_dir}")
            sys.exit(1)

    def clean_locks(self) -> None:
        """Remove all lock directories."""
        if not self.locks_dir.is_dir():
            print("No locks directory found. Nothing to clean.")
            return

        lock_dirs = [
            d for d in self.locks_dir.iterdir()
            if d.is_dir() and not d.name.startswith(".")
        ]

        if not lock_dirs:
            print("No locks found. All clean!")
            return

        print(f"Found {len(lock_dirs)} lock(s) to remove:")
        for lock_dir in lock_dirs:
            print(f"  - {lock_dir.name}")

        print("\nRemoving locks...")
        removed_count = 0
        failed_count = 0

        for lock_dir in lock_dirs:
            try:
                # Remove directory (should be empty, but use rmtree for safety)
                if lock_dir.is_dir():
                    shutil.rmtree(lock_dir)
                    print(f"✓ Removed lock: {lock_dir.name}")
                    removed_count += 1
            except Exception as e:
                print(f"✗ Failed to remove {lock_dir.name}: {e}")
                failed_count += 1

        print(f"\n{'='*50}")
        print(f"Summary:")
        print(f"  Removed: {removed_count}")
        if failed_count > 0:
            print(f"  Failed:  {failed_count}")
        print(f"{'='*50}")

        if failed_count > 0:
            sys.exit(1)

    def run(self) -> None:
        """Run the lock cleaning process."""
        try:
            print("Agent Workspace Lock Cleaner")
            print("="*50)
            self.validate_environment()
            self.clean_locks()
            print("\n✓ Lock cleaning completed successfully!")
        except KeyboardInterrupt:
            print("\n\nCleaning interrupted by user.")
            sys.exit(130)
        except Exception as e:
            print(f"\n✗ Error: {e}")
            sys.exit(1)


def main():
    """Main entry point."""
    cleaner = LockCleaner()
    cleaner.run()


if __name__ == "__main__":
    main()
