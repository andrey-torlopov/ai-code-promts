#!/bin/sh
# SessionStart hook: deterministically inject the global rule chain into session context.
#
# CORE.md and RESOLVER.md are the SSOT for behavior and routing. Injecting them here removes
# the probabilistic "agent must decide to read them" step: their content is developer context
# from the first token of the session, and again after resume, clear and compaction.
#
#   found     -> print a wrapped copy to stdout; the runtime adds it as developer context
#   not found -> exit 0 silently (bare Codex install without the system)

set -eu

CODEX_HOME_DIR="${CODEX_HOME:-$HOME/.codex}"
CORE="$CODEX_HOME_DIR/custom/CORE.md"
RESOLVER="$CODEX_HOME_DIR/custom/RESOLVER.md"

if [ ! -f "$CORE" ] || [ ! -f "$RESOLVER" ]; then
  exit 0
fi

echo "AI RUNTIME RULES (injected on SessionStart; current copies of CORE.md and RESOLVER.md)."
echo "Do not re-read these two files this session. For substantial work: pick exactly one skill"
echo "via the routing table below, load only the knowledge packs it names, and output the"
echo "SKILL CONTEXT block before the first file change."
echo "--- $CORE ---"
cat "$CORE"
echo ""
echo "--- $RESOLVER ---"
cat "$RESOLVER"
echo "--- end of injected rules ---"
