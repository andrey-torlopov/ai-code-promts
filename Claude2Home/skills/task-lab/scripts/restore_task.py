#!/usr/bin/env python3
"""Build a bounded recovery brief for a canonical task-lab folder (layout v2)."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from audit_task import (
    CLOSED_STATUSES,
    OPEN_STATUS,
    STATE_LINE_RE,
    detect_layout,
    level2_sections,
    section_lookup,
    step_status,
)
from resolve_task import TaskResolutionError, resolve_task

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
LINK_RE = re.compile(r"\[[^\]]*\]\((?!https?:|mailto:|#)([^)\s]+)\)")
FILL_RE = re.compile(r"\{\{(?:FILL_)?[A-Z0-9_]+\}\}")
SECTIONS = (
    "task", "state", "invariants", "step", "timeline", "facts",
    "hypotheses", "kb", "queue", "forbidden", "next",
)


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def table_rows(lines: list[str]) -> list[list[str]]:
    rows: list[list[str]] = []
    started = False
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("|"):
            if started:
                break
            continue
        started = True
        if re.fullmatch(r"\|[\s|:-]+\|?", stripped):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if any(cells):
            rows.append(cells)
    return rows


def first_heading(text: str) -> str:
    for line in text.splitlines():
        match = HEADING_RE.match(line)
        if match:
            return match.group(2).strip()
    return ""


def shorten(text: str, width: int) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) <= width else text[: width - 1] + "…"


def field(text: str, names: set[str]) -> str:
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip().strip("*").strip("`").strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) >= 2 and cells[0].lower() in names:
            return re.sub(r"\s+", " ", cells[1].replace("*", "")).strip()
    for line in text.splitlines():
        match = re.match(r"\*\*([^*]+):\*\*\s*(.+)", line)
        if match and match.group(1).strip().lower() in names:
            return shorten(match.group(2), 120)
    return ""


class Brief:
    def __init__(self, root: Path, limit: int):
        self.root = root
        self.limit = limit
        self.layout = detect_layout(root)
        self.readme = read(root / "README.md")
        self.readme_sections = level2_sections(self.readme)
        self.out: list[str] = []

    def head(self, title: str) -> None:
        self.out.extend(("", title, "-" * max(24, len(title))))

    def line(self, text: str = "") -> None:
        self.out.append(text)

    def capped(self, items: list[str], empty: str) -> None:
        if not items:
            self.line(f"  ({empty})")
            return
        self.out.extend(items[: self.limit])
        if len(items) > self.limit:
            self.line(f"  … ещё {len(items) - self.limit}; открыть файл только при необходимости")

    def readme_section(self, name: str) -> str:
        return section_lookup(self.readme_sections, name) or ""

    # --- steps -------------------------------------------------------------

    def scan_steps(self) -> tuple[dict[int, Path], list[int], list[int]]:
        steps_dir = self.root / "Steps"
        files: dict[int, Path] = {}
        opened: list[int] = []
        closed: list[int] = []
        for candidate in sorted(steps_dir.glob("*.md")) if steps_dir.is_dir() else []:
            match = re.fullmatch(r"Step-(\d{2,})\.md", candidate.name)
            if not match:
                continue
            number = int(match.group(1))
            files[number] = candidate
            status = step_status(read(candidate))
            if status == OPEN_STATUS:
                opened.append(number)
            elif status in CLOSED_STATUSES:
                closed.append(number)
        return files, sorted(opened), sorted(closed)

    # --- sections ----------------------------------------------------------

    def s_task(self) -> None:
        title = first_heading(self.readme) or self.root.name
        self.line(f"БРИФ ЗАДАЧИ: {title}")
        self.line("=" * 72)
        mode = field(self.readme, {"режим", "mode"}) or "не указан"
        count = sum(1 for _ in self.root.rglob("*.md"))
        self.line(f"  структура {self.layout} · режим {mode} · Markdown-файлов {count}")
        fill_count = 0
        for path in self.root.rglob("*.md"):
            if "Archive" in path.relative_to(self.root).parts:
                continue
            fill_count += len(FILL_RE.findall(read(path)))
        if fill_count:
            self.line(f"  БЛОКЕР: незаполненных {{FILL_*}} маркеров {fill_count}; папка не готова к работе")

    def s_state(self) -> None:
        self.head("СОСТОЯНИЕ  (README.md)")
        state = STATE_LINE_RE.search(self.readme)
        if state:
            self.line(f"  {state.group(1)}")
        else:
            self.line("  строка «**Состояние:** …» отсутствует — аудит обязан быть красным")
        for label in ("фаза", "блокер", "результаты"):
            value = field(self.readme, {label})
            if value:
                self.line(f"  {label:<10} {shorten(value, 150)}")

    def s_invariants(self) -> None:
        self.head("ПРАВИЛА ЗАДАЧИ")
        items = [
            "  " + shorten(line.strip().lstrip("-* "), 155)
            for line in self.readme_section("правила задачи").splitlines()
            if re.match(r"^\s*[-*]?\s*INV-\d+", line)
        ]
        self.capped(items, "не выписаны")

    def s_step(self) -> None:
        files, opened, closed = self.scan_steps()
        self.head("ТЕКУЩИЙ ШАГ")
        if len(opened) > 1:
            self.line(f"  КОНТРАКТ НАРУШЕН: открытых шагов {len(opened)} — {opened}")
            return
        if opened:
            number = opened[0]
            path = files[number]
            text = read(path)
            self.line(f"  файл: {path.relative_to(self.root)}")
            self.line(f"  номер: {number:02d}")
            self.line("  " + shorten(first_heading(text), 150))
            request = section_lookup(level2_sections(text), "запрос") or ""
            if request.strip():
                self.line("  запрос:")
                for item in request.splitlines()[:6]:
                    if item.strip():
                        self.line("    " + shorten(item, 150))
            return
        self.line("  открытого шага нет; ждать запроса пользователя")
        if not closed:
            return
        number = max(closed)
        path = files[number]
        text = read(path)
        self.line(f"  чекпойнт: {path.relative_to(self.root)} — {shorten(first_heading(text), 110)}")
        verdict = field(text, {"вердикт"})
        if verdict:
            self.line(f"  вердикт: {shorten(verdict, 150)}")
        knowledge = section_lookup(level2_sections(text), "задействованные знания") or ""
        rows = table_rows(knowledge.splitlines())
        for row in rows[:4]:
            if row and row[0].lower() not in ("id", "—"):
                self.line("    знание: " + shorten(" — ".join(cell for cell in row if cell), 140))

    def s_timeline(self) -> None:
        history = self.readme_section("шаги")
        if not history.strip():
            return
        self.head("ИСТОРИЯ ШАГОВ  (README «Шаги»)")
        items = []
        for row in table_rows(history.splitlines()):
            if row and row[0].lower() in ("шаг", "step", "дата", "date"):
                continue
            items.append("  " + shorten(" | ".join(row), 155))
            if len(items) >= 4:
                break
        self.capped(items, "история пуста")

    def entity_list(self, prefix: str, status: bool) -> list[str]:
        base = self.root / "Knowledge"
        if not base.is_dir():
            return []
        pattern = re.compile(rf"^{prefix}-(\d+)")
        items: list[tuple[int, str]] = []
        for path in base.glob("*.md"):
            if path.name.endswith("_context.md"):
                continue
            match = pattern.match(path.name)
            if not match:
                continue
            text = read(path)
            title = re.sub(rf"^{prefix}-\d+[.\s—-]*", "", first_heading(text)).strip()
            number = int(match.group(1))
            state = field(text, {"статус", "status"}) if status else ""
            state_text = f" [{shorten(state, 24)}]" if state else ""
            items.append((number, f"  {prefix}-{number:02d}{state_text}  {shorten(title, 110)}"))
        return [item for _, item in sorted(items)]

    def s_facts(self) -> None:
        self.head("ФАКТЫ")
        self.capped(self.entity_list("F", False), "нет")

    def s_hypotheses(self) -> None:
        self.head("ГИПОТЕЗЫ")
        self.capped(self.entity_list("H", True), "нет")

    def kb_pointer(self) -> str | None:
        """The external_knowledge path from root env.json, or None when unset."""
        raw = read(self.root / "env.json")
        if not raw:
            return None
        try:
            data = json.loads(raw)
        except ValueError:
            return None
        value = data.get("external_knowledge", data.get("external_knoledge", "")) if isinstance(data, dict) else ""
        return value.strip() if isinstance(value, str) and value.strip() else None

    def registry_entries(self, text: str, prefix: str) -> list[str]:
        """Tags cell of every `| [F-NN](file.md) | tags | …` registry row."""
        return [
            match.group(1).strip()
            for match in re.finditer(
                rf"^\|\s*\[?`?{prefix}-\d+[^|]*\|([^|]*)\|", text, re.MULTILINE
            )
        ]

    def s_kb(self) -> None:
        raw_path = self.kb_pointer()
        if raw_path is None:
            return
        self.head("ВНЕШНЯЯ БАЗА ЗНАНИЙ  (env.json)")
        base = Path(raw_path).expanduser()
        if not base.is_absolute():
            base = (self.root / raw_path).resolve()
        if not base.is_dir():
            self.line(f"  {raw_path} — НЕДОСТУПНА: каталога нет; проверить env.json")
            return
        registry = base / "README.md"
        if not registry.is_file():
            self.line(f"  {raw_path} — каталог есть, но реестра README.md нет")
            return
        text = read(registry)
        facts = self.registry_entries(text, "F")
        hypotheses = self.registry_entries(text, "H")
        self.line(f"  {base}")
        self.line(f"  фактов {len(facts)} · гипотез {len(hypotheses)}")
        tags: dict[str, int] = {}
        for cell in facts + hypotheses:
            for tag in cell.split(","):
                tag = tag.strip()
                if tag and tag != "—":
                    tags[tag] = tags.get(tag, 0) + 1
        if tags:
            ranked = sorted(tags.items(), key=lambda item: (-item[1], item[0]))
            self.line("  теги: " + " · ".join(f"{name} {count}" for name, count in ranked[: self.limit]))
        legacy = [
            line
            for line in text.splitlines()
            if re.match(r"^\|\s*\[(?!F-\d|H-\d)[^\]]*\]\([^)]+\)", line)
        ]
        if legacy:
            self.line(
                f"  строк реестра без ID: {len(legacy)} — формат не приведён к контракту "
                "(ID | Tags | Описание | Источник / срез); конвертация — отдельная задача"
            )

    def s_queue(self) -> None:
        block = self.readme_section("рекомендуемая очередность")
        if not block.strip():
            return
        self.head("РЕКОМЕНДУЕМАЯ ОЧЕРЕДНОСТЬ")
        items = [
            "  " + shorten(line.strip(), 155)
            for line in block.splitlines()
            if re.match(r"^\s*\d+\.", line)
        ]
        self.capped(items, "кандидатов нет")
        questions = []
        in_questions = False
        for line in block.splitlines():
            if re.match(r"^###\s+вопросы", line.strip(), re.IGNORECASE):
                in_questions = True
                continue
            if in_questions and line.startswith("###"):
                break
            if in_questions:
                questions.append(line)
        rows = [
            "  ? " + shorten(" | ".join(row), 150)
            for row in table_rows(questions)
            if row and row[0].lower() not in ("вопрос", "question")
        ]
        if rows:
            self.line("  Блокирующие вопросы:")
            self.out.extend(rows[: self.limit])

    def s_forbidden(self) -> None:
        block = self.readme_section("не предлагать повторно")
        items = [
            "  " + shorten(line.strip().lstrip("-* "), 150)
            for line in block.splitlines()
            if line.strip() and not line.strip().lower().startswith("подробности")
        ]
        if items:
            self.head("ЧТО НЕ ПРЕДЛАГАТЬ")
            self.capped(items, "нет")

    def s_next(self) -> None:
        files, opened, _ = self.scan_steps()
        self.head("ЧИТАТЬ ДАЛЬШЕ")
        picks: list[str] = ["README.md, целиком"]
        if len(opened) == 1:
            path = files[opened[0]]
            picks.append(str(path.relative_to(self.root)))
            for target in LINK_RE.findall(read(path)):
                clean = target.split("#", 1)[0]
                resolved = (path.parent / clean).resolve()
                if not resolved.is_file():
                    continue
                try:
                    picks.append(str(resolved.relative_to(self.root)))
                except ValueError:
                    continue
        else:
            picks.append("последний закрытый Steps/Step-NN.md — чекпойнт (вердикт + знания)")
        seen: set[str] = set()
        unique = [item for item in picks if not (item in seen or seen.add(item))]
        self.capped(["  " + item for item in unique], "открытого шага нет; ждать запроса пользователя")
        self.line("  Затем: audit_task.py <папка>")

    def build(self, only: str | None) -> str:
        actions = (
            ("task", self.s_task),
            ("state", self.s_state),
            ("invariants", self.s_invariants),
            ("step", self.s_step),
            ("timeline", self.s_timeline),
            ("facts", self.s_facts),
            ("hypotheses", self.s_hypotheses),
            ("kb", self.s_kb),
            ("queue", self.s_queue),
            ("forbidden", self.s_forbidden),
            ("next", self.s_next),
        )
        for name, action in actions:
            if only and name not in ("task", only):
                continue
            action()
        return "\n".join(self.out)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Собрать bounded task-lab brief (layout v2)")
    parser.add_argument("task", help="TaskID или точный путь к папке задачи")
    parser.add_argument("--workspace", default=".", help="область поиска TaskID")
    parser.add_argument("--limit", type=int, default=14)
    parser.add_argument("--section", choices=SECTIONS, default=None)
    args = parser.parse_args(argv)

    try:
        root = resolve_task(args.task, Path(args.workspace))
    except TaskResolutionError as error:
        print(f"ОШИБКА: {error}", file=sys.stderr)
        return 2
    layout = detect_layout(root)
    if layout == "unsupported":
        print(
            f"ОШИБКА: структура папки вне канона (найдены Process/steps/ или Steps/_next.md): {root}\n"
            "Скилл работает только с канонической структурой; перенос — отдельная явная задача.",
            file=sys.stderr,
        )
        return 2
    if layout == "legacy":
        print(
            f"ОШИБКА: структура v1 (index.md / steps.md / Context/): {root}\n"
            "Скилл читает только v2. Конвертация выполняется явно: python3 migrate_task.py <TaskID>.",
            file=sys.stderr,
        )
        return 2
    if layout == "unknown":
        print(
            f"ОШИБКА: нет ни Steps/, ни README.md со строкой состояния — это не папка задачи: {root}",
            file=sys.stderr,
        )
        return 2
    print(Brief(root, max(1, args.limit)).build(args.section))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
