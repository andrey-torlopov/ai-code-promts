#!/usr/bin/env bash
# Install this Home template into a Claude Code home directory.
#
#   ./init_claude.sh                 # install into ~/.claude
#   ./init_claude.sh --target DIR    # install into DIR (used for testing)
#   ./init_claude.sh --dry-run       # show what would change, touch nothing
#   ./init_claude.sh --no-backup     # skip the backup of replaced files
#
# Payload -> destination:
#   CLAUDE.md      -> <target>/CLAUDE.md
#   settings.json  -> <target>/settings.json
#   hooks/         -> <target>/hooks/
#   skills/        -> <target>/skills/          (only the skills shipped here)
#   custom/        -> <target>/custom/          (replaced wholesale)
#
# settings.json carries {{HOME}} placeholders so the template stays portable; they are
# substituted with the real $HOME right after the copy.
#
# Anything already in <target> and not listed above is left untouched:
# projects/, sessions/, history.jsonl, plugins/, and any skill not shipped here.

set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
DRY_RUN=0
BACKUP=1

while [ $# -gt 0 ]; do
  case "$1" in
    --target) TARGET="$2"; shift 2 ;;
    --target=*) TARGET="${1#*=}"; shift ;;
    --dry-run) DRY_RUN=1; shift ;;
    --no-backup) BACKUP=0; shift ;;
    -h|--help) sed -n '2,20p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
done

STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_DIR="$TARGET/backups/home-template-$STAMP"

say() { printf '%s\n' "$*"; }
run() { if [ "$DRY_RUN" -eq 1 ]; then say "  would: $*"; else "$@"; fi; }

[ -f "$SRC/custom/CORE.md" ] || { echo "not a Home template directory: $SRC" >&2; exit 1; }

say "source: $SRC"
say "target: $TARGET"
[ "$DRY_RUN" -eq 1 ] && say "mode:   dry-run"

run mkdir -p "$TARGET"

backup() {
  local path="$1" rel="${1#"$TARGET"/}"
  [ -e "$path" ] || return 0
  [ "$BACKUP" -eq 1 ] || return 0
  run mkdir -p "$BACKUP_DIR/$(dirname "$rel")"
  run cp -a "$path" "$BACKUP_DIR/$rel"
  say "  backed up: $rel"
}

# --- single files -----------------------------------------------------------
case "$HOME" in
  *"|"*) echo "HOME contains '|', cannot substitute placeholders safely: $HOME" >&2; exit 1 ;;
esac

substitute_home() {
  file="$1"
  if [ "$DRY_RUN" -eq 1 ]; then
    say "  would: substitute {{HOME}} -> $HOME in ${file#"$TARGET"/}"
    return 0
  fi
  grep -q '{{HOME}}' "$file" || return 0
  sed "s|{{HOME}}|$HOME|g" "$file" > "$file.tmp.$$"
  mv "$file.tmp.$$" "$file"
  if grep -q '{{HOME}}' "$file"; then
    echo "placeholder substitution failed in $file" >&2
    exit 1
  fi
  say "  resolved:  {{HOME}} -> $HOME"
}

for f in CLAUDE.md settings.json; do
  backup "$TARGET/$f"
  run cp -a "$SRC/$f" "$TARGET/$f"
  substitute_home "$TARGET/$f"
  say "installed: $f"
done

# --- hooks ------------------------------------------------------------------
run mkdir -p "$TARGET/hooks"
for hook in "$SRC"/hooks/*.sh; do
  name="$(basename "$hook")"
  backup "$TARGET/hooks/$name"
  run cp -a "$hook" "$TARGET/hooks/$name"
  run chmod +x "$TARGET/hooks/$name"
  say "installed: hooks/$name"
done

# --- custom/ (wholesale replace) --------------------------------------------
backup "$TARGET/custom"
if [ "$DRY_RUN" -eq 0 ] && [ -d "$TARGET/custom" ]; then
  find "$TARGET/custom" -mindepth 1 -delete
fi
run mkdir -p "$TARGET/custom"
run cp -a "$SRC/custom/." "$TARGET/custom/"
say "installed: custom/"

# --- skills (only the ones shipped here) ------------------------------------
run mkdir -p "$TARGET/skills"
for dir in "$SRC"/skills/*/; do
  name="$(basename "$dir")"
  backup "$TARGET/skills/$name"
  if [ "$DRY_RUN" -eq 0 ] && [ -d "$TARGET/skills/$name" ]; then
    find "$TARGET/skills/$name" -mindepth 1 -delete
  fi
  run mkdir -p "$TARGET/skills/$name"
  run cp -a "$dir." "$TARGET/skills/$name/"
  say "installed: skills/$name"
done

# --- validation -------------------------------------------------------------
if [ "$DRY_RUN" -eq 0 ]; then
  say ""
  if sh "$TARGET/skills/skill-maintenance/scripts/validate-system.sh" "$TARGET"; then
    say "validation: ok"
  else
    say "validation: FAILED (see findings above)"
    exit 1
  fi
  [ "$BACKUP" -eq 1 ] && [ -d "$BACKUP_DIR" ] && say "backup:     $BACKUP_DIR"
fi

say "done"
