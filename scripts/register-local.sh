#!/usr/bin/env sh
set -eu
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
REPO_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)

if ! command -v codex >/dev/null 2>&1; then
  echo "Codex CLI was not found in PATH. Install/enable Codex CLI, then rerun this script." >&2
  exit 1
fi

echo "Registering Apartment Ranking marketplace from: $REPO_ROOT"
codex plugin marketplace add "$REPO_ROOT"
echo
echo "Marketplace registered."
echo "Restart ChatGPT desktop / Codex, open the Plugin Directory, select 'Apartment Ranking Tools', and install 'Apartment Ranking'."
