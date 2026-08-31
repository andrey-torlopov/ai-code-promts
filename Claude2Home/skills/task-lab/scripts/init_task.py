#!/usr/bin/env python3
"""Create a canonical task-lab folder (layout v2) without overwriting existing files.

There is exactly one layout: root ``README.md`` with the machine-readable state
line as the only entry point, ``Steps/`` with single-file ``Step-NN.md`` records,
``Knowledge/``, ``Results/``, ``tools/``, ``Notes/``, root ``Logs/`` and optional
``Inbox/``. Folders that carry the v1 layout (``index.md``, root ``steps.md``,
``Context/``) are refused with a ``migrate_task.py`` hint; foreign shapes
(``Process/steps/``, ``Steps/_next.md``) are refused outright.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path
from typing import NoReturn

from resolve_task import TaskResolutionError, find_task_dirs, validate_task_id

MODES = ("general", "bug", "perf", "plan")

STANDARD_FILES = (
    "README.md",
    "env.json",
    "Knowledge/README.md",
    "Knowledge/F-01-problem-and-targets.md",
    "Knowledge/F-02-environment.md",
    "Results/README.md",
)

STANDARD_DIRS = ("Steps", "Notes", "Logs", "tools")

FOREIGN_MARKERS = (
    ("Process/steps", "Process/steps/"),
    ("Steps/_next.md", "Steps/_next.md"),
)

LEGACY_MARKERS = (
    ("index.md", "index.md"),
    ("steps.md", "steps.md"),
    ("Context", "Context/"),
)


def die(message: str) -> NoReturn:
    print(f"ОШИБКА: {message}", file=sys.stderr)
    raise SystemExit(2)


def foreign_marker(task_dir: Path) -> str | None:
    for relative, label in FOREIGN_MARKERS:
        if (task_dir / relative).exists():
            return label
    return None


def legacy_marker(task_dir: Path) -> str | None:
    for relative, label in LEGACY_MARKERS:
        if (task_dir / relative).exists():
            return label
    return None


def template_root(explicit: str | None) -> Path:
    if explicit:
        root = Path(explicit).expanduser().resolve()
    else:
        root = Path(__file__).resolve().parent.parent / "templates" / "standard"
    if not root.is_dir():
        die(f"каталог шаблонов не найден: {root}")
    return root.resolve()


def template_for(relative: str, root: Path) -> Path:
    candidate = root / relative
    if not candidate.is_file():
        die(f"шаблон отсутствует: {candidate}")
    return candidate


def substitute(text: str, values: dict[str, str]) -> str:
    for key, value in values.items():
        text = text.replace("{{%s}}" % key, value)
    return text


def build_plan(with_inbox: bool) -> list[str]:
    """The file set is identical for every mode; only Inbox/ is optional."""
    files = list(STANDARD_FILES)
    if with_inbox:
        files.append("Inbox/README.md")
    return files


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Развернуть durable task folder из task-lab (layout v2)")
    parser.add_argument("--id", required=True, help="TaskID и имя папки, например 123 или APP-001")
    parser.add_argument("--title", default=None, help="название; по умолчанию равно TaskID")
    parser.add_argument("--mode", default="general", choices=MODES, help="внутренний режим; структура одинакова")
    parser.add_argument("--workspace", default=".", help="область поиска/создания; по умолчанию текущий workspace")
    parser.add_argument("--date", default=None, help="YYYY-MM-DD; по умолчанию сегодня")
    parser.add_argument("--with-inbox", action="store_true", help="создать временную Inbox/")
    parser.add_argument("--kb", default=None, help="путь к внешней базе знаний; заполняет external_knowledge в env.json")
    parser.add_argument("--templates", default=None, help="явный корень шаблонов")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    workspace = Path(args.workspace).expanduser().resolve()
    if not workspace.is_dir():
        die(f"workspace не является каталогом: {workspace}")
    try:
        validate_task_id(args.id)
        matches = find_task_dirs(args.id, workspace)
    except TaskResolutionError as error:
        die(str(error))
    if len(matches) > 1:
        rendered = "\n  - ".join(str(path) for path in matches)
        die(f"TaskID {args.id!r} неоднозначен; найдено {len(matches)} папки:\n  - {rendered}")
    task_dir = matches[0] if matches else workspace / args.id
    if task_dir.exists() and not task_dir.is_dir():
        die(f"путь TaskID уже существует и не является папкой: {task_dir}")

    marker = foreign_marker(task_dir)
    if marker:
        die(
            f"в {task_dir} найдена неканоническая структура ({marker}); поверх неё нельзя разворачивать "
            "каноническую. Перенос — отдельная явная задача"
        )
    marker = legacy_marker(task_dir)
    if marker:
        die(
            f"в {task_dir} найдена структура v1 ({marker}); поверх неё нельзя разворачивать v2. "
            "Конвертация выполняется явно: python3 migrate_task.py " + args.id
        )

    now = dt.datetime.now().astimezone()
    date = args.date or now.date().isoformat()
    try:
        parsed_date = dt.date.fromisoformat(date)
    except ValueError:
        die(f"дата не в формате YYYY-MM-DD: {date}")
    if args.date:
        timestamp = dt.datetime.combine(parsed_date, dt.time.min, tzinfo=now.tzinfo).strftime("%Y-%m-%d %H:%M")
    else:
        timestamp = now.strftime("%Y-%m-%d %H:%M")

    root = template_root(args.templates)
    files = build_plan(args.with_inbox)
    values = {
        "TASK_ID": args.id,
        "TITLE": args.title or args.id,
        "DATE": date,
        "TIMESTAMP": timestamp,
        "MODE": args.mode,
        # JSON-escaped content without the surrounding quotes, safe inside "…" in env.json.
        "KB_PATH": json.dumps(args.kb or "", ensure_ascii=False)[1:-1],
    }

    created: list[str] = []
    skipped: list[str] = []
    for relative in STANDARD_DIRS:
        target = task_dir / relative
        if target.is_dir():
            skipped.append(relative + "/")
            continue
        if target.exists():
            die(f"путь обязательного каталога уже занят файлом: {target}")
        if not args.dry_run:
            target.mkdir(parents=True, exist_ok=False)
        created.append(relative + "/")
    for relative in files:
        target = task_dir / relative
        if target.exists():
            skipped.append(relative)
            continue
        source = template_for(relative, root)
        content = substitute(source.read_text(encoding="utf-8"), values)
        if not args.dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        created.append(relative)

    prefix = "[dry-run] " if args.dry_run else ""
    print(f"{prefix}Папка задачи: {task_dir}")
    print(f"{prefix}TaskID: {args.id} · режим: {args.mode} · структура: каноническая v2 · дата: {date}")

    print(f"\n{prefix}Создано ({len(created)}):")
    for relative in created:
        print(f"  + {relative}")
    if skipped:
        print(f"\n{prefix}Пропущено, уже существует ({len(skipped)}):")
        for relative in skipped:
            print(f"  = {relative}")
    if args.kb:
        kb_path = Path(args.kb).expanduser()
        if not kb_path.is_absolute():
            kb_path = (task_dir / kb_path).resolve()
        if not kb_path.is_dir():
            print(f"\nВНИМАНИЕ: путь внешней базы не существует: {kb_path}")
        elif not (kb_path / "README.md").is_file():
            print(f"\nВНИМАНИЕ: во внешней базе нет реестра README.md: {kb_path}")

    print("\nДальше:")
    print("  1. Заполнить Knowledge/F-01 и F-02, затем README (задача, правила, дрейф, очередность).")
    print("  2. Будущий шаг заранее не создавать: Steps/Step-01.md появляется по запросу пользователя,")
    print("     строка состояния README обновляется при открытии и закрытии шага.")
    print("  3. Удалить все {{FILL_*}}; до этого audit обязан быть красным.")

    audit = Path(__file__).resolve().parent / "audit_task.py"
    restore = Path(__file__).resolve().parent / "restore_task.py"
    print("\nПроверка:")
    print(f"  python3 {audit} {args.id} --workspace {workspace}")
    print(f"  python3 {restore} {args.id} --workspace {workspace}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
