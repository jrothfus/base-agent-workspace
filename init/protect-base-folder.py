#!/usr/bin/env python3
"""
Protect the base workspace folder from accidental deletion.

Cross-platform support:
  - macOS: Uses ACL (chmod +a "everyone deny delete")
  - Linux: Uses chattr +i (requires root), falls back to advisory message
  - Windows: Uses icacls to deny delete permission
"""
import platform
import subprocess
import sys
from pathlib import Path


def protect_macos(target_dir: Path) -> None:
    """Apply macOS ACL delete protection."""
    result = subprocess.run(
        ["ls", "-lde", str(target_dir)],
        capture_output=True,
        text=True,
    )
    if "everyone deny delete" in result.stdout:
        print(f"Protection already enabled on: {target_dir}")
        print(result.stdout.strip())
        return

    subprocess.run(
        ["chmod", "+a", "everyone deny delete", str(target_dir)],
        check=True,
    )
    print(f"Delete protection enabled on: {target_dir}")

    result = subprocess.run(
        ["ls", "-lde", str(target_dir)],
        capture_output=True,
        text=True,
    )
    print("Current ACLs:")
    print(result.stdout.strip())
    print()
    print("Note: Root/sudo can still remove this directory intentionally.")


def protect_linux(target_dir: Path) -> None:
    """Apply Linux immutable flag (requires root)."""
    result = subprocess.run(
        ["lsattr", "-d", str(target_dir)],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0 and "i" in result.stdout.split()[0]:
        print(f"Protection already enabled on: {target_dir}")
        return

    result = subprocess.run(
        ["chattr", "+i", str(target_dir)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"Warning: Could not set immutable flag on {target_dir}")
        print("         This requires root privileges (run with sudo).")
        print("         The workspace will still function without this protection.")
        return

    print(f"Delete protection enabled on: {target_dir}")
    print("Note: Root/sudo can still remove this directory intentionally.")


def protect_windows(target_dir: Path) -> None:
    """Apply Windows ACL delete protection using icacls."""
    result = subprocess.run(
        ["icacls", str(target_dir), "/deny", "Everyone:(D)"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"Warning: Could not set delete protection on {target_dir}")
        print("         You may need to run as Administrator.")
        print("         The workspace will still function without this protection.")
        return

    print(f"Delete protection enabled on: {target_dir}")
    print("Note: Administrator can still remove this directory intentionally.")


def main() -> None:
    if len(sys.argv) > 1:
        target_dir = Path(sys.argv[1])
    else:
        target_dir = Path(__file__).resolve().parent.parent

    if not target_dir.is_dir():
        print(f"Error: Target directory does not exist: {target_dir}", file=sys.stderr)
        sys.exit(1)

    system = platform.system()

    if system == "Darwin":
        protect_macos(target_dir)
    elif system == "Linux":
        protect_linux(target_dir)
    elif system == "Windows":
        protect_windows(target_dir)
    else:
        print(f"Warning: Unsupported platform '{system}' for folder protection.")
        print("         The workspace will still function without this protection.")


if __name__ == "__main__":
    main()
