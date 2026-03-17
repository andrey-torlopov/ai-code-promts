#!/bin/sh
set -eu

ROOT="${1:-.}"
FAILED=0
LIST_FILE="${TMPDIR:-/tmp}/skill-lint-$$.list"

fail() {
  echo "CRITICAL $1"
  FAILED=1
}

warn() {
  echo "WARNING $1"
}

exists_file() {
  [ -f "$ROOT/$1" ]
}

contains() {
  grep -q "$2" "$ROOT/$1" 2>/dev/null
}

require_file() {
  if ! exists_file "$1"; then
    fail "$1: missing"
  fi
}

require_file "CORE.md"
require_file "RESOLVER.md"
require_file "COMMON.md"
require_file "AGENTS.md"
require_file "CLAUDE.md"
require_file "GEMINI.md"
require_file "KNOWLEDGE/_index.md"

for anchor in AGENTS.md CLAUDE.md GEMINI.md; do
  if exists_file "$anchor"; then
    if ! contains "$anchor" "CORE.md"; then
      fail "$anchor: anchor must point to CORE.md"
    fi
    if ! contains "$anchor" "RESOLVER.md"; then
      fail "$anchor: anchor must point to RESOLVER.md"
    fi
    if contains "$anchor" "SKILLS/agent-router"; then
      fail "$anchor: must not route through SKILLS/agent-router"
    fi
  fi
done

if exists_file "COMMON.md"; then
  if ! contains "COMMON.md" "Compatibility bridge"; then
    fail "COMMON.md: must be a compatibility bridge"
  fi
  if ! contains "COMMON.md" "CORE.md"; then
    fail "COMMON.md: must point to CORE.md"
  fi
  if ! contains "COMMON.md" "RESOLVER.md"; then
    fail "COMMON.md: must point to RESOLVER.md"
  fi
fi

EXPECTED_SKILLS="analysis-plan swift-build-optimization implementation-from-plan debug-diagnose mac-local-ops deploy-ops skill-maintenance"
set -- $EXPECTED_SKILLS
expected_skill_count="$#"

for skill_name in $EXPECTED_SKILLS; do
  require_file "SKILLS/$skill_name/SKILL.md"
done

if [ -d "$ROOT/SKILLS/agent-router" ]; then
  fail "SKILLS/agent-router: active routing skill must not exist"
fi

if [ -d "$ROOT/SKILLS/swift-workflow" ]; then
  fail "SKILLS/swift-workflow: active routing skill must not exist"
fi

find "$ROOT/SKILLS" -mindepth 1 -maxdepth 1 -type d | sort > "$LIST_FILE"
skill_count="$(wc -l < "$LIST_FILE" | tr -d ' ')"
if [ "$skill_count" -ne "$expected_skill_count" ]; then
  fail "SKILLS: expected $expected_skill_count active workflow skills, found $skill_count"
fi

find "$ROOT" -name SKILL.md -type f | sort > "$LIST_FILE"

while IFS= read -r skill; do
  rel="${skill#"$ROOT"/}"
  dir="$(dirname "$skill")"
  name="$(basename "$dir")"
  first_line="$(sed -n '1p' "$skill")"
  yaml_name="$(sed -n '2,8p' "$skill" | sed -n 's/^name: *//p' | head -n 1)"
  lines="$(wc -l < "$skill" | tr -d ' ')"

  if [ "$first_line" != "---" ]; then
    fail "$rel: missing YAML frontmatter"
  fi

  if [ "$yaml_name" != "$name" ]; then
    fail "$rel: YAML name '$yaml_name' differs from folder '$name'"
  fi

  if sed -n '1,20p' "$skill" | grep -Eq '^(allowed-tools|context|agent|metadata|tags):'; then
    fail "$rel: unsupported frontmatter field"
  fi

  if [ "$lines" -gt 500 ]; then
    fail "$rel: $lines lines, limit 500"
  elif [ "$lines" -gt 300 ]; then
    warn "$rel: $lines lines, recommended max 300"
  fi

  for heading in "## Inputs" "## Workflow" "## Output" "## Stop Conditions" "## SKILL CONTEXT"; do
    if ! grep -q "^$heading" "$skill"; then
      fail "$rel: missing $heading"
    fi
  done

  if grep -Eq 'SKILLS/(agent-router|swift-workflow|swift-analysis-plan|swift-refactor-plan|swift-architecture-doc|swift-repo-scout|swift-dependency-check|swift-code-review|swift-delivery|swift-patterns|swift-ai-context-init|research-report|brainstorm-design-spec|skill-authoring|ai-skill-audit|ai-doc-lint|ai-setup-registry)' "$skill"; then
    fail "$rel: references removed top-level skill route"
  fi

  if grep -q '_ai/layers/' "$skill"; then
    fail "$rel: references legacy prompt layers"
  fi

  if find "$dir" -path '*/agents/openai.yaml' -type f | grep -q .; then
    fail "$rel: agents/openai.yaml is not allowed"
  fi
done < "$LIST_FILE"

rm -f "$LIST_FILE"

if [ -d "$ROOT/_ai/layers" ]; then
  fail "_ai/layers: legacy prompt layers must not be active"
fi

if [ -f "$ROOT/_ai/Router.md" ]; then
  fail "_ai/Router.md: legacy router must not be active"
fi

if find "$ROOT" -path "$ROOT/.git" -prune -o -type f -name '*.md' -print |
  grep -v 'SKILLS/skill-maintenance/references/stale-reference-signatures.md' |
  xargs grep -n '_ai/layers/' >/dev/null 2>&1; then
  fail "active Markdown references legacy _ai/layers"
fi

if ! grep -q 'deploy-ops' "$ROOT/RESOLVER.md"; then
  fail "RESOLVER.md: missing deploy-ops route"
fi

if ! grep -n 'deploy.*deploy-ops\|release.*deploy-ops\|publish.*deploy-ops\|rollout.*deploy-ops' "$ROOT/RESOLVER.md" >/dev/null 2>&1; then
  fail "RESOLVER.md: deploy/release/publish/rollout must route to deploy-ops"
fi

exit "$FAILED"
