#!/usr/bin/env python3
"""Convert a v1 task-lab folder (index.md / steps.md / Context/) to layout v2.

Explicit request only: the audit/restore/init scripts refuse v1 folders and
point here. The conversion merges every ``Step-XX.md`` + ``Step-XX-result.md``
pair into a single ``Step-XX.md``, composes the v2 ``README.md`` from
``index.md``, ``steps.md`` and ``Context/``, relocates ``Context/`` content,
and moves every superseded original into ``Archive/v1/`` — nothing is deleted.

Exit codes: 0 = converted, 2 = refused (wrong layout, ambiguous TaskID).
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import shutil
import sys
from pathlib import Path
from typing import NoReturn

from audit_task import HEADING_RE, detect_layout, level2_sections, section_lookup
from resolve_task import TaskResolutionError, resolve_task
from restore_task import field, first_heading, read, shorten, table_rows

DURABLE_TOPS = ("Knowledge", "Steps", "Results")
DURABLE_ROOT_FILES = ("decisions.md", "change-log.md", "acceptance.md")
LINK_REPLACEMENTS = (
    ("Context/tools/", "tools/"),
    ("Context/change-log.md", "change-log.md"),
    ("Context/decisions.md", "decisions.md"),
    ("Context/verification-and-acceptance.md", "acceptance.md"),
    ("](../index.md", "](../README.md"),
    ("](index.md", "](README.md"),
    ("](../steps.md", "](../README.md"),
    ("](steps.md", "](README.md"),
)
STALE_PATTERNS = (
    re.compile(r"Context/"),
    re.compile(r"\]\((?:\.\./)*index\.md"),
    re.compile(r"\]\((?:\.\./)*steps\.md"),
    re.compile(r"Step-\d+-result\.md"),
)


def die(message: str) -> NoReturn:
    print(f"ОШИБКА: {message}", file=sys.stderr)
    raise SystemExit(2)


def trim(lines: list[str]) -> list[str]:
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return lines


def section(text: str, pattern: str) -> list[str]:
    """Body lines of the first heading (any level) matching the regex."""
    lines = text.splitlines()
    matcher = re.compile(pattern, re.IGNORECASE)
    start: int | None = None
    level: int | None = None
    for index, line in enumerate(lines):
        heading = HEADING_RE.match(line)
        if heading and matcher.search(heading.group(2)):
            start, level = index + 1, len(heading.group(1))
            break
    if start is None or level is None:
        return []
    result: list[str] = []
    for line in lines[start:]:
        heading = HEADING_RE.match(line)
        if heading and len(heading.group(1)) <= level:
            break
        result.append(line)
    return trim(result)


def normalize_status(raw: str) -> str:
    low = raw.lower()
    if "отмен" in low:
        return "отменён"
    if "блок" in low:
        return "заблокирован"
    return "завершён"


def step_title(*texts: str) -> str:
    for text in texts:
        heading = first_heading(text)
        if heading:
            heading = re.sub(r"^шаг\s*\d+\s*[—:-]\s*", "", heading, flags=re.IGNORECASE)
            heading = re.sub(r"^результат:\s*", "", heading, flags=re.IGNORECASE)
            if heading.strip():
                return heading.strip()
    return "перенесённый шаг"


def compose_step(number: int, plan_text: str, result_text: str | None, today: str) -> tuple[str, dict[str, str]]:
    """Return the merged v2 step file plus metadata for the README history."""
    plan_sections = level2_sections(plan_text)

    def plan_get(name: str) -> str:
        return (section_lookup(plan_sections, name) or "").strip()

    request = plan_get("запрос пользователя") or plan_get("запрос")
    question = plan_get("вопрос шага") or plan_get("вопрос")
    if question and question not in request:
        request = (request + "\n\nВопрос шага: " + question).strip()
    if not request:
        request = "Перенос из v1: запрос не был выписан отдельной секцией."

    plan_parts: list[str] = []
    criterion_found = False
    for label, name in (
        ("Границы", "границы"),
        ("Входы", "входы"),
        ("Действия", "действия"),
        ("Критерий завершения", "критерий завершения"),
        ("Карта вердиктов", "карта вердиктов"),
    ):
        body = plan_get(name)
        if body:
            plan_parts.append(f"**{label}:**\n\n{body}")
            if name == "критерий завершения":
                criterion_found = True
    if not criterion_found:
        plan_parts.append("**Критерий завершения:** не был зафиксирован в v1; перенос без изменений.")

    lines = [f"# Шаг {number:02d} — {step_title(plan_text, result_text or '')}", ""]
    meta = {"date": today, "verdict": "", "status": "выполняется"}

    if result_text is None:
        date = field(plan_text, {"дата", "date"}) or today
        meta["date"] = date
        lines += [f"**Статус:** выполняется · **Дата:** {date}", ""]
        lines += ["## Запрос", "", request, "", "## План", ""]
        lines.append("\n\n".join(plan_parts))
        lines.append("")
        return "\n".join(lines), meta

    result_sections = level2_sections(result_text)

    def result_get(name: str) -> str:
        return (section_lookup(result_sections, name) or "").strip()

    status = normalize_status(field(result_text, {"статус", "status"}))
    date = field(result_text, {"дата", "date"}) or field(plan_text, {"дата", "date"}) or today
    verdict = field(result_text, {"вердикт", "answer"})
    if not verdict:
        heading = first_heading(result_text)
        verdict = heading.split(":", 1)[1].strip() if ":" in heading else ""
    if not verdict:
        verdict = "перенос из v1: вердикт не был выписан отдельной строкой; см. текст результата"

    done = result_get("что сделано") or "Перенос из v1: отдельного блока «Что сделано» не было; см. «Результат»."

    result_parts = [f"**Вердикт:** {verdict}"]
    for label, name in (
        ("Доказательства", "доказательства"),
        ("Изменённые файлы и артефакты", "изменённые файлы"),
        ("Что НЕ сделано", "что не сделано"),
        ("Ограничения и долги", "ограничения"),
    ):
        body = result_get(name)
        if body:
            result_parts.append(f"**{label}:**\n\n{body}")

    knowledge = "| ID | Роль в шаге |\n|---|---|\n| — | перенос из v1: роли не размечались |"
    knowledge_src = result_get("изменения знаний")
    if knowledge_src:
        knowledge += "\n\nИзменения знаний (перенос из v1):\n\n" + knowledge_src

    meta.update({"date": date, "verdict": verdict, "status": status})
    lines += [f"**Статус:** {status} · **Дата:** {date}", ""]
    lines += ["## Запрос", "", request, "", "## План", ""]
    lines.append("\n\n".join(plan_parts))
    lines += ["", "## Что сделано", "", done, "", "## Результат", ""]
    lines.append("\n\n".join(result_parts))
    lines += ["", "## Задействованные знания", "", knowledge, ""]
    return "\n".join(lines), meta


FOLDER_MAP = """```text
README.md      ← вы здесь: состояние, правила, дрейф-чек, история, очередность
env.json       указатель на внешнюю базу знаний; пустая строка — базы нет
Knowledge/     реестр фактов F-NN и гипотез H-NN, по одному утверждению на файл
Steps/         Step-NN.md — один файл на шаг: запрос, план, что сделано, результат, знания
Results/       самодостаточный деливерабл: читается без остальной папки
tools/         скрипты задачи: читатели, калькуляторы, анализаторы
Notes/         черновики и журналы наблюдений; не источник истины
Logs/          сырой машинный вывод; рядом с Notes/, не внутри
Inbox/         входные материалы — временная папка, к удалению
Archive/       оригиналы структуры v1; аудит игнорирует, ссылки внутрь запрещены
```

