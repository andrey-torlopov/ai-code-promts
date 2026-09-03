#!/usr/bin/env bash
# Install this Home template into a Codex home directory.
#
#   ./init_codex.sh
#   ./init_codex.sh --target DIR
#   ./init_codex.sh --user-skills-dir DIR
#   ./init_codex.sh --no-skill-links
#   ./init_codex.sh --dry-run
#   ./init_codex.sh --no-backup
#
# Payload -> destination:
#   AGENTS.md -> <target>/AGENTS.md
#   hooks.json -> <target>/hooks.json                (merge managed entry)
#   hooks/*.sh -> <target>/hooks/<name>.sh           (only shipped hooks)
#   custom/   -> <target>/custom/                   (replaced wholesale)
#   skills/   -> <target>/skills/<name>/            (only shipped skills)
#   links     -> <user-skills-dir>/<name>            (one symlink per shipped skill)
#
# Default target: ${CODEX_HOME:-$HOME/.codex}
# Default user skill discovery: ${CODEX_USER_SKILLS_DIR:-$HOME/.agents/skills}
#
# Existing hooks.json entries not managed by Codex2Home are preserved. Codex state not
# listed above is left untouched, including config.toml, auth.json, history, sessions,
# plugins, caches, logs and any skill not shipped by this template.

set -euo pipefail

: "${HOME:?HOME must be set}"

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="${CODEX_HOME:-$HOME/.codex}"
USER_SKILLS_DIR="${CODEX_USER_SKILLS_DIR:-$HOME/.agents/skills}"
DRY_RUN=0
BACKUP=1
LINK_SKILLS=1

usage() {
  sed -n '2,24p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
}

die() {
  printf 'error: %s\n' "$*" >&2
  exit 2
}

require_value() {
  [ "$#" -ge 2 ] && [ -n "$2" ] || die "$1 requires a non-empty directory"
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --target)
      require_value "$@"
      TARGET="$2"
      shift 2
      ;;
    --target=*)
      TARGET="${1#*=}"
      [ -n "$TARGET" ] || die "--target requires a non-empty directory"
      shift
      ;;
    --user-skills-dir)
      require_value "$@"
      USER_SKILLS_DIR="$2"
      shift 2
      ;;
    --user-skills-dir=*)
      USER_SKILLS_DIR="${1#*=}"
      [ -n "$USER_SKILLS_DIR" ] || die "--user-skills-dir requires a non-empty directory"
      shift
      ;;
    --no-skill-links)
      LINK_SKILLS=0
      shift
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --no-backup)
      BACKUP=0
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      die "unknown option: $1"
      ;;
  esac
done

case "$TARGET" in
  ""|/|.|..)
    die "unsafe target: $TARGET"
    ;;
esac

case "$USER_SKILLS_DIR" in
  ""|/|.|..)
    die "unsafe user skills directory: $USER_SKILLS_DIR"
    ;;
esac

[ -f "$SRC/AGENTS.md" ] || die "not a Codex Home template: missing $SRC/AGENTS.md"
[ -f "$SRC/custom/CORE.md" ] || die "not a Codex Home template: missing $SRC/custom/CORE.md"
[ -f "$SRC/custom/RESOLVER.md" ] || die "not a Codex Home template: missing $SRC/custom/RESOLVER.md"
[ -f "$SRC/hooks.json" ] || die "not a Codex Home template: missing $SRC/hooks.json"
[ -f "$SRC/hooks/project-context.sh" ] || \
  die "not a Codex Home template: missing project-context hook"
[ -f "$SRC/hooks/rules-context.sh" ] || \
  die "not a Codex Home template: missing rules-context hook"
[ -f "$SRC/hooks/route-guard.sh" ] || \
  die "not a Codex Home template: missing route-guard hook"
[ -f "$SRC/scripts/merge_hooks.py" ] || \
  die "not a Codex Home template: missing hooks merger"
[ -f "$SRC/skills/skill-maintenance/scripts/validate-system.sh" ] || \
  die "not a Codex Home template: missing validator"

PYTHON_BIN="$(command -v python3 || true)"
[ -n "$PYTHON_BIN" ] || die "python3 is required to merge hooks.json safely"

STAMP="$(date +%Y%m%d-%H%M%S)-$$"

say() {
  printf '%s\n' "$*"
}

run() {
  if [ "$DRY_RUN" -eq 1 ]; then
    say "  would: $*"
  else
    "$@"
  fi
}

path_exists() {
  [ -e "$1" ] || [ -L "$1" ]
}

backup_as() {
  local path="$1" label="$2"
  path_exists "$path" || return 0
  [ "$BACKUP" -eq 1 ] || return 0
  run mkdir -p "$BACKUP_DIR/$(dirname "$label")"
  run cp -a "$path" "$BACKUP_DIR/$label"
  say "  backed up: $label"
}

remove_exact_path() {
  local path="$1"
  path_exists "$path" || return 0

  if [ -L "$path" ] || [ -f "$path" ]; then
    run unlink "$path"
  elif [ -d "$path" ]; then
    if [ "$DRY_RUN" -eq 1 ]; then
      say "  would: delete exact directory $path"
    else
      find "$path" -depth -delete
    fi
  else
    die "refusing to replace unsupported filesystem entry: $path"
  fi
}

