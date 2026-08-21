#!/bin/sh
set -eu

if [ "$#" -lt 2 ]; then
  echo "Usage: $0 skill-name 'description text' [target-root]" >&2
  exit 2
fi

NAME="$1"
DESCRIPTION="$2"
# Default target: the skills/ directory of whichever tree this script lives in — the Home
# template source or the installed ~/.claude. Never a hard-coded machine path.
SELF_DIR="$(cd "$(dirname "$0")" && pwd)"
TREE_ROOT="$(cd "$SELF_DIR/../../.." && pwd)"
ROOT="${3:-$TREE_ROOT/skills}"

case "$NAME" in
  *[!a-z0-9-]*|''|*-| -*)
    echo "Invalid skill name: use lowercase letters, digits and hyphens only" >&2
    exit 2
    ;;
esac

DIR="$ROOT/$NAME"
if [ -e "$DIR" ]; then
  echo "Refusing to overwrite existing directory: $DIR" >&2
  exit 1
fi

mkdir -p "$DIR/references"

{
  printf '%s\n' '---'
  printf 'name: %s\n' "$NAME"
  printf 'description: %s\n' "$DESCRIPTION"
  printf '%s\n\n' '---'
  printf '# %s\n\n' "$NAME"
  printf '%s\n\n' 'Read this file first. This skill is atomic and must not require sibling skill folders.'
  printf '%s\n\n' '## Inputs'
  printf '%s\n\n' '- User request and concrete target artifact or path.'
  printf '%s\n\n' '## Workflow'
  printf '%s\n' '1. Inspect the request and available files.'
  printf '%s\n' '2. Read only local references required by this task.'
  printf '%s\n' '3. Perform the smallest complete workflow that satisfies the request.'
  printf '%s\n\n' '4. Verify the output or state the blocker.'
  printf '%s\n\n' '## Output'
  printf '%s\n\n' 'Return changed paths, produced artifacts, verification and residual risk.'
  printf '%s\n\n' '## Stop Conditions'
  printf '%s\n' '- Stop if required input is missing.'
  printf '%s\n' '- Do not rely on another skill folder for core instructions.'
} > "$DIR/SKILL.md"

echo "$DIR"