Порядок чтения при старте сессии: `restore_task.py` → этот файл целиком → открытый
`Steps/Step-NN.md` (или последний закрытый как чекпойнт) → `Knowledge/README.md` при смене
направления → только файлы, названные планом шага."""


class Migration:
    def __init__(self, root: Path, dry: bool):
        self.root = root
        self.dry = dry
        self.archive = root / "Archive" / "v1"
        self.log: list[str] = []
        self.review: list[str] = []
        self.today = dt.date.today().isoformat()

    def note(self, message: str) -> None:
        prefix = "[dry-run] " if self.dry else ""
        self.log.append(prefix + message)

    def write(self, path: Path, content: str) -> None:
        self.note(f"записан {path.relative_to(self.root)}")
        if not self.dry:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")

    def to_archive(self, path: Path, sub: str = "") -> None:
        if not path.exists():
            return
        target_dir = self.archive / sub if sub else self.archive
        self.note(f"{path.relative_to(self.root)} → Archive/v1/{sub + '/' if sub else ''}{path.name}")
        if not self.dry:
            target_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(path), str(target_dir / path.name))

    def copy_to_archive(self, path: Path, sub: str = "") -> None:
        if not path.exists():
            return
        target_dir = self.archive / sub if sub else self.archive
        self.note(f"{path.relative_to(self.root)} → Archive/v1/{sub + '/' if sub else ''}{path.name} (копия)")
        if not self.dry:
            target_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(path), str(target_dir / path.name))

    def move_to_root(self, source: Path, target: Path) -> None:
        if not source.exists():
            return
        if target.exists():
            self.note(f"{target.relative_to(self.root)} уже существует; {source.relative_to(self.root)} уходит в архив")
            self.to_archive(source, "Context")
            return
        self.note(f"{source.relative_to(self.root)} → {target.relative_to(self.root)}")
        if not self.dry:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source), str(target))

    # --- steps --------------------------------------------------------------

    def migrate_steps(self) -> list[tuple[int, dict[str, str]]]:
        steps_dir = self.root / "Steps"
        plans: dict[int, Path] = {}
        results: dict[int, Path] = {}
        for path in sorted(steps_dir.glob("*.md")) if steps_dir.is_dir() else []:
            result_match = re.fullmatch(r"Step-(\d+)-result\.md", path.name)
            if result_match:
                results[int(result_match.group(1))] = path
                continue
            plan_match = re.fullmatch(r"Step-(\d+)\.md", path.name)
            if plan_match:
                plans[int(plan_match.group(1))] = path
        merged: list[tuple[int, dict[str, str]]] = []
        for number in sorted(set(plans) | set(results)):
            plan_path = plans.get(number)
            result_path = results.get(number)
            plan_text = read(plan_path) if plan_path else ""
            result_text = read(result_path) if result_path else None
            content, meta = compose_step(number, plan_text, result_text, self.today)
            if plan_path:
                self.copy_to_archive(plan_path, "Steps")
            if result_path:
                self.to_archive(result_path, "Steps")
            target = steps_dir / f"Step-{number:02d}.md"
            self.write(target, content)
            merged.append((number, meta))
        if not steps_dir.is_dir():
            self.note("Steps/ отсутствовал — создан пустым")
            if not self.dry:
                steps_dir.mkdir(parents=True, exist_ok=True)
        return merged

    # --- knowledge ----------------------------------------------------------

    def migrate_environment_fact(self, c10: str) -> str | None:
        if not c10.strip():
            return None
        knowledge = self.root / "Knowledge"
        numbers = [
            int(match.group(1))
            for path in (knowledge.glob("F-*.md") if knowledge.is_dir() else [])
            if (match := re.match(r"^F-(\d+)", path.name))
        ]
        next_number = (max(numbers) + 1) if numbers else 1
        name = f"F-{next_number:02d}-environment.md"

        def verbatim(pattern: str, fallback: str) -> str:
            lines = section(c10, pattern)
            return "\n".join(lines) if lines else fallback

        content = "\n".join(
            [
                f"# F-{next_number:02d} — авторитетный предмет и срез",
                "",
                "**Статус:** подтверждено (перенос из v1)",
                f"**Проверено:** {self.today}, перенос из v1 (10-repo-and-revisions.md)",
                "",
                "## Утверждение",
                "",
                "Авторитетный предмет задачи и срез, к которому относятся `file:line`, числа и выводы в `Knowledge/`.",
                "",
                "## Пути",
                "",
                verbatim(r"^пути$", "Не зафиксировано при переносе."),
                "",
                "## Срез",
                "",
                verbatim(r"^срез", "Не зафиксировано при переносе."),
                "",
                "## Доказательства: команды проверки среза",
                "",
                verbatim(r"полезные команды|команды", "Не зафиксировано при переносе."),
                "",
                "## Что не проверено",
                "",
                verbatim(r"оговорка|не проверено", "Не зафиксировано при переносе."),
                "",
            ]
        )
        self.write(knowledge / name, content)
        self.register_fact(next_number, name)
        return name

    def register_fact(self, number: int, name: str) -> None:
        registry = self.root / "Knowledge" / "README.md"
        text = read(registry)
        if not text:
            self.review.append("Knowledge/README.md отсутствует — зарегистрировать факт среза вручную")
            return
        lines = text.splitlines()
        in_facts = False
        columns = 0
        last_row = None
        for index, line in enumerate(lines):
            if line.startswith("## "):
                in_facts = "факт" in line.lower()
                continue
            if in_facts and line.strip().startswith("|"):
                cells = [cell for cell in line.strip().strip("|").split("|")]
                if re.fullmatch(r"[\s|:-]+", line.strip().strip("|")):
                    columns = len(cells)
                    last_row = index
                elif re.search(r"F-\d+", line):
                    columns = columns or len(cells)
                    last_row = index
        if last_row is None or columns < 2:
            self.review.append(f"не удалось вставить строку {name} в Knowledge/README.md — добавить вручную")
            return
        middle = ["Авторитетный предмет и срез (перенос из v1)"] + ["—"] * max(0, columns - 3)
        row = "| " + " | ".join([f"`F-{number:02d}`", *middle[: columns - 2], f"[F-{number:02d}]({name})"]) + " |"
        lines.insert(last_row + 1, row)
        self.write(registry, "\n".join(lines) + ("\n" if text.endswith("\n") else ""))

    # --- README --------------------------------------------------------------

    def compose_readme(self, merged: list[tuple[int, dict[str, str]]], open_steps: list[int]) -> str:
        # At compose time the originals are still in place (README is archived later).
        v1_readme = read(self.root / "README.md")
        v1_index = read(self.root / "index.md")
        v1_steps = read(self.root / "steps.md")
        c00 = read(self.root / "Context" / "00-START-HERE.md")
        c30 = read(self.root / "Context" / "30-method.md")
        c40 = read(self.root / "Context" / "40-queue.md")
        c90 = read(self.root / "Context" / "90-session-restore.md")

        title = first_heading(v1_readme) or f"{self.root.name} — перенесённая задача"
        mode_match = re.search(r"\*\*Режим[^:]*:\*\*\s*`([^`]+)`", v1_index)
        mode = mode_match.group(1) if mode_match else "general"
        phase = field(v1_index, {"фаза"}) or field(v1_readme, {"фаза"}) or "перенесено из v1"
        blocker = field(v1_index, {"блокер"}) or field(v1_readme, {"блокер"}) or "нет"

        if open_steps:
            state = f"**Состояние:** шаг {open_steps[0]:02d} открыт · {self.today}"
        else:
            state = f"**Состояние:** открытого шага нет · ждём запрос пользователя · {self.today}"

        goal = "\n".join(section(c00, r"^задача$")) or "Постановка — в `Knowledge/F-01`."
        success = " ".join(line.strip() for line in section(c00, r"критерий успеха") if line.strip())
        if success:
            goal += f"\n\nКритерий успеха: {success}"
        f01 = next(iter(sorted((self.root / "Knowledge").glob("F-01*.md"))), None) if (self.root / "Knowledge").is_dir() else None
        if f01 is not None:
            goal += f"\n\nПолная постановка — [`Knowledge/{f01.name}`](Knowledge/{f01.name})."

        invariants = [
            "- " + line.strip().lstrip("-* ")
            for line in c00.splitlines()
            if re.match(r"^\s*[-*]?\s*INV-\d+", line)
        ]
        if not invariants:
            invariants = [
                "- INV-1. **Шаг создаётся только по запросу пользователя; открытый шаг ровно один** — `Steps/Step-NN.md` со статусом «выполняется» и без блока «Результат».",
                "- INV-2. **Любая правка долговечного файла по запросу — это шаг, даже на одну строку.** Исключения: черновик в `Notes/`, сырой вывод в `Logs/`.",
            ]

        drift_lines = [line for line in section(c90, r"drift") if line.strip().startswith("|")]
        if not drift_lines:
            drift_lines = [
                "| Проверка | Ожидание | Если изменилось |",
                "|---|---|---|",
                "| Авторитетная ревизия | не зафиксирована при переносе из v1 | перепроверить затронутые факты и `file:line` |",
                "| Новые файлы задачи | нет новее верхней строки в «Шаги» | прочитать новый шаг до работы |",
            ]

        history_rows = []
        for number, meta in sorted(merged, key=lambda item: item[0], reverse=True):
            if meta["status"] == "выполняется":
                continue
            history_rows.append(
                f"| {number:02d} | {meta['date']} | {shorten(step_title(read(self.root / 'Steps' / f'Step-{number:02d}.md')), 60)} "
                f"| {shorten(meta['verdict'], 60)} | [шаг](Steps/Step-{number:02d}.md) |"
            )
        if not history_rows:
            history_rows = ["| — | — | завершённых шагов нет | — | — |"]

        queue_items = [
            line.strip()
            for line in section(v1_steps, r"рекомендуемая очередность")
            if re.match(r"^\s*\d+\.", line)
        ] or ["1. — кандидатов пока нет; блок заполнится по мере первых наблюдений —"]

        question_rows = []
        for row in table_rows(section(c40, r"блокирующ")):
            if not row or row[0].lower() in ("id", "вопрос", "№", "#"):
                continue
            cells = row[1:] if re.fullmatch(r"Q-\d+", row[0]) else row
            cells = (cells + ["—", "—", "—"])[:3]
            question_rows.append("| " + " | ".join(cells) + " |")
        if not question_rows:
            question_rows = ["| — | — | — |"]

        forbidden = "\n".join(
            line for line in section(v1_index, r"не предлагать") if line.strip()
        ) or "—"

        method_parts = []
        for heading, body in level2_sections(c30).items():
            if heading.startswith(("факт против", "contents")):
                continue
            cleaned = body.strip()
            if cleaned and cleaned.lower() not in ("не применимо", "—"):
                method_parts.append(f"**{heading.capitalize()}:**\n\n{cleaned}")

        parts = [
            f"# {title}",
            "",
            state,
            "",
            "| | |",
            "|---|---|",
            f"| Режим | `{mode}` |",
            f"| Фаза | {phase} |",
            f"| Блокер | {blocker} |",
            "| Результаты | см. [`Results/`](Results/README.md) |",
            "",
            "Перенесено из структуры v1; оригиналы — в `Archive/v1/` (аудит их игнорирует, ссылки внутрь запрещены).",
            "",
            "## Задача",
            "",
            goal,
            "",
            "## Правила задачи",
            "",
            *invariants,
            "",
            "## Проверить при возобновлении",
            "",
            *drift_lines,
            "",
            "Замеченный дрейф записывается черновиком в `Notes/` и разбирается ближайшим шагом.",
            "",
            "## Шаги",
            "",
            "История: свежие сверху. Открытый шаг в таблице не значится — он назван в строке состояния.",
            "",
            "| Шаг | Дата | Запрос и вопрос шага | Вердикт | Файл |",
            "|---:|---|---|---|---|",
            *history_rows,
            "",
            "## Рекомендуемая очередность",
            "",
            *queue_items,
            "",
            "### Вопросы к вам",
            "",
            "| Вопрос | Почему нельзя решить самому | Умолчание |",
            "|---|---|---|",
            *question_rows,
            "",
            "## Не предлагать повторно",
            "",
            forbidden,
            "",
        ]
        if method_parts:
            parts += ["## Метод", "", "\n\n".join(method_parts), ""]
        parts += ["## Устройство папки и порядок чтения", "", FOLDER_MAP, ""]
        return "\n".join(parts)

    # --- link cleanup --------------------------------------------------------

    def cleanup_links(self) -> None:
        targets: list[Path] = []
        for top in DURABLE_TOPS:
            base = self.root / top
            if base.is_dir():
                targets.extend(sorted(base.rglob("*.md")))
        for name in DURABLE_ROOT_FILES:
            path = self.root / name
            if path.is_file():
                targets.append(path)
        for path in targets:
            text = read(path)
            updated = text
            for old, new in LINK_REPLACEMENTS:
                updated = updated.replace(old, new)
            updated = re.sub(r"Step-(\d+)-result\.md", r"Step-\1.md", updated)
            if updated != text:
                self.write(path, updated)
            for pattern in STALE_PATTERNS:
                if pattern.search(updated):
                    self.review.append(f"{path.relative_to(self.root)}: осталось упоминание {pattern.pattern}")
                    break

    # --- main ----------------------------------------------------------------

    def run(self) -> None:
        merged = self.migrate_steps()
        open_steps = sorted(number for number, meta in merged if meta["status"] == "выполняется")

        readme_content = self.compose_readme(merged, open_steps)

        context = self.root / "Context"
        env_fact = self.migrate_environment_fact(read(context / "10-repo-and-revisions.md"))

        tools = context / "tools"
        if tools.is_dir():
            root_tools = self.root / "tools"
            if not self.dry:
                root_tools.mkdir(exist_ok=True)
            for child in sorted(tools.iterdir()):
                self.move_to_root(child, root_tools / child.name)
        self.move_to_root(context / "decisions.md", self.root / "decisions.md")
        self.move_to_root(context / "change-log.md", self.root / "change-log.md")
        self.move_to_root(context / "verification-and-acceptance.md", self.root / "acceptance.md")

        self.to_archive(self.root / "README.md")
        self.write(self.root / "README.md", readme_content)
        self.to_archive(self.root / "index.md")
        self.to_archive(self.root / "steps.md")
        if context.is_dir():
            self.note("Context/ → Archive/v1/Context")
            if not self.dry:
                self.archive.mkdir(parents=True, exist_ok=True)
                shutil.move(str(context), str(self.archive / "Context"))

        env = self.root / "env.json"
        if not env.is_file():
            self.write(env, '{\n  "external_knowledge": ""\n}\n')
        for name in ("Notes", "Logs"):
            directory = self.root / name
            if not directory.is_dir():
                self.note(f"{name}/ отсутствовал — создан")
                if not self.dry:
                    directory.mkdir(parents=True, exist_ok=True)

        self.cleanup_links()

        print(f"МИГРАЦИЯ {self.root}")
        print("=" * 72)
        for line in self.log:
            print("  " + line)
        if env_fact:
            print(f"\n  Факт среза: Knowledge/{env_fact}")
        if open_steps:
            print(f"  Открытый шаг после переноса: {open_steps[0]:02d}")
        if self.review:
            print(f"\nПРОВЕРИТЬ ВРУЧНУЮ ({len(self.review)}):")
            for item in self.review:
                print("  - " + item)
        print("\nДальше:")
        print("  python3 audit_task.py <папка>   — обязан пройти без ошибок")
        print("  python3 restore_task.py <папка> — бриф по новой структуре")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Конвертировать папку задачи v1 в layout v2 (только по явному запросу)")
    parser.add_argument("task", help="TaskID или точный путь к папке задачи")
    parser.add_argument("--workspace", default=".", help="область поиска TaskID")
    parser.add_argument("--dry-run", action="store_true", help="показать план переноса, ничего не меняя")
    args = parser.parse_args(argv)

    try:
        root = resolve_task(args.task, Path(args.workspace))
    except TaskResolutionError as error:
        print(f"ОШИБКА: {error}", file=sys.stderr)
        return 2

    layout = detect_layout(root)
    if layout == "unsupported":
        die(f"структура вне канона (Process/steps/ или Steps/_next.md): {root}; перенос этой формы не автоматизирован")
    if layout == "standard":
        die(f"папка уже в структуре v2, мигрировать нечего: {root}")
    if layout == "unknown":
        die(f"это не папка задачи (нет ни v1-, ни v2-маркеров): {root}")

    Migration(root, args.dry_run).run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