install_directory() {
  local source="$1" destination="$2" label="$3"
  backup_as "$destination" "$label"
  remove_exact_path "$destination"
  run mkdir -p "$destination"
  run cp -a "$source/." "$destination/"
  say "installed: $label"
}

say "source:           $SRC"
say "Codex home:       $TARGET"
if [ "$LINK_SKILLS" -eq 1 ]; then
  say "user skills:      $USER_SKILLS_DIR"
else
  say "user skill links: disabled"
fi
[ "$DRY_RUN" -eq 1 ] && say "mode:             dry-run"

run mkdir -p "$TARGET"
if [ "$DRY_RUN" -eq 0 ]; then
  TARGET="$(cd "$TARGET" && pwd -P)"
fi
BACKUP_DIR="$TARGET/backups/codex2home-$STAMP"

for owned_dir in "$TARGET/skills" "$TARGET/hooks"; do
  if [ -L "$owned_dir" ]; then
    die "refusing to write through symlink: $owned_dir"
  fi
  if [ -e "$owned_dir" ] && [ ! -d "$owned_dir" ]; then
    die "expected a directory: $owned_dir"
  fi
done
if [ -L "$TARGET/hooks.json" ]; then
  die "refusing to replace symlink: $TARGET/hooks.json"
fi
if [ -e "$TARGET/hooks.json" ] && [ ! -f "$TARGET/hooks.json" ]; then
  die "expected a regular file: $TARGET/hooks.json"
fi
"$PYTHON_BIN" "$SRC/scripts/merge_hooks.py" --check "$SRC/hooks.json" "$TARGET/hooks.json"
if [ -s "$TARGET/AGENTS.override.md" ]; then
  say "warning: $TARGET/AGENTS.override.md will shadow the installed AGENTS.md" >&2
fi

backup_as "$TARGET/AGENTS.md" "AGENTS.md"
remove_exact_path "$TARGET/AGENTS.md"
run cp -a "$SRC/AGENTS.md" "$TARGET/AGENTS.md"
say "installed: AGENTS.md"

install_directory "$SRC/custom" "$TARGET/custom" "custom"

run mkdir -p "$TARGET/hooks"
for hook_file in "$SRC"/hooks/*.sh; do
  hook_name="$(basename "$hook_file")"
  backup_as "$TARGET/hooks/$hook_name" "hooks/$hook_name"
  remove_exact_path "$TARGET/hooks/$hook_name"
  run cp -a "$hook_file" "$TARGET/hooks/$hook_name"
  run chmod +x "$TARGET/hooks/$hook_name"
  say "installed: hooks/$hook_name"
done

backup_as "$TARGET/hooks.json" "hooks.json"
if [ "$DRY_RUN" -eq 1 ]; then
  say "  would: merge Codex2Home-managed entries into $TARGET/hooks.json"
else
  "$PYTHON_BIN" "$SRC/scripts/merge_hooks.py" "$SRC/hooks.json" "$TARGET/hooks.json"
fi
say "installed: hooks.json (managed entries merged)"

run mkdir -p "$TARGET/skills"

for source_dir in "$SRC"/skills/*/; do
  skill_name="$(basename "$source_dir")"
  install_directory "$source_dir" "$TARGET/skills/$skill_name" "skills/$skill_name"
done

if [ "$LINK_SKILLS" -eq 1 ]; then
  run mkdir -p "$USER_SKILLS_DIR"

  if [ "$DRY_RUN" -eq 0 ]; then
    USER_SKILLS_DIR="$(cd "$USER_SKILLS_DIR" && pwd -P)"
  fi

  if [ "$USER_SKILLS_DIR" = "$TARGET/skills" ]; then
    say "skill links: skipped; discovery directory is the canonical skills directory"
  else
    for source_dir in "$SRC"/skills/*/; do
      skill_name="$(basename "$source_dir")"
      link_path="$USER_SKILLS_DIR/$skill_name"
      link_target="$TARGET/skills/$skill_name"

      if [ -L "$link_path" ] && [ "$(readlink "$link_path")" = "$link_target" ]; then
        say "linked:    $link_path (already correct)"
        continue
      fi

      backup_as "$link_path" "user-skills/$skill_name"
      remove_exact_path "$link_path"
      run ln -s "$link_target" "$link_path"
      say "linked:    $link_path -> $link_target"
    done
  fi
fi

if [ "$DRY_RUN" -eq 0 ]; then
  say ""
  if CODEX_HOME="$TARGET" sh "$TARGET/skills/skill-maintenance/scripts/validate-system.sh" "$TARGET"; then
    say "validation: ok"
  else
    say "validation: FAILED (see findings above)" >&2
    exit 1
  fi

  if [ "$BACKUP" -eq 1 ] && [ -d "$BACKUP_DIR" ]; then
    say "backup:     $BACKUP_DIR"
  fi
fi

say "done"
