#!/usr/bin/env python3
"""Resolve a task folder from an explicit path or an exact TaskID."""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

TASK_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
PRUNE_NAMES = {
    ".git",
    ".build",
    ".idea",
    ".swiftpm",
    ".venv",
    "DerivedData",
    "build",
    "graphify-out",
    "node_modules",
    "venv",
}


class TaskResolutionError(ValueError):
    """The TaskID or path cannot be resolved unambiguously."""


def validate_task_id(task_id: str) -> str:
    if not TASK_ID_RE.fullmatch(task_id):
        raise TaskResolutionError(
            f"некорректный TaskID {task_id!r}; разрешены буквы, цифры, точка, '_' и '-'"
        )
    return task_id


def find_task_dirs(task_id: str, workspace: Path) -> list[Path]:
    validate_task_id(task_id)
    root = workspace.expanduser().resolve()
    if not root.is_dir():
        raise TaskResolutionError(f"workspace не является каталогом: {root}")

    matches: list[Path] = []
    if root.name == task_id:
        matches.append(root)
    for current, directories, _ in os.walk(root, followlinks=False):
        directories[:] = [name for name in directories if name not in PRUNE_NAMES]
        for name in list(directories):
            if name != task_id:
                continue
            raw_candidate = Path(current) / name
            if raw_candidate.is_symlink():
                directories.remove(name)
                continue
            candidate = raw_candidate.resolve()
            matches.append(candidate)
            directories.remove(name)
    return sorted(set(matches))


def resolve_task(value: str, workspace: Path) -> Path:
    supplied = Path(value).expanduser()
    looks_like_path = supplied.is_absolute() or any(separator in value for separator in ("/", os.sep))
    if looks_like_path or supplied.is_dir():
        candidate = supplied.resolve()
        if not candidate.is_dir():
            raise TaskResolutionError(f"путь задачи не является каталогом: {candidate}")
        return candidate

    matches = find_task_dirs(value, workspace)
    if not matches:
        raise TaskResolutionError(
            f"папка с TaskID {value!r} не найдена в workspace {workspace.expanduser().resolve()}"
        )
    if len(matches) > 1:
        rendered = "\n  - ".join(str(path) for path in matches)
        raise TaskResolutionError(
            f"TaskID {value!r} неоднозначен; найдено {len(matches)} папки:\n  - {rendered}"
        )
    return matches[0]


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Найти папку задачи по TaskID или точному пути")
    parser.add_argument("task", help="TaskID, например 123 или APP-001, либо точный путь")
    parser.add_argument("--workspace", default=".", help="область поиска TaskID; по умолчанию текущий workspace")
    args = parser.parse_args(argv)
    try:
        print(resolve_task(args.task, Path(args.workspace)))
    except TaskResolutionError as error:
        print(f"ОШИБКА: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
