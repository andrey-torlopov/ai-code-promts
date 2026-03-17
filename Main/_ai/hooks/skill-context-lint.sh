#!/bin/sh
# Fast check for substantial response templates in active skills.

set -eu

ROOT="${1:-.}"
FAILED=0

for skill in "$ROOT"/SKILLS/*/SKILL.md; do
  [ -f "$skill" ] || continue
  if ! grep -q 'SKILL CONTEXT' "$skill"; then
    echo "CRITICAL ${skill#"$ROOT"/}: missing SKILL CONTEXT requirement"
    FAILED=1
  fi
  if ! grep -q 'TRACE' "$skill"; then
    echo "CRITICAL ${skill#"$ROOT"/}: missing final TRACE requirement"
    FAILED=1
  fi
done

exit "$FAILED"
