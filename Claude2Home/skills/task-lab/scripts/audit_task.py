#!/usr/bin/env python3
"""Audit a task-lab folder against the single canonical structure (layout v2).

Exit codes: 0 = no errors, 1 = errors (or warnings with --pedantic),
2 = unreadable/ambiguous folder.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from resolve_task import TaskResolutionError, resolve_task

ERROR, WARN = "ОШИБКА", "ВНИМАНИЕ"

EVIDENCE_MARKERS = (
    "чем подтверждено",
    "доказательств",
    "доказательство",
    "как получен",
    "как измерен",
    "замер",
    "расчёт",
    "расчет",
    "evidence",
    "confirmed by",
    "подтверждено:",
)
H_GROUPS = (
    ("статус", ("статус", "status")),
    ("вопрос/механизм", ("вопрос", "суть", "механизм", "question", "essence", "mechanism")),
    ("проверка", ("как провер", "гейт", "gate", "what closes", "check", "чем закрывается")),
    (
        "исходы/ожидаемый эффект",
        ("что следует из каждого исхода", "ожидаемый эффект", "expected effect", "outcome", "вердикт"),
    ),
)

PRUNE_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", ".idea"}
BUNDLE_EXT = (".trace", ".logarchive", ".xcresult", ".dSYM", ".app", ".framework")
SCRIPT_EXT = {".py", ".sh", ".bash", ".zsh", ".rb", ".js", ".mjs", ".pl", ".swift"}
OBSERVATION_EXT = {".trace", ".logarchive", ".xcresult", ".log", ".csv", ".har", ".nettrace"}
IGNORED_NAMES = {".DS_Store", ".gitignore", ".gitkeep", ".markdownlint.yaml"}

CANONICAL_DIRS = ("Knowledge", "Steps", "Results", "tools", "Notes", "Logs", "Inbox", "Archive")
OPTIONAL_ROOT_FILES = ("decisions.md", "change-log.md", "acceptance.md")
# The single synchronized projection: edited while a step opens/closes, so it is
# legitimately newer than the closed step files.
PROJECTION_FILES = ("README.md",)
# Two root siblings, never nested: Notes/ is human scratch, Logs/ is machine output.
SCRATCH_DIRS = ("Notes", "Logs")
# Scratch, inbound and archived material are exempt from the "every edit is a step" rule.
UNTRACKED_DIRS = SCRATCH_DIRS + ("Inbox", "Archive")
EDIT_TOLERANCE_SECONDS = 15 * 60
SCRIPT_DIRS = (("tools",), ("Inbox",), ("Notes",))
# Raw captured output belongs in root Logs/; Inbox/ may carry it as inbound material;
# tools/ may hold tables its scripts produce.
OBSERVATION_DIRS = ("Logs", "Inbox", "tools")
FOREIGN_MARKERS = (
    ("Process/steps", "Process/steps/", "шаги живут в Steps/ как Step-NN.md"),
    ("Steps/_next.md", "Steps/_next.md", "текущий шаг — это Step-NN.md со статусом «выполняется»"),
)
LEGACY_MARKERS = (
    ("index.md", "index.md"),
    ("steps.md", "steps.md"),
    ("Context", "Context/"),
)
RETIRED_DIRS = (
    ("Tools", "скрипты задачи живут в tools/ (нижний регистр)"),
    ("Traces", "сырой вывод живёт в корневой Logs/, журналы наблюдений — в Notes/"),
    ("Hypotheses", "гипотезы живут в Knowledge/ как H-NN-*.md"),
)

OPEN_STATUS = "выполняется"
CLOSED_STATUSES = {"завершён", "завершен", "отменён", "отменен", "заблокирован"}

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
WIKI_LINK_RE = re.compile(r"\[\[([^\]|#]+)")
FILL_RE = re.compile(r"\{\{(?:FILL_)?[A-Z0-9_]+\}\}")
LEGACY_FILL_RE = re.compile(
    r"<[^>\n]*(?:task-specific|what\b|describe|fill|metric|value|branch|sha|pin|repo|path|"
    r"command|condition|every trap|опис|заполн|указать|чем)[^>\n]*>",
    re.IGNORECASE,
)
DATE_HEAD_RE = re.compile(r"^##\s+(\d{4})-(\d{2})-(\d{2})")
TIME_RE = re.compile(r"^[~]?(\d{1,2}):(\d{2})")
TABLE_STAMP_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})(?:[ T](\d{2}):(\d{2}))?$")
INBOX_PATH_RE = re.compile(r"(?:^|[\s`(\[])(?:\.\./)*Inbox/[A-Za-z0-9_.-]+")
RESULT_EXTERNAL_RE = re.compile(
    r"(?:^|[\s`(\[])(?:\.\./)*(?:Context|Knowledge|Steps|Inbox|tools|Archive)/[A-Za-z0-9_.-]+"
)
STATUS_RE = re.compile(r"^\*\*Статус:\*\*\s*(.+)$", re.MULTILINE)
VERDICT_RE = re.compile(r"^\s*\*\*Вердикт:\*\*", re.MULTILINE)
STATE_LINE_RE = re.compile(r"^\*\*Состояние:\*\*\s*(.+?)\s*$", re.MULTILINE)
STATE_OPEN_RE = re.compile(r"^шаг\s+0*(\d+)\s+открыт\s*·\s*\d{4}-\d{2}-\d{2}$")
STATE_WAIT_RE = re.compile(
    r"^открытого шага нет\s*·\s*ждём запрос(?:а)? пользователя\s*·\s*\d{4}-\d{2}-\d{2}$"
)
STEP_ROW_NUMBER_RE = re.compile(r"^(?:\[)?(?:шаг\s*|step[- ]*)?0*(\d+)(?:\]|\s|$)", re.IGNORECASE)
ENTITY_ID_RE = re.compile(r"\b([FH])-0*(\d+)\b")

README_SECTIONS = (
    "задача",
    "правила задачи",
    "проверить при возобновлении",
    "шаги",
    "рекомендуемая очередность",
    "не предлагать повторно",
    "устройство папки",
)
STEP_OPEN_SECTIONS = ("запрос", "план")
STEP_CLOSE_SECTIONS = ("запрос", "план", "что сделано", "результат", "задействованные знания")


@dataclass
class Finding:
    level: str
    code: str
    where: str
    message: str


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def strip_fences(text: str) -> list[tuple[int, str]]:
    result: list[tuple[int, str]] = []
    fence = False
    for number, line in enumerate(text.splitlines(), 1):
        if line.lstrip().startswith(("```", "~~~")):
            fence = not fence
            continue
        if not fence:
            result.append((number, line))
    return result


def has_any(text_lower: str, markers: tuple[str, ...]) -> bool:
    return any(marker in text_lower for marker in markers)


def level2_sections(text: str) -> dict[str, str]:
    """Map of level-2 heading (lowercased) -> section body, fences stripped."""
    result: dict[str, str] = {}
    current: str | None = None
    accumulated: list[str] = []
    for _, line in strip_fences(text):
        heading = HEADING_RE.match(line)
        if heading and len(heading.group(1)) <= 2:
            if current is not None:
                result[current] = "\n".join(accumulated)
            current = heading.group(2).strip().lower() if len(heading.group(1)) == 2 else None
            accumulated = []
            continue
        if current is not None:
            accumulated.append(line)
    if current is not None:
        result[current] = "\n".join(accumulated)
    return result


def section_lookup(sections: dict[str, str], name: str) -> str | None:
    for heading, body in sections.items():
        if heading.startswith(name):
            return body
    return None


def step_status(text: str) -> str | None:
    match = STATUS_RE.search(text)
    if not match:
        return None
    value = match.group(1).split("·", 1)[0]
    return value.strip().strip(".").lower()


def detect_layout(root: Path) -> str:
    """standard (v2), legacy (v1), unsupported (foreign shape) or unknown."""
    for relative, _, _ in FOREIGN_MARKERS:
        if (root / relative).exists():
            return "unsupported"
    for relative, _ in LEGACY_MARKERS:
        if (root / relative).exists():
            return "legacy"
    if (root / "Steps").is_dir():
        return "standard"
    if STATE_LINE_RE.search(read(root / "README.md")):
        return "standard"
    return "unknown"


class Audit:
    def __init__(self, root: Path, pedantic: bool):
        self.root = root
        self.pedantic = pedantic
        self.findings: list[Finding] = []
        self.entries = self.walk()
        self.md = sorted(path for path in self.entries if path.is_file() and path.suffix == ".md")
        self.stats: dict[str, object] = {}
        self.layout = detect_layout(root)
        self.current_step: int | None = None
        self.completed_steps: set[int] = set()
        self.step_files: dict[int, Path] = {}
        self.kb_dirs: list[Path] = []

    def walk(self) -> list[Path]:
        result: list[Path] = []
        stack = [self.root]
        while stack:
            try:
                entries = sorted(stack.pop().iterdir())
            except OSError:
                continue
            for entry in entries:
                if entry.is_dir() and not entry.is_symlink():
                    if entry.name in PRUNE_DIRS:
                        continue
                    if entry.name.endswith(BUNDLE_EXT):
                        result.append(entry)
                    else:
                        stack.append(entry)
                else:
                    result.append(entry)
        return result

    def relative(self, path: Path | str) -> str:
        if isinstance(path, str):
            return path
        try:
            return str(path.relative_to(self.root))
        except ValueError:
            return str(path)

    def top(self, path: Path) -> str:
        parts = path.relative_to(self.root).parts
        return parts[0] if parts else ""

    def add(self, level: str, code: str, where: Path | str, message: str) -> None:
        self.findings.append(Finding(level, code, self.relative(where), message))

    def entity_files(self, prefix: str, recursive: bool = False) -> list[tuple[int, Path]]:
        base = self.root / "Knowledge"
        if not base.is_dir():
            return []
        iterator = base.rglob("*.md") if recursive else base.glob("*.md")
        pattern = re.compile(rf"^{prefix}-(\d+)")
        result: list[tuple[int, Path]] = []
        for path in sorted(iterator):
            if path.name.endswith("_context.md"):
                continue
            match = pattern.match(path.name)
            if match:
                result.append((int(match.group(1)), path))
        return result

    # --- structure ---------------------------------------------------------

    def check_surface(self) -> None:
        if self.layout == "unsupported":
            for relative, label, hint in FOREIGN_MARKERS:
                if (self.root / relative).exists():
                    self.add(
                        ERROR,
                        "unsupported-layout",
                        label,
                        f"структура вне канона; {hint}. Перенос — отдельная явная задача, "
                        "молча мигрировать нельзя",
                    )
            return
        if self.layout == "legacy":
            found = [label for relative, label in LEGACY_MARKERS if (self.root / relative).exists()]
            self.add(
                ERROR,
                "legacy-layout",
                ", ".join(found),
                "структура v1 (index.md / steps.md / Context/); скилл читает только v2. "
                "Конвертация выполняется явно: python3 migrate_task.py <TaskID>",
            )
            return
        if self.layout == "unknown":
            self.add(
                ERROR,
                "unknown-layout",
                self.root,
                "нет ни Steps/, ни README.md со строкой «**Состояние:** …»: это не папка задачи",
            )
            return
        required = ("README.md", "Knowledge/README.md", "Results/README.md")
        if not (self.root / "Steps").is_dir():
            self.add(ERROR, "surface-missing", "Steps/", "обязательный каталог отсутствует")
        for relative in required:
            if not (self.root / relative).is_file():
                self.add(ERROR, "surface-missing", relative, "обязательная точка структуры отсутствует")
        # Compare by real names: on a case-insensitive filesystem Path("Tools").is_dir()
        # would match the canonical tools/ and produce a false warning.
        root_dir_names = {entry.name for entry in self.root.iterdir() if entry.is_dir()}
        for relative, hint in RETIRED_DIRS:
            if relative in root_dir_names:
                self.add(WARN, "retired-dir", relative + "/", f"папки нет в канонической структуре: {hint}")
        for nested in sorted(self.root.rglob("Logs")):
            if not nested.is_dir() or nested == self.root / "Logs":
                continue
            relative_parts = nested.relative_to(self.root).parts
            if any(part in PRUNE_DIRS for part in relative_parts) or relative_parts[0] == "Archive":
                continue
            self.add(
                ERROR,
                "logs-nested",
                nested,
                "Logs/ — корневая папка на одном уровне с Notes/; вложенную копию скилл не читает",
            )
        known = set(CANONICAL_DIRS) | {name for name, _ in RETIRED_DIRS} | {"Process"}
        for entry in sorted(self.root.iterdir()):
            if not entry.is_dir() or entry.name.startswith(".") or entry.name in known:
                continue
            self.add(
                WARN,
                "unknown-dir",
                entry.name + "/",
                "каталог вне канонической структуры: "
                + ", ".join(name + "/" for name in CANONICAL_DIRS if name != "Archive"),
            )

    def check_env(self) -> None:
        """Validate root env.json and resolve the external knowledge base it names."""
        path = self.root / "env.json"
        if not path.is_file():
            self.add(
                ERROR,
                "env-missing",
                "env.json",
                'обязательный файл-указатель отсутствует; создать {"external_knowledge": ""}',
            )
            return
        try:
            data = json.loads(read(path))
        except ValueError:
            self.add(ERROR, "env-format", path, "не парсится как JSON")
            return
        if not isinstance(data, dict) or (
            "external_knowledge" not in data and "external_knoledge" not in data
        ):
            self.add(ERROR, "env-format", path, 'нет ключа "external_knowledge"')
            return
        value = data.get("external_knowledge", data.get("external_knoledge"))
        if not isinstance(value, str):
            self.add(ERROR, "env-format", path, '"external_knowledge" должен быть строкой; пустая строка — базы нет')
            return
        raw = value.strip()
        if not raw:
            return
        base = Path(raw).expanduser()
        if not base.is_absolute():
            base = self.root / raw
        base = base.resolve()
        if not base.is_dir():
            self.add(WARN, "kb-unreachable", path, f"путь внешней базы не разрешается: {raw}")
            return
        self.kb_dirs.append(base)
        self.stats["внешняя база"] = str(base)
        if not (base / "README.md").is_file():
            self.add(WARN, "kb-no-registry", path, f"во внешней базе нет реестра README.md: {raw}")

    def check_placeholders(self) -> None:
        for path in self.md:
            parts = path.relative_to(self.root).parts
            if any(name in parts for name in UNTRACKED_DIRS):
                continue
            hits: list[str] = []
            text = read(path)
            hits.extend(FILL_RE.findall(text))
            hits.extend(LEGACY_FILL_RE.findall(text))
            if "ЧЧ:ММ" in text:
                hits.append("ЧЧ:ММ")
            if hits:
                shown = ", ".join(sorted(set(hits))[:6])
                self.add(ERROR, "placeholder", path, f"незаполненные маркеры шаблона: {shown}")

    # --- steps -------------------------------------------------------------

    def check_steps(self) -> None:
        steps_dir = self.root / "Steps"
        open_steps: list[int] = []
        for path in sorted(steps_dir.glob("*.md")) if steps_dir.is_dir() else []:
            legacy = re.fullmatch(r"Step-(\d+)-result\.md", path.name, re.IGNORECASE)
            if legacy:
                self.add(
                    ERROR,
                    "legacy-step-file",
                    path,
                    "результат живёт блоком «Результат» внутри Step-NN.md; "
                    "файл v1 переносится через migrate_task.py",
                )
                continue
            match = re.fullmatch(r"Step-(\d{2,})\.md", path.name)
            if not match:
                if re.match(r"step-", path.name, re.IGNORECASE):
                    self.add(ERROR, "step-name", path, "ожидается Step-NN.md с номером 01, 02, …")
                continue
            number = int(match.group(1))
            if number in self.step_files:
                self.add(ERROR, "duplicate-step", path, f"номер шага {number:02d} уже занят")
                continue
            self.step_files[number] = path
            text = read(path)
            sections = level2_sections(text)
            status = step_status(text)
            has_result = section_lookup(sections, "результат") is not None
            if status is None:
                self.add(ERROR, "step-status-unknown", path, "нет строки «**Статус:** …»")
                continue
            if status == OPEN_STATUS:
                if has_result:
                    self.add(
                        ERROR,
                        "step-status-mismatch",
                        path,
                        "статус «выполняется», но блок «Результат» уже есть — закрыть статусом "
                        "завершён/отменён/заблокирован",
                    )
                missing = [name for name in STEP_OPEN_SECTIONS if section_lookup(sections, name) is None]
                if missing:
                    self.add(ERROR, "step-sections", path, "у открытого шага нет секций: " + ", ".join(missing))
                open_steps.append(number)
            elif status in CLOSED_STATUSES:
                missing = [name for name in STEP_CLOSE_SECTIONS if section_lookup(sections, name) is None]
                if missing:
                    self.add(ERROR, "step-sections", path, f"у закрытого шага ({status}) нет секций: " + ", ".join(missing))
                result_body = section_lookup(sections, "результат")
                if result_body is not None and not VERDICT_RE.search(result_body):
                    self.add(ERROR, "step-verdict", path, "блок «Результат» не начинается с «**Вердикт:** …»")
                self.completed_steps.add(number)
            else:
                self.add(
                    ERROR,
                    "step-status-unknown",
                    path,
                    f"статус {status!r}; допустимо: выполняется, завершён, отменён, заблокирован",
                )
                continue
            if "критерий завершения" not in text.lower():
                self.add(WARN, "step-plan-incomplete", path, "в «План» не зафиксирован критерий завершения")

        if len(open_steps) > 1:
            self.add(ERROR, "many-open-steps", steps_dir, f"открытых шагов {len(open_steps)}: {sorted(open_steps)}")
        elif open_steps:
            self.current_step = open_steps[0]

        numbers = set(self.step_files)
        if numbers:
            missing_numbers = sorted(set(range(1, max(numbers) + 1)) - numbers)
            if missing_numbers:
                self.add(
                    ERROR,
                    "step-gap",
                    steps_dir,
                    "нет Step-файлов: " + ", ".join(f"{n:02d}" for n in missing_numbers),
                )
            if self.current_step is not None and self.current_step != max(numbers):
                self.add(
                    ERROR,
                    "open-step-not-latest",
                    self.step_files[self.current_step],
                    "открытый шаг должен иметь наибольший номер",
                )
        self.stats["шагов всего"] = len(self.step_files)
        self.stats["шагов завершено"] = len(self.completed_steps)
        self.stats["текущий шаг"] = self.current_step if self.current_step is not None else "нет — ожидается запрос"

    def check_readme(self) -> None:
        readme = self.root / "README.md"
        if not readme.is_file():
            return
        text = read(readme)
        sections = level2_sections(text)

        missing = [name for name in README_SECTIONS if section_lookup(sections, name) is None]
        if missing:
            self.add(ERROR, "readme-section-missing", readme, "нет обязательных секций: " + ", ".join(missing))

        state = STATE_LINE_RE.search(text)
        if not state:
            self.add(
                ERROR,
                "state-line",
                readme,
                "нет строки состояния «**Состояние:** …» — единственного указателя на текущий шаг",
            )
        else:
            content = state.group(1)
            open_match = STATE_OPEN_RE.match(content)
            wait_match = STATE_WAIT_RE.match(content)
            if not open_match and not wait_match:
                self.add(
                    ERROR,
                    "state-line",
                    readme,
                    f"строка состояния не разбирается: {content!r}; ожидается "
                    "«шаг NN открыт · YYYY-MM-DD» или «открытого шага нет · ждём запрос пользователя · YYYY-MM-DD»",
                )
            elif open_match:
                claimed = int(open_match.group(1))
                if self.current_step is None:
                    self.add(
                        ERROR,
                        "state-line-mismatch",
                        readme,
                        f"строка состояния называет открытым шаг {claimed:02d}, но открытого шага нет",
                    )
                elif claimed != self.current_step:
                    self.add(
                        ERROR,
                        "state-line-mismatch",
                        readme,
                        f"строка состояния называет шаг {claimed:02d}, фактически открыт {self.current_step:02d}",
                    )
            elif wait_match and self.current_step is not None:
                self.add(
                    ERROR,
                    "state-line-mismatch",
                    readme,
                    f"строка состояния говорит «открытого шага нет», но открыт шаг {self.current_step:02d}",
                )

        history = section_lookup(sections, "шаги")
        if history is None:
            return
        numbers: list[int] = []
        for line in history.splitlines():
            if not line.strip().startswith("|"):
                continue
            cells = [cell.strip().replace("*", "") for cell in line.strip().strip("|").split("|")]
            for cell in cells[:2]:
                match = STEP_ROW_NUMBER_RE.match(cell)
                if match:
                    numbers.append(int(match.group(1)))
                    break
        if any(upper < lower for upper, lower in zip(numbers, numbers[1:])):
            self.add(ERROR, "readme-steps-order", readme, "история в «Шаги» должна идти по убыванию: последние сверху")
        for number in sorted(self.completed_steps):
            if number in numbers or f"Step-{number:02d}.md" in history:
                continue
            self.add(
                ERROR,
                "readme-steps-missing",
                readme,
                f"закрытый шаг {number:02d} отсутствует в таблице «Шаги»",
            )
        if self.current_step is not None and self.current_step in numbers:
            self.add(
                WARN,
                "readme-steps-open",
                readme,
                f"открытый шаг {self.current_step:02d} значится в истории; его место — строка состояния",
            )

    def check_footer_knowledge(self) -> None:
        known = {("F", number) for number, _ in self.entity_files("F", recursive=True)}
        known |= {("H", number) for number, _ in self.entity_files("H", recursive=True)}
        referenced: set[tuple[str, int]] = set()
        for number in sorted(self.completed_steps):
            path = self.step_files[number]
            body = section_lookup(level2_sections(read(path)), "задействованные знания")
            if body is None:
                continue
            for prefix, digits in ENTITY_ID_RE.findall(body):
                entity = (prefix, int(digits))
                referenced.add(entity)
                if entity not in known:
                    self.add(
                        ERROR,
                        "footer-knowledge",
                        path,
                        f"{prefix}-{int(digits):02d} из «Задействованные знания» не существует в Knowledge/",
                    )
        if not self.pedantic:
            return
        for prefix in ("F", "H"):
            for number, path in self.entity_files(prefix):
                if (prefix, number) in referenced:
                    continue
                if prefix == "F" and (number in (1, 2) or "environment" in path.name):
                    continue
                self.add(
                    WARN,
                    "knowledge-unreferenced",
                    path,
                    "утверждение не названо ни в одном футере «Задействованные знания»",
                )

    def check_edits_outside_step(self) -> None:
        """Durable files touched after the last step closed, with no step open.

        Heuristic: it reads modification times, so a checkout or a copy can move
        them. It is a WARN for that reason — but it is the only mechanical signal
        that a report was edited without a request-bound step.
        """
        if self.layout != "standard" or self.current_step is not None or not self.completed_steps:
            return
        closed_files = [self.step_files[number] for number in self.completed_steps if self.step_files[number].is_file()]
        if not closed_files:
            return
        newest = max(path.stat().st_mtime for path in closed_files)
        newest_name = max(closed_files, key=lambda path: path.stat().st_mtime).name
        late: list[tuple[float, str]] = []
        for path in self.entries:
            if not path.is_file() or path.name in IGNORED_NAMES:
                continue
            relative = path.relative_to(self.root)
            posix = relative.as_posix()
            if relative.parts[0] in UNTRACKED_DIRS or posix in PROJECTION_FILES:
                continue
            try:
                mtime = path.stat().st_mtime
            except OSError:
                continue
            if mtime > newest + EDIT_TOLERANCE_SECONDS:
                late.append((mtime, posix))
        if not late:
            return
        late.sort(reverse=True)
        shown = ", ".join(name for _, name in late[:3])
        more = f" и ещё {len(late) - 3}" if len(late) > 3 else ""
        self.add(
            WARN,
            "edit-outside-step",
            self.root,
            f"файлов изменено после закрытия последнего шага ({newest_name}): {len(late)} — {shown}{more}. "
            "Правка по запросу пользователя оформляется своим шагом; проверка идёт по времени файла",
        )

    # --- knowledge ---------------------------------------------------------

    def check_facts_and_hypotheses(self) -> None:
        facts = self.entity_files("F")
        hypotheses = self.entity_files("H")
        self.stats["фактов"] = len(facts)
        self.stats["гипотез"] = len(hypotheses)
        for _, path in facts:
            if not has_any(read(path).lower(), EVIDENCE_MARKERS):
                self.add(ERROR, "fact-no-evidence", path, "нет блока доказательства; это гипотеза")
        for _, path in hypotheses:
            lower = read(path).lower()
            missing = [name for name, markers in H_GROUPS if not has_any(lower, markers)]
            if missing:
                self.add(ERROR, "hypothesis-fields", path, "нет полей: " + ", ".join(missing))

    def check_duplicate_ids(self) -> None:
        for prefix in ("F", "H"):
            seen: dict[int, list[Path]] = {}
            for number, path in self.entity_files(prefix, recursive=True):
                seen.setdefault(number, []).append(path)
            for number, paths in seen.items():
                if len(paths) > 1:
                    self.add(
                        ERROR,
                        "duplicate-id",
                        "Knowledge",
                        f"{prefix}-{number:02d}: " + ", ".join(self.relative(path) for path in paths),
                    )

    def check_registry_coverage(self) -> None:
        registry = self.root / "Knowledge/README.md"
        if not registry.is_file():
            return
        text = read(registry)
        for prefix in ("F", "H"):
            for number, path in self.entity_files(prefix):
                if path.name in text:
                    continue
                if re.search(rf"\b{prefix}-0*{number}\b", text):
                    self.add(WARN, "registry-no-link", path, f"ID есть, но ссылки на файл нет в Knowledge/README.md")
                else:
                    self.add(ERROR, "orphan-file", path, f"файл отсутствует в Knowledge/README.md")

    def check_context_companions(self) -> None:
        for path in self.md:
            if self.top(path) == "Archive" or not path.name.endswith("_context.md"):
                continue
            main = path.with_name(path.name[: -len("_context.md")] + ".md")
            if not main.is_file():
                self.add(ERROR, "orphan-context", path, f"нет основного файла {main.name}")

    # --- links and boundaries ----------------------------------------------

    def resolve_target(self, source: Path, target: str) -> Path | None:
        if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target) or target.startswith("#"):
            return None
        clean = target.split("#", 1)[0].split("?", 1)[0]
        return (source.parent / clean).resolve() if clean else None

    def check_links_and_boundaries(self) -> None:
        for path in self.md:
            top = self.top(path)
            if top == "Archive":
                continue
            exported_result = top == "Results"
            # Notes/ and Logs/ are scratch material: their own links are advisory, not contractual.
            level = WARN if top in SCRATCH_DIRS else ERROR
            for _, line in strip_fences(read(path)):
                inbox_link_found = False
                result_link_found = False
                for target in LINK_RE.findall(line):
                    resolved = self.resolve_target(path, target)
                    if resolved is None:
                        continue
                    try:
                        inside = resolved.relative_to(self.root)
                    except ValueError:
                        if any(resolved.is_relative_to(kb_dir) for kb_dir in self.kb_dirs):
                            self.add(
                                WARN,
                                "kb-link",
                                path,
                                f"Markdown-ссылка на файл внешней базы: {target}; "
                                "цитировать текстом с датой",
                            )
                        continue
                    if not resolved.exists():
                        self.add(level, "dead-link", path, f"ссылка не разрешается: {target}")
                    first = inside.parts[0] if inside.parts else ""
                    if first == "Inbox" and top != "Inbox":
                        self.add(ERROR, "inbox-link", path, f"долговечный файл зависит от Inbox: {target}")
                        inbox_link_found = True
                    if first == "Archive" and top != "Archive":
                        self.add(ERROR, "archive-link", path, f"долговечный файл зависит от Archive: {target}")
                    if first == "Notes" and top not in UNTRACKED_DIRS:
                        self.add(WARN, "notes-link", path, f"долговечный файл зависит от черновика: {target}")
                    if first == "Logs" and top not in UNTRACKED_DIRS:
                        self.add(WARN, "logs-link", path, f"долговечный файл зависит от сырого лога: {target}")
                    if exported_result and inside.parts and first != "Results":
                        self.add(ERROR, "result-external-link", path, f"Results ссылается наружу: {target}")
                        result_link_found = True

                if not inbox_link_found and top != "Inbox" and INBOX_PATH_RE.search(line):
                    self.add(ERROR, "inbox-reference", path, "явный путь в Inbox/; извлечь утверждение в Knowledge")
                if exported_result and not result_link_found and RESULT_EXTERNAL_RE.search(line):
                    self.add(ERROR, "result-external-reference", path, "Results зависит от пути вне экспортной папки")

                for target in WIKI_LINK_RE.findall(line):
                    if target.startswith("Inbox/") and top != "Inbox":
                        self.add(ERROR, "inbox-link", path, f"wiki-link в Inbox: {target}")

    def check_result_status(self) -> None:
        results = self.root / "Results"
        payloads = [path for path in results.rglob("*") if path.is_file() and path.name != "README.md"] if results.is_dir() else []
        if not payloads:
            return
        readme = read(self.root / "README.md")
        contradiction = re.search(
            r"(?:results|результат[^\n|]*)(?:[^\n|]{0,60})(?:пуст|пока\s+нет|нет\s+результат|empty)",
            readme,
            re.IGNORECASE,
        )
        if contradiction:
            self.add(
                ERROR,
                "status-contradiction",
                "README.md",
                f"заявлено отсутствие результатов, но найдено payload-файлов: {len(payloads)}",
            )

    def check_artifact_placement(self) -> None:
        for path in self.entries:
            if path.name in IGNORED_NAMES or not path.is_file():
                continue
            relative = path.relative_to(self.root)
            top = relative.parts[0] if len(relative.parts) > 1 else ""
            if top == "Archive":
                continue
            suffix = path.suffix
            if suffix in SCRIPT_EXT:
                if any(relative.parts[: len(prefix)] == prefix for prefix in SCRIPT_DIRS):
                    continue
                if top in ("Tools", "Traces"):
                    self.add(WARN, "tool-retired-location", path, "устаревшее место; скрипт переносится в tools/")
                    continue
                self.add(
                    ERROR,
                    "tool-misplaced",
                    path,
                    "скрипт задачи должен быть в tools/; входной код — в Inbox/",
                )
                continue
            if suffix in OBSERVATION_EXT and top not in OBSERVATION_DIRS:
                self.add(WARN, "observation-misplaced", path, "сырой машинный вывод вне корневой Logs/")

    # --- registries and journals -------------------------------------------

    def check_orders(self) -> None:
        registries = (
            ("Knowledge/README.md", ("F", "H")),
            ("decisions.md", ("D",)),
        )
        for relative, prefixes in registries:
            self.check_registry_order(self.root / relative, prefixes)
        for relative in ("Notes/runs.md", "change-log.md"):
            self.check_journal_order(self.root / relative)

    def check_registry_order(self, path: Path, prefixes: tuple[str, ...]) -> None:
        if not path.is_file():
            return
        section = "start"
        seen: dict[str, list[int]] = {prefix: [] for prefix in prefixes}
        reported: set[tuple[str, str]] = set()
        for _, line in strip_fences(read(path)):
            if line.startswith("## "):
                section = line[3:].strip()
                seen = {prefix: [] for prefix in prefixes}
                continue
            for prefix in prefixes:
                match = re.match(rf"^\|\s*\**\s*`?\[?{prefix}-(\d+)", line)
                if not match:
                    continue
                number = int(match.group(1))
                if seen[prefix] and number < seen[prefix][-1] and (section, prefix) not in reported:
                    reported.add((section, prefix))
                    self.add(WARN, "registry-order", path, f"{prefix}-{number:02d} после {prefix}-{seen[prefix][-1]:02d} в {section}")
                seen[prefix].append(number)

    def check_journal_order(self, path: Path) -> None:
        if not path.is_file():
            return
        table_stamps: list[tuple[int, int, int, int, int]] = []
        for _, line in strip_fences(read(path)):
            if not line.startswith("|"):
                continue
            first = line.strip().strip("|").split("|", 1)[0].strip().replace("*", "")
            match = TABLE_STAMP_RE.fullmatch(first)
            if match:
                year, month, day, hour, minute = match.groups()
                table_stamps.append((int(year), int(month), int(day), int(hour or 0), int(minute or 0)))
        if any(upper < lower for upper, lower in zip(table_stamps, table_stamps[1:])):
            self.add(
                ERROR,
                "journal-order",
                path,
                "журнал должен быть по убыванию: свежие записи сверху, старые снизу",
            )

        dates: list[str] = []
        current_date: str | None = None
        times: list[int] = []
        for _, line in strip_fences(read(path)):
            match = DATE_HEAD_RE.match(line)
            if match:
                current_date = "-".join(match.groups())
                dates.append(current_date)
                times = []
                continue
            if current_date and line.startswith("|"):
                first = line.strip().strip("|").split("|", 1)[0].strip().replace("*", "")
                match = TIME_RE.match(first)
                if match:
                    minutes = int(match.group(1)) * 60 + int(match.group(2))
                    if times and minutes > times[-1]:
                        self.add(ERROR, "journal-row-order", path, f"в {current_date} время не по убыванию")
                        current_date = None
                    times.append(minutes)
        if any(upper < lower for upper, lower in zip(dates, dates[1:])):
            self.add(ERROR, "journal-order", path, "секции дат не от свежей к старой")

    def check_unreverted(self) -> None:
        path = self.root / "change-log.md"
        pattern = re.compile(r"(?:откачено|reverted)\s*[:=|]\s*(?:нет|no)\b", re.IGNORECASE)
        for number, line in strip_fences(read(path)):
            if pattern.search(line.replace("*", "")):
                self.add(WARN, "unreverted-change", path, f"строка {number}: изменение не откачено")

    def check_bare_percentages(self) -> None:
        if not self.pedantic:
            return
        for path in self.md:
            if self.top(path) == "Archive":
                continue
            lines = []
            for number, line in strip_fences(read(path)):
                if "%" in line and "/" not in line and re.search(r"\d[\d\s.,]*\s*%", line):
                    lines.append(number)
            if lines:
                self.add(WARN, "bare-percent", path, "процент без числителя/знаменателя: " + ", ".join(map(str, lines[:5])))

    def run(self) -> None:
        self.stats["структура"] = self.layout if self.layout != "legacy" else "v1-legacy"
        self.check_surface()
        if self.layout in ("unsupported", "legacy", "unknown"):
            return
        self.check_env()
        self.check_placeholders()
        self.check_steps()
        self.check_readme()
        self.check_footer_knowledge()
        self.check_edits_outside_step()
        self.check_facts_and_hypotheses()
        self.check_duplicate_ids()
        self.check_registry_coverage()
        self.check_context_companions()
        self.check_links_and_boundaries()
        self.check_result_status()
        self.check_artifact_placement()
        self.check_orders()
        self.check_unreverted()
        self.check_bare_percentages()


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Проверить папку задачи task-lab по канонической структуре v2")
    parser.add_argument("task", help="TaskID или точный путь к папке задачи")
    parser.add_argument("--workspace", default=".", help="область поиска TaskID")
    parser.add_argument("--pedantic", action="store_true", help="warnings also fail; extra checks")
    args = parser.parse_args(argv)

    try:
        root = resolve_task(args.task, Path(args.workspace))
    except TaskResolutionError as error:
        print(f"ОШИБКА: {error}", file=sys.stderr)
        return 2

    audit = Audit(root, args.pedantic)
    audit.run()
    print(f"АУДИТ {root}")
    print("=" * 72)
    for key, value in audit.stats.items():
        print(f"  {key}: {value}")

    errors = [finding for finding in audit.findings if finding.level == ERROR]
    warnings = [finding for finding in audit.findings if finding.level == WARN]
    for level, findings in ((ERROR, errors), (WARN, warnings)):
        if not findings:
            continue
        print(f"\n{level} — {len(findings)}")
        print("-" * 72)
        for finding in findings:
            print(f"  [{finding.code}] {finding.where}")
            print(f"      {finding.message}")

    print("\n" + "=" * 72)
    failed = bool(errors) or (args.pedantic and bool(warnings))
    if failed:
        print(f"СТОП: ошибок {len(errors)}, предупреждений {len(warnings)}")
        return 1
    print(f"ГОТОВО: ошибок нет, предупреждений {len(warnings)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
