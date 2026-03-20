#!/usr/bin/env python3
"""Clean all locks from the agent workspace."""
import subprocess
import sys
from pathlib import Path


def main() -> None:
    script_dir = Path(__file__).resolve().parent
    clean_locks_script = script_dir / ".scripts" / "clean_locks.py"

    result = subprocess.run(
        [sys.executable, str(clean_locks_script)] + sys.argv[1:],
    )
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
