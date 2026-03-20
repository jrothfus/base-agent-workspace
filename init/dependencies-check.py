#!/usr/bin/env python3
"""
Check that Python 3+ is available and report its version.

When this script runs successfully, Python 3 is guaranteed to be present
(because this script itself requires it).
"""
import platform
import sys

MINIMUM_MAJOR = 3


def main() -> None:
    print("Checking Python dependency...")

    major, minor, patch = sys.version_info[:3]

    if major < MINIMUM_MAJOR:
        print(
            f"Error: Python {MINIMUM_MAJOR}+ is required but found {major}.{minor}.{patch}.",
            file=sys.stderr,
        )
        print(
            "       Install Python 3 from https://www.python.org/downloads/",
            file=sys.stderr,
        )
        sys.exit(1)

    executable = sys.executable or "python"
    print(f"OK: Found Python {major}.{minor}.{patch} ({executable})")
    print(f"    Platform: {platform.system()} {platform.machine()}")


if __name__ == "__main__":
    main()
