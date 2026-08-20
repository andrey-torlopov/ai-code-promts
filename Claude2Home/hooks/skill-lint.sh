#!/bin/sh
# PostToolUse hook: fast validation of SKILL-first instruction files.
#
# Scope, in order:
#   1. ~/.claude/custom/**            - the global instruction system
#   2. ~/.claude/skills/<active>/**   - only skills listed in custom/_core/active-skills.txt
#   3. <project>/**                   - only when the project opted in with CORE.md in its root
# Anything else exits 0 immediately, so ordinary projects and foreign skills are never linted.

set -eu

CLAUDE_HOME="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
CUSTOM_ROOT="$CLAUDE_HOME/custom"
REGISTRY="$CUSTOM_ROOT/_core/active-skills.txt"
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-}"

INPUT="$(cat)"

if ! command -v jq >/dev/null 2>&1; then
  exit 0
fi

FILE_PATH="$(printf '%s' "$INPUT" | jq -r '.tool_input.file_path // empty')"
[ -n "$FILE_PATH" ] || exit 0
[ -f "$FILE_PATH" ] || exit 0

is_active_skill_path() {
  [ -f "$REGISTRY" ] || return 1
  rest="${1#"$CLAUDE_HOME"/skills/}"
  [ "$rest" != "$1" ] || return 1
  name="${rest%%/*}"
  grep -v '^#' "$REGISTRY" | grep -qx "$name"
}

case "$FILE_PATH" in
  "$CUSTOM_ROOT"/*) ;;
  "$CLAUDE_HOME"/CLAUDE.md) ;;
  "$CLAUDE_HOME"/skills/*)
    is_active_skill_path "$FILE_PATH" || exit 0
    ;;
  *)
    [ -n "$PROJECT_DIR" ] || exit 0
    [ -f "$PROJECT_DIR/CORE.md" ] || exit 0
    case "$FILE_PATH" in
      "$PROJECT_DIR"/*) ;;
      *) exit 0 ;;
    esac
    ;;
esac

case "$FILE_PATH" in
  */stale-reference-signatures.md) exit 0 ;;
  */CORE.md|*/RESOLVER.md|*/COMMON.md|*/AGENTS.md|*/CLAUDE.md|*/GEMINI.md) ;;
  */SKILL.md) ;;
  */modes/*.md|*/references/*.md) ;;
  */KNOWLEDGE/*.md|*/KNOWLEDGE/*/*.md|*/KNOWLEDGE/*/*/*.md) ;;
  */_core/*.md) ;;
  *) exit 0 ;;
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
