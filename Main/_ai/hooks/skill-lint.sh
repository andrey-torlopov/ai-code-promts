#!/bin/sh
# Post-edit hook: fast validation of SKILL-first instruction files.

set -eu

INPUT="$(cat)"
FILE_PATH="$(printf '%s' "$INPUT" | jq -r '.tool_input.file_path // empty')"

if [ -z "$FILE_PATH" ]; then
  exit 0
fi

case "$FILE_PATH" in
  */CORE.md|*/RESOLVER.md|*/COMMON.md|*/AGENTS.md|*/CLAUDE.md|*/GEMINI.md|*/SKILLS/*/SKILL.md|*/SKILLS/*/modes/*.md|*/SKILLS/*/references/*.md|*/KNOWLEDGE/*.md|*/KNOWLEDGE/*/*.md|*/_core/*.md)
    ;;
  *)
    exit 0
    ;;
esac

FINDINGS=""
FILENAME="$(basename "$FILE_PATH")"
LINE_COUNT="$(wc -l < "$FILE_PATH" | tr -d ' ')"

if [ "$FILENAME" = "SKILL.md" ]; then
  if [ "$(sed -n '1p' "$FILE_PATH")" != "---" ]; then
    FINDINGS="${FINDINGS}
 CRITICAL: Missing YAML frontmatter"
  fi
  for heading in "## Inputs" "## Workflow" "## Output" "## Stop Conditions" "## SKILL CONTEXT"; do
    if ! grep -q "^$heading" "$FILE_PATH"; then
      FINDINGS="${FINDINGS}
 CRITICAL: Missing ${heading}"
    fi
  done
fi

case "$FILENAME" in
  AGENTS.md|CLAUDE.md|GEMINI.md)
    if ! grep -q 'CORE.md' "$FILE_PATH"; then
      FINDINGS="${FINDINGS}
 CRITICAL: Anchor must point to CORE.md"
    fi
    if ! grep -q 'RESOLVER.md' "$FILE_PATH"; then
      FINDINGS="${FINDINGS}
 CRITICAL: Anchor must point to RESOLVER.md"
    fi
    if grep -q 'SKILLS/agent-router' "$FILE_PATH"; then
      FINDINGS="${FINDINGS}
 CRITICAL: Anchor must not route through SKILLS/agent-router"
    fi
    ;;
  COMMON.md)
    if ! grep -q 'Compatibility bridge' "$FILE_PATH"; then
      FINDINGS="${FINDINGS}
 CRITICAL: COMMON.md must remain a bridge"
    fi
    ;;
esac

if [ "$LINE_COUNT" -gt 500 ]; then
  FINDINGS="${FINDINGS}
 WARNING: ${LINE_COUNT} lines"
fi

if grep -Eq 'SKILLS/(agent-router|swift-workflow)|_ai/layers/' "$FILE_PATH"; then
  FINDINGS="${FINDINGS}
 CRITICAL: Stale active routing or legacy layer reference"
fi

if [ -n "$FINDINGS" ]; then
  printf 'skill-lint: %s%s\n' "$FILE_PATH" "$FINDINGS" >&2
  exit 2
fi

exit 0
