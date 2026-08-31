#!/usr/bin/env python3
"""Audit a task-lab folder against the single canonical structure.

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
    ("проверка", ("как провер", "гейт", "gate", "what closes", "check")),
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

CANONICAL_DIRS = ("Context", "Knowledge", "Steps", "Results", "Notes", "Logs", "Inbox")
# Synchronised while a step is being closed, so they are legitimately newer than its result.
PROJECTION_FILES = ("README.md", "index.md", "steps.md", "Context/90-session-restore.md")
# Two root siblings, never nested: Notes/ is human scratch, Logs/ is machine output.
SCRATCH_DIRS = ("Notes", "Logs")
# Scratch and inbound material are exempt from the "every edit is a step" rule.
UNTRACKED_DIRS = SCRATCH_DIRS + ("Inbox",)
EDIT_TOLERANCE_SECONDS = 15 * 60
SCRIPT_DIRS = (("Context", "tools"), ("Inbox",), ("Notes",))
# Raw captured output belongs in root Logs/; Inbox/ may carry it as inbound material.
OBSERVATION_DIRS = ("Logs", "Inbox")
UNSUPPORTED_MARKERS = (
    ("Process/steps", "Process/steps/", "шаги живут в Steps/ как пары Step-XX.md + Step-XX-result.md"),
    ("Steps/_next.md", "Steps/_next.md", "текущий шаг — это Step-XX.md без парного результата"),
)
RETIRED_DIRS = (
    ("Tools", "скрипты задачи живут в Context/tools/"),
    ("Traces", "сырой вывод живёт в корневой Logs/, журналы наблюдений — в Notes/"),
    ("Hypotheses", "гипотезы живут в Knowledge/ как H-NN-*.md"),
)

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
STATE_HEADING_RE = re.compile(r"состояни|текущий шаг|state|current step", re.IGNORECASE)
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
    r"(?:^|[\s`(\[])(?:\.\./)*(?:Context|Knowledge|Steps|Inbox)/[A-Za-z0-9_.-]+"
)
NO_OPEN_MARKERS = (
    "открытого шага нет",
    "текущий шаг | нет",
    "нет. следующий запрос",
    "следующий запрос пользователя создаст",
    "ждать запроса пользователя",
    "no open step",
)


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


def status_text(text: str) -> str:
    """The state section of a projection, or the whole file when it has none.

    Entry points also *explain* the waiting rule in prose; only the state block
    is a status claim, so the staleness check must not read the explanation.
    """
    lines = text.splitlines()
    start: int | None = None
    level = 0
    for index, line in enumerate(lines):
        heading = HEADING_RE.match(line)
        if heading and STATE_HEADING_RE.search(heading.group(2)):
            start, level = index + 1, len(heading.group(1))
            break
    if start is None:
        return text
    collected: list[str] = []
    for line in lines[start:]:
        heading = HEADING_RE.match(line)
        if heading and len(heading.group(1)) <= level:
            break
        collected.append(line)
    return "\n".join(collected)


class Audit:
    def __init__(self, root: Path, pedantic: bool):
        self.root = root
        self.pedantic = pedantic
        self.findings: list[Finding] = []
        self.entries = self.walk()
        self.md = sorted(path for path in self.entries if path.is_file() and path.suffix == ".md")
        self.stats: dict[str, object] = {}
        self.layout = self.detect_layout()
        self.current_step: int | None = None
        self.completed_steps: set[int] = set()
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

    def detect_layout(self) -> str:
        """Canonical, unsupported (another shape), or unknown (no step surface)."""
        for relative, _, _ in UNSUPPORTED_MARKERS:
            if (self.root / relative).exists():
                return "unsupported"
        if (self.root / "Steps").is_dir() or (self.root / "steps.md").is_file():
            return "standard"
        return "unknown"

    def relative(self, path: Path | str) -> str:
        if isinstance(path, str):
            return path
        try:
            return str(path.relative_to(self.root))
        except ValueError:
            return str(path)

    def add(self, level: str, code: str, where: Path | str, message: str) -> None:
        self.findings.append(Finding(level, code, self.relative(where), message))

    def entity_files(self, directory: str, prefix: str, recursive: bool = False) -> list[tuple[int, Path]]:
        base = self.root / directory
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

    def check_surface(self) -> None:
        if self.layout == "unsupported":
            for relative, label, hint in UNSUPPORTED_MARKERS:
                if (self.root / relative).exists():
                    self.add(
                        ERROR,
                        "unsupported-layout",
                        label,
                        f"структура вне канона; {hint}. Перенос — отдельная явная задача, "
                        "молча мигрировать нельзя",
                    )
            return
        if self.layout == "unknown":
            self.add(ERROR, "unknown-layout", self.root, "нет ни Steps/, ни steps.md: это не папка задачи")
            return
        required = (
            "README.md",
            "index.md",
            "steps.md",
            "Context/00-START-HERE.md",
            "Context/90-session-restore.md",
            "Knowledge/README.md",
            "Results/README.md",
        )
        if not (self.root / "Steps").is_dir():
            self.add(ERROR, "surface-missing", "Steps/", "обязательный каталог отсутствует")
        for relative in required:
            if not (self.root / relative).is_file():
                self.add(ERROR, "surface-missing", relative, "обязательная точка структуры отсутствует")
        for relative, hint in RETIRED_DIRS:
            if (self.root / relative).is_dir():
                self.add(WARN, "retired-dir", relative + "/", f"папки нет в канонической структуре: {hint}")
        for nested in sorted(self.root.rglob("Logs")):
            if not nested.is_dir() or nested == self.root / "Logs":
                continue
            if any(part in PRUNE_DIRS for part in nested.relative_to(self.root).parts):
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
                + ", ".join(name + "/" for name in CANONICAL_DIRS),
            )

    def check_env(self) -> None:
        """Validate root env.json and resolve the external knowledge base it names."""
        path = self.root / "env.json"
        if not path.is_file():
            self.add(
                WARN,
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
        # Canonicalize like resolve_target does, so symlinked paths (/var -> /private/var)
        # compare equal when link targets are checked against the base.
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
            if "Inbox" in parts or any(name in parts for name in SCRATCH_DIRS):
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

    def check_steps(self) -> None:
        if self.layout == "standard":
            self.check_standard_steps()

    def check_standard_steps(self) -> None:
        """Check the canonical request-plan/result-pair contract."""
        steps_dir = self.root / "Steps"
        plans: dict[int, Path] = {}
        results: dict[int, Path] = {}
        for path in steps_dir.glob("*.md") if steps_dir.is_dir() else []:
            plan_match = re.fullmatch(r"Step-(\d{2,})\.md", path.name)
            result_match = re.fullmatch(r"Step-(\d{2,})-result\.md", path.name)
            if plan_match:
                plans[int(plan_match.group(1))] = path
            elif result_match:
                results[int(result_match.group(1))] = path
            elif re.match(r"step-", path.name, re.IGNORECASE):
                self.add(ERROR, "step-name", path, "ожидается Step-XX.md или Step-XX-result.md с номером 01, 02, …")

        for number in sorted(set(results) - set(plans)):
            self.add(ERROR, "step-orphan", results[number], f"результат шага {number:02d} без Step-{number:02d}.md")

        opened = sorted(set(plans) - set(results))
        if len(opened) > 1:
            self.add(ERROR, "many-open-steps", steps_dir, f"открытых шагов {len(opened)}: {opened}")
        elif opened:
            self.current_step = opened[0]

        numbers = set(plans) | set(results)
        if numbers:
            missing = sorted(set(range(1, max(numbers) + 1)) - set(plans))
            if missing:
                self.add(ERROR, "step-gap", steps_dir, "нет Step-файлов: " + ", ".join(f"{n:02d}" for n in missing))
        if self.current_step is not None and self.current_step != max(plans):
            self.add(ERROR, "open-step-not-latest", plans[self.current_step], "открытый шаг должен иметь наибольший номер")

        self.completed_steps = set(plans) & set(results)
        history_text = read(self.root / "steps.md")
        for number in sorted(self.completed_steps):
            result_name = results[number].name
            if result_name not in history_text:
                self.add(ERROR, "step-history-missing", results[number], f"пара шага {number:02d} отсутствует в steps.md")
        self.stats["шагов всего"] = len(plans)
        self.stats["шагов завершено"] = len(self.completed_steps)
        self.stats["текущий шаг"] = self.current_step if self.current_step is not None else "нет — ожидается запрос"

    def check_edits_outside_step(self) -> None:
        """Durable files touched after the last step closed, with no step open.

        Heuristic: it reads modification times, so a checkout or a copy can move
        them. It is a WARN for that reason — but it is the only mechanical signal
        that a report was edited without a request-bound step.
        """
        if self.layout != "standard" or self.current_step is not None or not self.completed_steps:
            return
        results = [
            path
            for path in (self.root / "Steps" / f"Step-{number:02d}-result.md" for number in self.completed_steps)
            if path.is_file()
        ]
        if not results:
            return
        newest = max(path.stat().st_mtime for path in results)
        newest_name = max(results, key=lambda path: path.stat().st_mtime).name
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

    def step_needles(self, number: int) -> tuple[str, ...]:
        values = {str(number), f"{number:02d}"}
        return tuple(
            f"{word}{separator}{value}"
            for value in values
            for word, separator in (
                ("step", "-"), ("step", " "), ("шаг", " "), ("шага", " "),
                ("шагом", " "), ("шаге", " "),
            )
        )

    def check_entry_points(self) -> None:
        if self.layout != "standard":
            return
        targets = (("README.md", ERROR), ("index.md", ERROR), ("steps.md", ERROR),
                   ("Context/90-session-restore.md", WARN))
        if self.current_step is None:
            for relative, level in targets:
                path = self.root / relative
                if path.is_file() and not has_any(status_text(read(path)).lower(), NO_OPEN_MARKERS):
                    self.add(level, "entry-point-stale", path, "не отражает состояние ожидания запроса пользователя")
            return
        needles = self.step_needles(self.current_step)
        for relative, level in targets:
            path = self.root / relative
            if not path.is_file():
                continue
            lower = status_text(read(path)).lower()
            if has_any(lower, NO_OPEN_MARKERS) or not any(needle in lower for needle in needles):
                self.add(level, "entry-point-stale", path, f"не отражает текущий шаг {self.current_step:02d}")

        if self.current_step > 1:
            history = self.root / "steps.md"
            previous = self.step_needles(self.current_step - 1)
            if history.is_file() and not any(needle in read(history).lower() for needle in previous):
                self.add(WARN, "history-stale", history, f"не найден последний завершённый шаг {self.current_step - 1:02d}")

    def check_facts_and_hypotheses(self) -> None:
        facts = self.entity_files("Knowledge", "F")
        hypotheses = self.entity_files("Knowledge", "H")
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
        for directory, prefix in (("Knowledge", "F"), ("Knowledge", "H")):
            seen: dict[int, list[Path]] = {}
            for number, path in self.entity_files(directory, prefix, recursive=True):
                seen.setdefault(number, []).append(path)
            for number, paths in seen.items():
                if len(paths) > 1:
                    self.add(
                        ERROR,
                        "duplicate-id",
                        directory,
                        f"{prefix}-{number:02d}: " + ", ".join(self.relative(path) for path in paths),
                    )

    def check_registry_coverage(self) -> None:
        pairs = (("Knowledge", "F", "Knowledge/README.md"), ("Knowledge", "H", "Knowledge/README.md"))
        for directory, prefix, registry_relative in pairs:
            registry = self.root / registry_relative
            if not registry.is_file():
                continue
            text = read(registry)
            for number, path in self.entity_files(directory, prefix):
                if path.name in text:
                    continue
                if re.search(rf"\b{prefix}-0*{number}\b", text):
                    self.add(WARN, "registry-no-link", path, f"ID есть, но ссылки на файл нет в {registry_relative}")
                else:
                    self.add(ERROR, "orphan-file", path, f"файл отсутствует в {registry_relative}")

    def check_context_companions(self) -> None:
        for path in self.md:
            if not path.name.endswith("_context.md"):
                continue
            main = path.with_name(path.name[: -len("_context.md")] + ".md")
            if not main.is_file():
                self.add(ERROR, "orphan-context", path, f"нет основного файла {main.name}")

    def resolve_target(self, source: Path, target: str) -> Path | None:
        if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target) or target.startswith("#"):
            return None
        clean = target.split("#", 1)[0].split("?", 1)[0]
        return (source.parent / clean).resolve() if clean else None

    def check_links_and_boundaries(self) -> None:
        for path in self.md:
            relative_parts = path.relative_to(self.root).parts
            top = relative_parts[0] if relative_parts else ""
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
                    if inside.parts and inside.parts[0] == "Inbox" and top != "Inbox":
                        self.add(ERROR, "inbox-link", path, f"долговечный файл зависит от Inbox: {target}")
                        inbox_link_found = True
                    if inside.parts and inside.parts[0] == "Notes" and top not in UNTRACKED_DIRS:
                        self.add(WARN, "notes-link", path, f"долговечный файл зависит от черновика: {target}")
                    if inside.parts and inside.parts[0] == "Logs" and top not in UNTRACKED_DIRS:
                        self.add(WARN, "logs-link", path, f"долговечный файл зависит от сырого лога: {target}")
                    if exported_result and inside.parts and inside.parts[0] != "Results":
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
        if self.layout != "standard":
            return
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
            suffix = path.suffix
            if suffix in SCRIPT_EXT:
                if any(relative.parts[: len(prefix)] == prefix for prefix in SCRIPT_DIRS):
                    continue
                if top in ("Tools", "Traces"):
                    self.add(WARN, "tool-retired-location", path, "устаревшее место; скрипт переносится в Context/tools/")
                    continue
                self.add(
                    ERROR,
                    "tool-misplaced",
                    path,
                    "скрипт задачи должен быть в Context/tools/; входной код — в Inbox/",
                )
                continue
            if suffix in OBSERVATION_EXT and top not in OBSERVATION_DIRS and relative.parts[:2] != ("Context", "tools"):
                self.add(WARN, "observation-misplaced", path, "сырой машинный вывод вне корневой Logs/")

    def check_orders(self) -> None:
        registries = (
            ("Knowledge/README.md", ("F", "H")),
            ("Context/decisions.md", ("D",)),
            ("Context/40-queue.md", ("Q",)),
        )
        for relative, prefixes in registries:
            self.check_registry_order(self.root / relative, prefixes)
        self.check_step_registry_order(self.root / "steps.md")
        for relative in ("Notes/runs.md", "Context/change-log.md"):
            self.check_journal_order(self.root / relative)

    def check_step_registry_order(self, path: Path) -> None:
        if not path.is_file():
            return
        numbers: list[int] = []
        for _, line in strip_fences(read(path)):
            if not line.startswith("|"):
                continue
            cells = [cell.strip().replace("*", "") for cell in line.strip().strip("|").split("|")]
            number: int | None = None
            for cell in cells[:2]:
                match = re.match(r"^(?:\[)?(?:шаг\s*|step[- ]*)?0*(\d+)(?:\]|\s|$)", cell, re.IGNORECASE)
                if match:
                    number = int(match.group(1))
                    break
            if number is not None:
                numbers.append(number)
        if any(upper < lower for upper, lower in zip(numbers, numbers[1:])):
            self.add(
                ERROR,
                "step-registry-order",
                path,
                "шаги должны идти по убыванию: последние сверху, первые снизу",
            )

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
                match = re.match(rf"^\|\s*\**\s*{prefix}-(\d+)", line)
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
        path = self.root / "Context/change-log.md"
        pattern = re.compile(r"(?:откачено|reverted)\s*[:=|]\s*(?:нет|no)\b", re.IGNORECASE)
        for number, line in strip_fences(read(path)):
            if pattern.search(line.replace("*", "")):
                self.add(WARN, "unreverted-change", path, f"строка {number}: изменение не откачено")

    def check_bare_percentages(self) -> None:
        if not self.pedantic:
            return
        for path in self.md:
            lines = []
            for number, line in strip_fences(read(path)):
                if "%" in line and "/" not in line and re.search(r"\d[\d\s.,]*\s*%", line):
                    lines.append(number)
            if lines:
                self.add(WARN, "bare-percent", path, "процент без числителя/знаменателя: " + ", ".join(map(str, lines[:5])))

    def run(self) -> None:
        self.stats["структура"] = self.layout
        self.check_surface()
        self.check_env()
        self.check_placeholders()
        self.check_steps()
        self.check_edits_outside_step()
        self.check_entry_points()
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
    parser = argparse.ArgumentParser(description="Проверить папку задачи task-lab по канонической структуре")
    parser.add_argument("task", help="TaskID или точный путь к папке задачи")
    parser.add_argument("--workspace", default=".", help="область поиска TaskID")
    parser.add_argument("--pedantic", action="store_true", help="warnings also fail; check bare percentages")
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
