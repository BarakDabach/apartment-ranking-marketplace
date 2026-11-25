#!/usr/bin/env sh
# Copies both skills into one or more agent skill directories (no plugin system required).
# Examples:
#   ./scripts/install-skills.sh claude
#   ./scripts/install-skills.sh claude copilot codex
#   ./scripts/install-skills.sh --path /work/my-project/.github/skills
set -eu
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
SRC="$SCRIPT_DIR/../plugins/apartment-ranking/skills"
SKILLS="apartment-ranking architectural-document-ingestion"
STAMP=$(date +%Y%m%d-%H%M%S)

usage() {
  echo "Usage: $0 [claude] [copilot] [codex] [all] [--path DIR ...]" >&2
  exit 1
}

TARGETS=""
add_target() { TARGETS="$TARGETS
$1"; }

[ $# -gt 0 ] || usage
while [ $# -gt 0 ]; do
  case "$1" in
    claude) add_target "$HOME/.claude/skills" ;;
    copilot) add_target "$HOME/.copilot/skills" ;;
    codex) add_target "$HOME/.agents/skills" ;;
    all)
      add_target "$HOME/.claude/skills"
      add_target "$HOME/.copilot/skills"
      add_target "$HOME/.agents/skills" ;;
    --path) [ $# -ge 2 ] || usage; add_target "$2"; shift ;;
    *) usage ;;
  esac
  shift
done

echo "$TARGETS" | while IFS= read -r TARGET; do
  [ -n "$TARGET" ] || continue
  mkdir -p "$TARGET"
  # Backups go next to the skills directory, not inside it, so agents do not load them as duplicate skills.
  BACKUP_ROOT="$(dirname "$TARGET")/skills-backup/$STAMP"
  for SKILL in $SKILLS; do
    if [ -e "$TARGET/$SKILL" ]; then
      mkdir -p "$BACKUP_ROOT"
      mv "$TARGET/$SKILL" "$BACKUP_ROOT/$SKILL"
      echo "Existing $TARGET/$SKILL backed up to $BACKUP_ROOT/$SKILL (check its criteria-bank.md for local additions)."
    fi
    cp -R "$SRC/$SKILL" "$TARGET/$SKILL"
  done
  echo "Installed apartment-ranking, architectural-document-ingestion into $TARGET"
done
echo "Start a new agent session so the skills are discovered."
