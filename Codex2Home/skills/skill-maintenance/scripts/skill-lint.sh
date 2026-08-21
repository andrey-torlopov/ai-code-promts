#!/bin/sh
# Full validator for the global instruction system.
#
# Usage:
#   sh skill-lint.sh                 # validate the installed system in $CODEX_HOME
#   sh skill-lint.sh <root>          # validate a Home template source tree
#
# <root> is a directory that contains custom/ and skills/, i.e. either $CODEX_HOME
# or a Home template checkout.

set -eu

ROOT="${1:-${CODEX_HOME:-$HOME/.codex}}"
CUSTOM="$ROOT/custom"
SKILLS="$ROOT/skills"
REGISTRY="$CUSTOM/_core/active-skills.txt"
FAILED=0
LIST_FILE="${TMPDIR:-/tmp}/skill-lint-$$.list"

fail() {
  echo "CRITICAL $1"
  FAILED=1
}

warn() {
  echo "WARNING $1"
}

require_file() {
  [ -f "$1" ] || fail "${1#"$ROOT"/}: missing"
}

contains() {
  grep -q "$2" "$1" 2>/dev/null
}

require_file "$CUSTOM/CORE.md"
require_file "$CUSTOM/RESOLVER.md"
require_file "$CUSTOM/COMMON.md"
require_file "$CUSTOM/KNOWLEDGE/_index.md"
require_file "$REGISTRY"
require_file "$ROOT/AGENTS.md"

if [ -s "$ROOT/AGENTS.override.md" ]; then
  warn "AGENTS.override.md: shadows AGENTS.md in the global Codex scope"
fi

for anchor in "$ROOT/AGENTS.md"; do
  [ -f "$anchor" ] || continue
  rel="${anchor#"$ROOT"/}"
  contains "$anchor" "CORE.md"     || fail "$rel: anchor must point to CORE.md"
  contains "$anchor" "RESOLVER.md" || fail "$rel: anchor must point to RESOLVER.md"
  contains "$anchor" "SKILLS/agent-router" && fail "$rel: must not route through SKILLS/agent-router"
done

if [ -f "$CUSTOM/COMMON.md" ]; then
  contains "$CUSTOM/COMMON.md" "Compatibility bridge" || fail "custom/COMMON.md: must be a compatibility bridge"
  contains "$CUSTOM/COMMON.md" "CORE.md"              || fail "custom/COMMON.md: must point to CORE.md"
  contains "$CUSTOM/COMMON.md" "RESOLVER.md"          || fail "custom/COMMON.md: must point to RESOLVER.md"
fi

if [ ! -f "$REGISTRY" ]; then
  rm -f "$LIST_FILE"
  exit 1
fi

EXPECTED_SKILLS="$(grep -v '^#' "$REGISTRY" | grep -v '^[[:space:]]*$' || true)"

for skill_name in $EXPECTED_SKILLS; do
  skill="$SKILLS/$skill_name/SKILL.md"
  if [ ! -f "$skill" ]; then
    fail "skills/$skill_name/SKILL.md: missing"
    continue
  fi

  rel="skills/$skill_name/SKILL.md"
  dir="$SKILLS/$skill_name"
  first_line="$(sed -n '1p' "$skill")"
  yaml_name="$(sed -n '2,8p' "$skill" | sed -n 's/^name: *//p' | head -n 1)"
  lines="$(wc -l < "$skill" | tr -d ' ')"

  [ "$first_line" = "---" ] || fail "$rel: missing YAML frontmatter"
  [ "$yaml_name" = "$skill_name" ] || fail "$rel: YAML name '$yaml_name' differs from folder '$skill_name'"

  if sed -n '1,20p' "$skill" | grep -Eq '^(allowed-tools|context|agent|metadata|tags):'; then
    fail "$rel: unsupported frontmatter field"
  fi

  if [ "$lines" -gt 500 ]; then
    fail "$rel: $lines lines, limit 500"
  elif [ "$lines" -gt 300 ]; then
    warn "$rel: $lines lines, recommended max 300"
  fi

  for heading in "## Inputs" "## Workflow" "## Output" "## Stop Conditions" "## SKILL CONTEXT"; do
    grep -q "^$heading" "$skill" || fail "$rel: missing $heading"
  done

  grep -q "TRACE" "$skill" || fail "$rel: missing final TRACE requirement"

  if grep -Eq 'SKILLS/(agent-router|swift-workflow|swift-analysis-plan|swift-refactor-plan|swift-architecture-doc|swift-repo-scout|swift-dependency-check|swift-code-review|swift-delivery|swift-patterns|swift-ai-context-init|research-report|brainstorm-design-spec|skill-authoring|ai-skill-audit|ai-doc-lint|ai-setup-registry)' "$skill"; then
    fail "$rel: references removed top-level skill route"
  fi

  grep -q '_ai/layers/' "$skill" && fail "$rel: references legacy prompt layers"

done

for dead in "$SKILLS/agent-router" "$SKILLS/swift-workflow"; do
  [ -d "$dead" ] && fail "${dead#"$ROOT"/}: active routing skill must not exist"
done

# Every reference target named with an absolute $CODEX_HOME path must exist.
find "$CUSTOM" "$SKILLS" -name '*.md' -type f > "$LIST_FILE" 2>/dev/null || true
while IFS= read -r doc; do
  case "$doc" in
    */stale-reference-signatures.md|*/assets/*) continue ;;
  esac
  grep -oE '\$CODEX_HOME/[A-Za-z0-9_./-]+\.(md|sh|py|json|txt)' "$doc" 2>/dev/null | sort -u |
  while IFS= read -r ref; do
    target="$ROOT/${ref#\$CODEX_HOME/}"
    [ -f "$target" ] || echo "BROKEN-REF ${doc#"$ROOT"/} -> $ref"
  done
done < "$LIST_FILE" > "$LIST_FILE.refs" || true

if [ -s "$LIST_FILE.refs" ]; then
  cat "$LIST_FILE.refs"
  FAILED=1
fi
rm -f "$LIST_FILE" "$LIST_FILE.refs"

if [ -d "$CUSTOM/_ai/layers" ]; then
  fail "custom/_ai/layers: legacy prompt layers must not be active"
fi

grep -q 'deploy-ops' "$CUSTOM/RESOLVER.md" || fail "custom/RESOLVER.md: missing deploy-ops route"

if ! grep -qE 'deploy.*deploy-ops|release.*deploy-ops|publish.*deploy-ops|rollout.*deploy-ops' "$CUSTOM/RESOLVER.md"; then
  fail "custom/RESOLVER.md: deploy/release/publish/rollout must route to deploy-ops"
fi

exit "$FAILED"
