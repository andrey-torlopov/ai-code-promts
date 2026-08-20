#!/bin/sh
# Stop hook: every active skill must still require SKILL CONTEXT and TRACE.
#
# Runs only where an instruction system can actually be edited:
#   1. a session rooted inside ~/.claude
#   2. a project that opted in (CORE.md in its root)
#   3. the Home template source tree (Home/custom/CORE.md under the project root)
# Otherwise it exits 0 without scanning anything.

set -eu

PROJECT_DIR="${1:-${CLAUDE_PROJECT_DIR:-}}"
CLAUDE_HOME="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
REGISTRY_DEFAULT="$CLAUDE_HOME/custom/_core/active-skills.txt"
FAILED=0
PAIRS=""

case "$PROJECT_DIR" in
  "$CLAUDE_HOME"|"$CLAUDE_HOME"/*) PAIRS="$CLAUDE_HOME/skills|$REGISTRY_DEFAULT" ;;
esac

if [ -n "$PROJECT_DIR" ] && [ -f "$PROJECT_DIR/CORE.md" ]; then
  for dir in SKILLS skills; do
    [ -d "$PROJECT_DIR/$dir" ] && PAIRS="$PAIRS $PROJECT_DIR/$dir|$PROJECT_DIR/_core/active-skills.txt"
  done
fi

for tpl in "$PROJECT_DIR/Home" "$PROJECT_DIR/../Home"; do
  [ -n "$PROJECT_DIR" ] || continue
  [ -f "$tpl/custom/CORE.md" ] || continue
  PAIRS="$PAIRS $tpl/skills|$tpl/custom/_core/active-skills.txt"
done

[ -n "$PAIRS" ] || exit 0

for pair in $PAIRS; do
  root="${pair%%|*}"
  registry="${pair#*|}"
  [ -d "$root" ] || continue
  for skill in "$root"/*/SKILL.md; do
    [ -f "$skill" ] || continue
    name="$(basename "$(dirname "$skill")")"
    if [ -f "$registry" ]; then
      grep -v '^#' "$registry" | grep -qx "$name" || continue
    fi
    grep -q 'SKILL CONTEXT' "$skill" || {
      echo "CRITICAL ${skill}: missing SKILL CONTEXT requirement"; FAILED=1; }
    grep -q 'TRACE' "$skill" || {
      echo "CRITICAL ${skill}: missing final TRACE requirement"; FAILED=1; }
  done
done

exit "$FAILED"
