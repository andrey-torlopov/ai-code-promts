#!/usr/bin/env python3
"""Safely merge the Codex2Home-managed hook entries into hooks.json.

Managed entries live under any event section (SessionStart, PreToolUse, ...). Entries not
managed by Codex2Home are preserved untouched; managed ones are replaced wholesale.
"""

from __future__ import annotations

import argparse
import copy
import json
import os
from pathlib import Path
import stat
import tempfile
from typing import Any

MANAGED_HANDLERS = (
    ("/hooks/project-context.sh", "project-context"),
    ("/hooks/rules-context.sh", "rules-context"),
    ("/hooks/route-guard.sh", "route-guard"),
)


class HooksConfigError(ValueError):
    """Raised when a hooks file cannot be merged without losing structure."""


def load_json(path: Path, *, missing_ok: bool) -> dict[str, Any]:
    if missing_ok and not path.exists():
        return {}

    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise HooksConfigError(f"missing hooks file: {path}") from error
    except json.JSONDecodeError as error:
        raise HooksConfigError(
            f"invalid JSON in {path}: line {error.lineno}, column {error.colno}: {error.msg}"
        ) from error

    if not isinstance(value, dict):
        raise HooksConfigError(f"{path}: top-level value must be an object")
    return value


def event_groups(config: dict[str, Any], path: Path, event: str) -> list[Any]:
    hooks = config.get("hooks")
    if hooks is None:
        hooks = {}
        config["hooks"] = hooks
    if not isinstance(hooks, dict):
        raise HooksConfigError(f"{path}: hooks must be an object")

    groups = hooks.get(event)
    if groups is None:
        groups = []
        hooks[event] = groups
    if not isinstance(groups, list):
        raise HooksConfigError(f"{path}: hooks.{event} must be an array")
    return groups


def is_managed_group(group: Any) -> bool:
    if not isinstance(group, dict):
        return False
    handlers = group.get("hooks")
    if not isinstance(handlers, list):
        return False
    for handler in handlers:
        if not isinstance(handler, dict):
            continue
        command = handler.get("command")
        for managed_script, managed_status in MANAGED_HANDLERS:
            if (
                handler.get("type") == "command"
                and handler.get("statusMessage") == managed_status
                and isinstance(command, str)
                and managed_script in command
            ):
                return True
    return False


def merge(
    source: dict[str, Any],
    target: dict[str, Any],
    source_path: Path,
    target_path: Path,
) -> dict[str, Any]:
    source_hooks = source.get("hooks")
    if not isinstance(source_hooks, dict) or not source_hooks:
        raise HooksConfigError(f"{source_path}: hooks must be a non-empty object")

    for event in source_hooks:
        source_groups = event_groups(source, source_path, event)
        if not source_groups or not all(is_managed_group(group) for group in source_groups):
            raise HooksConfigError(
                f"{source_path}: expected only Codex2Home-managed {event} groups"
            )

        target_groups = event_groups(target, target_path, event)
        target_groups[:] = [group for group in target_groups if not is_managed_group(group)]
        target_groups.extend(copy.deepcopy(source_groups))

    if "description" not in target and "description" in source:
        target["description"] = source["description"]
    return target


def write_atomic(path: Path, config: dict[str, Any]) -> None:
    mode = stat.S_IMODE(path.stat().st_mode) if path.exists() else 0o644
    descriptor, temporary_name = tempfile.mkstemp(prefix=".hooks.json.", dir=path.parent)
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(config, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        temporary_path.chmod(mode)
        os.replace(temporary_path, path)
    finally:
        temporary_path.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate inputs without writing")
    parser.add_argument("source", type=Path, help="Codex2Home hooks.json template")
    parser.add_argument("target", type=Path, help="destination hooks.json")
    args = parser.parse_args()

    try:
        source = load_json(args.source, missing_ok=False)
        target = load_json(args.target, missing_ok=True)
        merged = merge(source, target, args.source, args.target)
        if not args.check:
            write_atomic(args.target, merged)
    except (HooksConfigError, OSError) as error:
        parser.exit(2, f"error: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
