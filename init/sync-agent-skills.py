#!/usr/bin/env python3
"""
Sync agent skills by creating symlinks from .agent_skills to each
agent config directory (.claude, .codex, .openclaw).
"""
import sys
from pathlib import Path

TARGET_DIR_NAMES = [".claude", ".codex", ".openclaw"]


def main() -> None:
    if len(sys.argv) > 1:
        workspace_root = Path(sys.argv[1])
    else:
        workspace_root = Path(__file__).resolve().parent.parent

    source_dir = workspace_root / ".agent_skills"

    if not source_dir.is_dir():
        print(f"Skipping skill sync: source directory not found at {source_dir}")
        return

    for dir_name in TARGET_DIR_NAMES:
        target_dir = workspace_root / dir_name
        target_dir.mkdir(parents=True, exist_ok=True)

        link_path = target_dir / "skills"

        if link_path.is_symlink() or link_path.exists():
            if link_path.is_dir() and not link_path.is_symlink():
                import shutil
                shutil.rmtree(link_path)
            else:
                link_path.unlink()

        link_path.symlink_to(source_dir)
        print(f"Linked skills: {link_path} -> {source_dir}")


if __name__ == "__main__":
    main()
