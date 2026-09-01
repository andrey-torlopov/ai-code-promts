#!/bin/sh
# PreToolUse gate for Write|Edit: file changes are substantial work, and substantial work
# must start with the SKILL CONTEXT block (CORE.md contract). This hook makes the contract
# mechanical: no block in the session transcript -> the edit is denied with instructions.
#
# Fail-open by design: any parse failure, missing transcript or missing jq allows the
# tool call. It blocks only on positive evidence that routing was skipped.
# After the first success the verdict is cached in a per-transcript flag file, so the
# steady-state cost is one existence check.
#
# Escape hatch: CLAUDE_ROUTE_GUARD=off disables the gate.

set -eu

if [ "${CLAUDE_ROUTE_GUARD:-on}" = "off" ]; then
  exit 0
fi

IN="$(cat 2>/dev/null || true)"
if [ -z "$IN" ]; then
  exit 0
fi

command -v jq >/dev/null 2>&1 || exit 0

TRANSCRIPT="$(printf '%s' "$IN" | jq -r '.transcript_path // empty' 2>/dev/null || true)"
FILE="$(printf '%s' "$IN" | jq -r '.tool_input.file_path // empty' 2>/dev/null || true)"

# Never gate scratch space or Claude-internal session data (memory, todos, transcripts).
case "$FILE" in
  /tmp/*|/private/tmp/*|*/.claude/projects/*) exit 0 ;;
esac

if [ -z "$TRANSCRIPT" ] || [ ! -f "$TRANSCRIPT" ]; then
  exit 0
fi

# A block never disappears from a transcript, so one success is cached for the session.
FLAG="${TMPDIR:-/tmp}/route-guard-ok-$(basename "$TRANSCRIPT")"
[ -f "$FLAG" ] && exit 0

# Unknown transcript format or nothing flushed yet: fail open rather than false-block.
if ! grep -q '"role":"assistant"' "$TRANSCRIPT" 2>/dev/null; then
  exit 0
fi

# The block only counts when the assistant itself emitted it: require the SKILL:/STOP:
# fields on assistant transcript lines, so the injected rules (user/system lines) and this
# hook's own message can never satisfy the gate.
if grep '"role":"assistant"' "$TRANSCRIPT" 2>/dev/null | grep 'SKILL:' | grep -q 'STOP:'; then
  : > "$FLAG" 2>/dev/null || true
  exit 0
fi

echo "route-guard: file edits are substantial work, and no routing block was emitted this session. Per the injected CORE/RESOLVER rules: pick one workflow skill from the routing table, load the knowledge packs it names, output the required context block (the SKILL/TASK/REASON/KNOWLEDGE/STOP lines from custom/_core/skill-context.md), then retry this edit." >&2
exit 2
