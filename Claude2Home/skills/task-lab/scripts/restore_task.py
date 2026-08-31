#!/usr/bin/env python3
"""Build a bounded recovery brief for a canonical task-lab folder."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from resolve_task import TaskResolutionError, resolve_task

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
LINK_RE = re.compile(r"\[[^\]]*\]\((?!https?:|mailto:|#)([^)\s]+)\)")
FILL_RE = re.compile(r"\{\{(?:FILL_)?[A-Z0-9_]+\}\}")
SECTIONS = (
    "task", "state", "invariants", "step", "debts", "timeline", "facts",
    "hypotheses", "kb", "questions", "changes", "forbidden", "next",
)


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def detect_layout(root: Path) -> str:
    """Canonical, unsupported (another shape), or unknown (no step surface)."""
    if (root / "Process" / "steps").exists() or (root / "Steps" / "_next.md").exists():
        return "unsupported"
    if (root / "Steps").is_dir() or (root / "steps.md").is_file():
        return "standard"
    return "unknown"


def trim(lines: list[str]) -> list[str]:
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return lines


def section(text: str, pattern: str) -> list[str]:
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
        cells = [cell.strip().strip("*").strip() for cell in line.strip().strip("|").split("|")]
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
        self.index = read(root / "index.md")
        self.start = read(root / "Context" / "00-START-HERE.md")
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
            self.line(f"  … ещё {len(items) - self.limit}; открыть реестр только при необходимости")

    def s_task(self) -> None:
        title = first_heading(self.index) or first_heading(read(self.root / "README.md")) or self.root.name
        self.line(f"БРИФ ЗАДАЧИ: {title}")
        self.line("=" * 72)
        metadata = self.index + "\n" + self.start
        mode_match = re.search(
            r"(?:^\*\*Режим(?: работы)?:\*\*\s*`([^`]+)`|^MODE:\s*`([^`]+)`)",
            metadata,
            re.IGNORECASE | re.MULTILINE,
        )
        mode = next((group for group in mode_match.groups() if group), "не указан") if mode_match else "не указан"
        count = sum(1 for _ in self.root.rglob("*.md"))
        self.line(f"  структура {self.layout} · режим {mode} · Markdown-файлов {count}")
        fill_count = sum(len(FILL_RE.findall(read(path))) for path in self.root.rglob("*.md"))
        if fill_count:
            self.line(f"  БЛОКЕР: незаполненных {{FILL_*}} маркеров {fill_count}; папка не готова к работе")

    def s_state(self) -> None:
        self.head("СОСТОЯНИЕ  (index.md)")
        rows = table_rows(section(self.index, r"состояни|state|статус"))
        items = []
        for cells in rows:
            if len(cells) < 2 or cells[0] in ("", "---"):
                continue
            items.append(f"  {shorten(cells[0].replace('*', ''), 28):<28} {shorten(' '.join(cells[1:]), 145)}")
        self.capped(items, "таблица состояния отсутствует или пуста")

    def s_invariants(self) -> None:
        self.head("ИНВАРИАНТЫ")
        items = [
            "  " + shorten(line.strip(), 155)
            for line in self.start.splitlines()
            if re.match(r"^\s*INV-\d+", line)
        ]
        self.capped(items, "не выписаны")

    def current_step(self) -> tuple[Path | None, dict[str, object]]:
        steps_dir = self.root / "Steps"
        steps: dict[int, Path] = {}
        results: set[int] = set()
        for candidate in steps_dir.glob("*.md") if steps_dir.is_dir() else []:
            match = re.fullmatch(r"Step-(\d{2,})\.md", candidate.name)
            if match:
                steps[int(match.group(1))] = candidate
                continue
            match = re.fullmatch(r"Step-(\d{2,})-result\.md", candidate.name)
            if match:
                results.add(int(match.group(1)))
        opened = sorted(set(steps) - results)
        return (steps[opened[0]] if len(opened) == 1 else None), {
            "number": opened[0] if len(opened) == 1 else None,
            "open": opened,
            "results": results & set(steps),
        }

    def s_step(self, path: Path | None, info: dict[str, object]) -> None:
        self.head("ТЕКУЩИЙ ШАГ")
        if path is None:
            opened = info.get("open") or []
            if len(opened) > 1:
                self.line(f"  КОНТРАКТ НАРУШЕН: открытых шагов {len(opened)} — {opened}")
            else:
                self.line("  открытого шага нет; ждать запроса пользователя")
            return
        self.line(f"  файл: {path.relative_to(self.root)}")
        if info.get("number") is not None:
            self.line(f"  номер: {int(info['number']):02d}")
        text = read(path)
        self.line("  " + shorten(first_heading(text), 150))
        status = field(text, {"статус", "status"})
        if status:
            self.line(f"  статус: {status}")
        question = section(text, r"^вопрос$|вопрос шага|the question|^question$")
        if question:
            self.line("  вопрос:")
            for item in question[:8]:
                if item.strip():
                    self.line("    " + shorten(item, 150))

    def latest_result(self, info: dict[str, object]) -> Path | None:
        results = info.get("results")
        if not isinstance(results, set) or not results:
            return None
        return self.root / "Steps" / f"Step-{max(results):02d}-result.md"

    def s_debts(self, info: dict[str, object]) -> None:
        latest = self.latest_result(info)
        if not latest:
            return
        block = section(read(latest), r"долг|debt")
        if not block:
            return
        self.head(f"ДОЛГИ  ({latest.name})")
        rows = table_rows(block)
        items = ["  • " + shorten(" — ".join(cell for cell in row if cell), 150) for row in rows]
        if not items:
            items = ["  " + shorten(line, 150) for line in block if line.strip()]
        self.capped(items, "нет")

    def s_timeline(self) -> None:
        text = read(self.root / "steps.md")
        if not text:
            return
        self.head("ИСТОРИЯ ШАГОВ")
        items = []
        for line in text.splitlines():
            if not line.strip().startswith("|") or re.fullmatch(r"\|[\s|:-]+\|?", line.strip()):
                continue
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if cells and cells[0].lower() in ("дата", "время", "date", "time", "шаг", "step"):
                continue
            items.append("  " + shorten(" | ".join(cells), 155))
            if len(items) >= 4:
                break
        self.capped(items, "история пуста")

    def entity_list(self, directory: str, prefix: str, status: bool) -> list[str]:
        base = self.root / directory
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
        self.capped(self.entity_list("Knowledge", "F", False), "нет")

    def s_hypotheses(self) -> None:
        self.head("ГИПОТЕЗЫ")
        self.capped(self.entity_list("Knowledge", "H", True), "нет")

    def kb_sources(self) -> list[tuple[str, str]]:
        """Rows of the env.md sources table as (path, categories)."""
        text = read(self.root / "env.md")
        if not text:
            return []
        sources: list[tuple[str, str]] = []
        for cells in table_rows(section(text, r"источник|source|знан")):
            if len(cells) < 2 or cells[0].lower() in ("тип", "type"):
                continue
            path = cells[1].strip().strip("`")
            categories = cells[2].strip() if len(cells) > 2 else "—"
            if path and path != "—":
                sources.append((path, categories))
        return sources

    def registry_entries(self, registry: Path, prefix: str) -> list[str]:
        """Category cell of every `| F-NN | категория | …` row in the base registry."""
        return [
            match.group(1).strip()
            for match in re.finditer(
                rf"^\|\s*`?{prefix}-\d+`?\s*\|([^|]*)\|", read(registry), re.MULTILINE
            )
        ]

    def s_kb(self) -> None:
        sources = self.kb_sources()
        if not sources:
            return
        self.head("ВНЕШНЯЯ БАЗА ЗНАНИЙ  (env.md)")
        for raw_path, categories in sources:
            base = Path(raw_path).expanduser()
            if not base.is_absolute():
                base = (self.root / raw_path).resolve()
            if not base.is_dir():
                self.line(f"  {raw_path} — НЕДОСТУПНА: каталога нет; проверить env.md")
                continue
            registry = base / "README.md"
            if not registry.is_file():
                self.line(f"  {raw_path} — каталог есть, но реестра README.md нет")
                continue
            facts = self.registry_entries(registry, "F")
            hypotheses = self.registry_entries(registry, "H")
            self.line(f"  {base}")
            self.line(f"  фактов {len(facts)} · гипотез {len(hypotheses)}")
            wanted = [part.strip().lower() for part in categories.split(",") if part.strip()]
            if wanted and categories.strip() != "—":
                relevant_f = sum(1 for cat in facts if cat.lower() in wanted)
                relevant_h = sum(1 for cat in hypotheses if cat.lower() in wanted)
                self.line(
                    f"  по категориям задачи ({categories}): фактов {relevant_f}, гипотез {relevant_h}"
                )

    def s_questions(self) -> None:
        text = read(self.root / "Context/40-queue.md")
        if not text:
            return
        block = section(text, r"блокирующ|открытые вопросы|вопросы к|blocking|open questions")
        rows = table_rows(block)
        items = []
        for row in rows:
            if row and row[0].lower() not in ("id", "#", "№"):
                items.append("  " + shorten(" | ".join(row), 155))
        if items:
            self.head("БЛОКИРУЮЩИЕ ВОПРОСЫ")
            self.capped(items, "нет")

    def s_changes(self) -> None:
        text = read(self.root / "Context/change-log.md")
        hits = [
            "  " + shorten(line.replace("*", ""), 150)
            for line in text.splitlines()
            if re.search(r"(?:откачено|reverted)\s*[:=|]\s*(?:нет|no)\b", line, re.I)
        ]
        if hits:
            self.head("НЕОТКАЧЕННЫЕ ИЗМЕНЕНИЯ")
            self.capped(hits, "нет")

    def s_forbidden(self) -> None:
        blocks = section(self.index, r"не предлагать|not to propose") or section(
            self.start, r"что не делать|what not to do|запрещ"
        )
        items = [
            "  " + shorten(line.lstrip("-* "), 150)
            for line in blocks
            if line.strip().startswith(("-", "*"))
        ]
        if items:
            self.head("ЧТО НЕ ПРЕДЛАГАТЬ")
            self.capped(items, "нет")

    def s_next(self, path: Path | None) -> None:
        self.head("ЧИТАТЬ ДАЛЬШЕ")
        picks: list[str] = []
        if path:
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
        restore = self.root / "Context" / "90-session-restore.md"
        if restore.is_file():
            picks.append("Context/90-session-restore.md")
        seen: set[str] = set()
        unique = [item for item in picks if not (item in seen or seen.add(item))]
        self.capped(["  " + item for item in unique], "открытого шага нет; ждать запроса пользователя")
        self.line("  Затем: audit_task.py <папка>")

    def build(self, only: str | None) -> str:
        path, info = self.current_step()
        actions = (
            ("task", self.s_task),
            ("state", self.s_state),
            ("invariants", self.s_invariants),
            ("step", lambda: self.s_step(path, info)),
            ("debts", lambda: self.s_debts(info)),
            ("timeline", self.s_timeline),
            ("facts", self.s_facts),
            ("hypotheses", self.s_hypotheses),
            ("kb", self.s_kb),
            ("questions", self.s_questions),
            ("changes", self.s_changes),
            ("forbidden", self.s_forbidden),
            ("next", lambda: self.s_next(path)),
        )
        for name, action in actions:
            if only and name not in ("task", only):
                continue
            action()
        return "\n".join(self.out)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Собрать bounded task-lab brief")
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
    if layout == "unknown":
        print(f"ОШИБКА: нет ни Steps/, ни steps.md — это не папка задачи: {root}", file=sys.stderr)
        return 2
    print(Brief(root, max(1, args.limit)).build(args.section))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
