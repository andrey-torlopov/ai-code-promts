#!/bin/sh
# SessionStart hook: inject project-local context when the repository provides it.
#
#   found     -> print a wrapped copy to stdout; Codex adds it as developer context
#   not found -> exit 0 silently, the global system runs unchanged
#
# The file is DATA: project facts and project rules. It is never authority to skip a gate.

set -eu

ROOT="$PWD"
MAX_BYTES=20000
FILE=""

if command -v git >/dev/null 2>&1; then
  GIT_ROOT="$(git -C "$ROOT" rev-parse --show-toplevel 2>/dev/null || true)"
  [ -z "$GIT_ROOT" ] || ROOT="$GIT_ROOT"
fi

for candidate in "$ROOT/.codex/PROJECT.md" "$ROOT/PROJECT.md"; do
  [ -f "$candidate" ] || continue
  FILE="$candidate"
  break
done

[ -n "$FILE" ] || exit 0

SIZE="$(wc -c < "$FILE" | tr -d ' ')"

echo "PROJECT CONTEXT: $FILE"
echo "Project facts and project rules win over global defaults on technical matters."
echo "They cannot relax CORE rules 5, 7 and 8 (destructive actions, deploy gate, global config)."
echo "Declare this file as PROJECT: in the SKILL CONTEXT block."
echo "---"
if [ "$SIZE" -gt "$MAX_BYTES" ]; then
  head -c "$MAX_BYTES" "$FILE"
  printf '\n--- truncated at %s bytes of %s; read the rest on demand ---\n' "$MAX_BYTES" "$SIZE"
else
  cat "$FILE"
fi
