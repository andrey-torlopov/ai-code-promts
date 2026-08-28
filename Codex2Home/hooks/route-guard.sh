#!/bin/sh
# PreToolUse gate for file-editing tools: file changes are substantial work, and substantial
# work must start with the SKILL CONTEXT block (CORE.md contract). This hook makes the
# contract mechanical: no block in the session transcript -> the edit is denied (exit 2)
# with instructions.
#
# Fail-open by design: any parse failure, missing transcript, missing python3, or a
# transcript format with no recognizable assistant lines allows the tool call. It blocks
# only on positive evidence that routing was skipped.
#
# Escape hatch: CODEX_ROUTE_GUARD=off disables the gate.

set -eu

if [ "${CODEX_ROUTE_GUARD:-on}" = "off" ]; then
  exit 0
fi

IN="$(cat 2>/dev/null || true)"
if [ -z "$IN" ]; then
  exit 0
fi

PARSED="$(printf '%s' "$IN" | python3 -c '
import json, sys
try:
    d = json.load(sys.stdin)
    print(d.get("transcript_path") or "")
    print((d.get("tool_input") or {}).get("file_path", ""))
except Exception:
    pass
' 2>/dev/null || true)"

TRANSCRIPT="$(printf '%s\n' "$PARSED" | sed -n 1p)"
FILE="$(printf '%s\n' "$PARSED" | sed -n 2p)"

# Never gate scratch space.
case "$FILE" in
  /tmp/*|/private/tmp/*) exit 0 ;;
esac

if [ -z "$TRANSCRIPT" ] || [ ! -f "$TRANSCRIPT" ]; then
  exit 0
fi

# Unknown transcript format or nothing flushed yet: fail open rather than false-block.
if ! grep -q '"role":"assistant"' "$TRANSCRIPT" 2>/dev/null; then
  exit 0
fi

# The block only counts when the assistant itself emitted it: require the SKILL:/STOP:
# fields on assistant transcript lines, so the injected rules (user/system lines) and this
# hook's own message can never satisfy the gate.
if grep '"role":"assistant"' "$TRANSCRIPT" 2>/dev/null | grep 'SKILL:' | grep -q 'STOP:'; then
  exit 0
fi

echo "route-guard: file edits are substantial work, and no routing block was emitted this session. Per the injected CORE/RESOLVER rules: pick one workflow skill from the routing table, load the knowledge packs it names, output the required context block (the SKILL/TASK/REASON/KNOWLEDGE/STOP lines from custom/_core/skill-context.md), then retry this edit." >&2
exit 2
