#!/usr/bin/env bash
set -euo pipefail

MINIMUM_MAJOR=3

# Try to find a Python binary that is version 3+
find_python() {
  for cmd in python3 python; do
    if command -v "$cmd" &>/dev/null; then
      local version
      version=$("$cmd" --version 2>&1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
      local major
      major=$(echo "$version" | cut -d. -f1)
      if [[ "$major" -ge "$MINIMUM_MAJOR" ]]; then
        echo "$cmd $version"
        return 0
      fi
    fi
  done
  return 1
}

echo "Checking Python dependency..."

if result=$(find_python); then
  echo "OK: Found Python $result"
else
  echo "Error: Python ${MINIMUM_MAJOR}+ is required but was not found." >&2
  echo "       Checked: python3, python" >&2
  echo "       Install Python 3 from https://www.python.org/downloads/" >&2
  exit 1
fi
