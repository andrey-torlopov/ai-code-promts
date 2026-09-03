#!/usr/bin/env python3
"""Regression smoke tests for task-lab scripts (layout v2); standard library only."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent

STATE_WAIT = "**Состояние:** открытого шага нет · ждём запрос пользователя · 2026-01-02"
STATE_OPEN = "**Состояние:** шаг 01 открыт · 2026-01-02"
HISTORY_PLACEHOLDER = "| — | — | завершённых шагов нет | — | — |"
HISTORY_ROW = "| 01 | 2026-01-02 | проверить контракт | контракт работает | [шаг](Steps/Step-01.md) |"

OPEN_STEP = """# Шаг 01 — проверить контракт

**Статус:** выполняется · **Дата:** 2026-01-02

## Запрос

Проверить пошаговый контракт. Вопрос шага: различает ли аудит открытый и закрытый шаг?

## План

**Границы:** только self-test.

**Действия:**

1. Запустить аудит.

**Критерий завершения:** аудит проходит без ошибок.
"""

CLOSED_STEP = OPEN_STEP.replace(
    "**Статус:** выполняется · **Дата:** 2026-01-02",
    "**Статус:** завершён · **Дата:** 2026-01-02",
) + """
## Что сделано

Прогнан аудит на открытом и на закрытом шаге.

## Результат

**Вердикт:** контракт работает; аудит различает открытый и закрытый шаг.

Доказательства: вывод audit_task.py без ошибок. Ограничения: нет.

## Задействованные знания

| ID | Роль в шаге |
|---|---|
| F-01 | опора: постановка задачи |
"""


def run(script: str, *arguments: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / script), *arguments],
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def require(condition: bool, message: str, output: str = "") -> None:
    if condition:
        return
    print(f"FAIL: {message}")
    if output:
        print(output)
    raise SystemExit(1)


def fill_standard(task: Path) -> None:
    for path in task.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        text = re.sub(r"\{\{FILL_[A-Z0-9_]+\}\}", "не применимо", text)
        path.write_text(text, encoding="utf-8")


def replace_in(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    require(old in text, f"фрагмент для замены не найден в {path.name}: {old!r}")
    path.write_text(text.replace(old, new), encoding="utf-8")


def build_legacy_fixture(root: Path) -> None:
    """A filled, self-consistent v1 folder for the migration test."""
    (root / "Context" / "tools").mkdir(parents=True)
    (root / "Steps").mkdir()
    (root / "Knowledge").mkdir()
    (root / "Results").mkdir()
    (root / "Notes").mkdir()
    (root / "Logs").mkdir()
    files = {
        "README.md": (
            "# OLD-100 — переносная задача\n\n## Состояние на 2026-01-02\n\n| | |\n|---|---|\n"
            "| Фаза | анализ |\n| Текущий шаг | нет |\n"
        ),
        "index.md": (
            "# OLD-100 — точка входа\n\n**Режим:** `general` · **Создано:** 2026-01-02\n\n"
            "## Состояние на 2026-01-02\n\n| | |\n|---|---|\n| Фаза | анализ |\n| Блокер | нет |\n\n"
            "## Что не предлагать повторно\n\n- не трогать кэш — опровергнуто наблюдением\n"
        ),
        "steps.md": (
            "# Шаги — история\n\n## Текущий шаг\n\n**Нет.**\n\n## Рекомендуемая очередность\n\n"
            "1. проверить, что миграция сохранила историю\n\n## История\n\n"
            "| Шаг | Дата | Запрос | Вердикт | Файлы |\n|---:|---|---|---|---|\n"
            "| 01 | 2026-01-02 | проверить перенос | пары сливаются | Steps/Step-01.md |\n"
        ),
        "Context/00-START-HERE.md": (
            "# START HERE\n\n## Задача\n\nПеренести контракт шагов на структуру v2.\n\n"
            "## Критерий успеха\n\nАудит после миграции зелёный.\n\n## Инварианты работы\n\n"
            "INV-1. **Один вердикт на шаг** — иначе история перестаёт объяснять работу.\n"
        ),
        "Context/10-repo-and-revisions.md": (
            "# Репозитории и ревизии\n\n## Пути\n\n| Что | Путь |\n|---|---|\n| Предмет | /tmp/subject |\n\n"
            "## Срез на 2026-01-02\n\n| Компонент | Ревизия | Как проверить |\n|---|---|---|\n"
            "| repo | abc1234 | git rev-parse HEAD |\n\n## Полезные команды\n\n```bash\ngit status\n```\n\n"
            "## Оговорка\n\nСборка не выполнялась.\n"
        ),
        "Context/30-method.md": "# Метод\n\n## Метод этой задачи\n\nне применимо\n",
        "Context/40-queue.md": (
            "# Очередь работ\n\n## Кандидаты\n\n| Приоритет | Кандидат |\n|---:|---|\n| 1 | проверить кэш |\n\n"
            "## Блокирующие вопросы к пользователю\n\n| ID | Вопрос | Почему нельзя решить самому | Умолчание |\n"
            "|---|---|---|---|\n| Q-01 | нужна ли миграция всех задач | вкусовое решение | да |\n"
        ),
        "Context/90-session-restore.md": (
            "# Восстановление сессии\n\n## Drift-check: проверить до выводов\n\n"
            "| Проверка | Ожидание на 2026-01-02 | Если изменилось |\n|---|---|---|\n"
            "| Авторитетная ревизия | abc1234 | перепроверить затронутые факты |\n"
        ),
        "Context/tools/calc.py": "print(83 / 242)\n",
        "Knowledge/README.md": (
            "# Knowledge — реестр фактов и гипотез\n\n## Факты\n\n| ID | Утверждение | Тяжесть | Файл |\n"
            "|---|---|---|---|\n| `F-01` | Задача и критерий успеха | — | [F-01](F-01-problem-and-targets.md) |\n\n"
            "## Гипотезы\n\n| ID | Вопрос | Статус | Чем закрывается | Файл |\n|---|---|---|---|---|\n"
            "| — | гипотез нет | — | — | — |\n"
        ),
        "Knowledge/F-01-problem-and-targets.md": (
            "# F-01 — задача и критерий успеха\n\n**Статус:** подтверждено\n\n## Утверждение\n\n"
            "Контракт шагов переносится на v2.\n\n## Доказательства\n\n- Постановка пользователя, 2026-01-02.\n"
        ),
        "Results/README.md": (
            "# Results — деливерабл\n\n| Файл | Что внутри |\n|---|---|\n| — | результатов пока нет |\n"
        ),
        "Steps/Step-01.md": (
            "# Шаг 01 — проверить перенос\n\n**Статус:** выполняется\n\n## Запрос пользователя\n\n"
            "Проверить перенос пар.\n\n## Вопрос шага\n\nСливаются ли пары в один файл?\n\n"
            "## Границы\n\nТолько self-test.\n\n## Действия\n\n1. Прогнать миграцию.\n\n"
            "## Критерий завершения\n\nАудит после миграции зелёный.\n"
        ),
        "Steps/Step-01-result.md": (
            "# Шаг 01 — результат: пары сливаются\n\n**Статус:** завершён\n**Дата:** 2026-01-02\n"
            "**Вердикт:** пары сливаются в один файл без потери контракта.\n\n## Что сделано\n\n"
            "Прогнан перенос на копии.\n\n## Доказательства\n\nАудит зелёный.\n\n## Изменения знаний\n\n"
            "F-01 подтверждён.\n\n## Ограничения и долги\n\nНет.\n"
        ),
    }
    for relative, content in files.items():
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="task-lab-self-test-") as temporary:
        parent = Path(temporary)

        # --- scaffold v2 ----------------------------------------------------
        created = run("init_task.py", "--id", "123", "--date", "2026-01-02", "--with-inbox", cwd=parent)
        require(created.returncode == 0, "standard scaffold failed", created.stdout)
        standard = parent / "123"

        for relative in (
            "README.md", "env.json",
            "Knowledge/README.md", "Knowledge/F-01-problem-and-targets.md",
            "Knowledge/F-02-environment.md", "Results/README.md", "Inbox/README.md",
        ):
            require((standard / relative).is_file(), f"canonical scaffold missed {relative}")
        for relative in ("Steps", "Notes", "Logs", "tools"):
            require((standard / relative).is_dir(), f"canonical scaffold missed {relative}/")
        require(not (standard / "Notes" / "Logs").exists(), "Logs/ must be a root sibling of Notes/")
        # Name-set check: on a case-insensitive filesystem Path("Tools").exists() matches tools/.
        root_names = {entry.name for entry in standard.iterdir()}
        for name in ("index.md", "steps.md", "Context", "Process", "Tools", "Traces", "Hypotheses", "timeline.md"):
            require(name not in root_names, f"canonical scaffold created forbidden {name}")
        steps_names = {entry.name for entry in (standard / "Steps").iterdir()}
        require(not steps_names & {"README.md", "_next.md"}, "canonical scaffold created forbidden Steps/ content")
        env_default = json.loads((standard / "env.json").read_text(encoding="utf-8"))
        require(env_default.get("external_knowledge") == "", "default env.json must carry an empty pointer")
        readme_text = (standard / "README.md").read_text(encoding="utf-8")
        require(STATE_WAIT in readme_text, "README template must carry the machine-readable state line")
        require("Рекомендуемая очередность" in readme_text, "README template must carry the queue block")

        red = run("audit_task.py", "123", cwd=parent)
        require(red.returncode == 1 and "[placeholder]" in red.stdout, "unfilled scaffold must fail", red.stdout)

        fill_standard(standard)
        green = run("audit_task.py", "123", cwd=parent)
        require(green.returncode == 0, "filled scaffold must pass", green.stdout)
        require("предупреждений 0" in green.stdout, "clean scaffold must not warn", green.stdout)

        brief = run("restore_task.py", "123", "--section", "step", cwd=parent)
        require(
            brief.returncode == 0
            and "структура standard" in brief.stdout
            and "открытого шага нет; ждать запроса пользователя" in brief.stdout,
            "new scaffold must wait for a user request",
            brief.stdout,
        )

        # --- step lifecycle -------------------------------------------------
        readme = standard / "README.md"
        step_01 = standard / "Steps" / "Step-01.md"
        step_01.write_text(OPEN_STEP, encoding="utf-8")

        mismatch = run("audit_task.py", "123", cwd=parent)
        require(
            mismatch.returncode == 1 and "[state-line-mismatch]" in mismatch.stdout,
            "open step without a README state-line update must fail",
            mismatch.stdout,
        )
        replace_in(readme, STATE_WAIT, STATE_OPEN)
        open_green = run("audit_task.py", "123", cwd=parent)
        require(open_green.returncode == 0, "one open step with a synced state line must pass", open_green.stdout)
        open_brief = run("restore_task.py", "123", "--section", "step", cwd=parent)
        require("номер: 01" in open_brief.stdout, "restore did not locate the open Step-01", open_brief.stdout)

        step_01.write_text(CLOSED_STEP, encoding="utf-8")
        replace_in(readme, STATE_OPEN, STATE_WAIT)
        replace_in(readme, HISTORY_PLACEHOLDER, HISTORY_ROW)
        closed_green = run("audit_task.py", "123", cwd=parent)
        require(closed_green.returncode == 0, "closed step with synced README must pass", closed_green.stdout)
        checkpoint = run("restore_task.py", "123", "--section", "step", cwd=parent)
        require(
            "чекпойнт" in checkpoint.stdout and "контракт работает" in checkpoint.stdout,
            "restore must show the latest closed step as the checkpoint",
            checkpoint.stdout,
        )

        # --- step contract violations --------------------------------------
        replace_in(step_01, "| F-01 | опора: постановка задачи |", "| F-01 | опора: постановка задачи |\n| F-99 | опора |")
        footer = run("audit_task.py", "123", cwd=parent)
        require(
            footer.returncode == 1 and "[footer-knowledge]" in footer.stdout,
            "a footer id missing from Knowledge/ must fail",
            footer.stdout,
        )
        replace_in(step_01, "\n| F-99 | опора |", "")

        half_step = standard / "Steps" / "Step-02.md"
        half_step.write_text(
            "# Шаг 02 — обрубок\n\n**Статус:** завершён · **Дата:** 2026-01-02\n\n"
            "## Запрос\n\nПроверить обрубок.\n\n## План\n\n**Критерий завершения:** аудит падает.\n",
            encoding="utf-8",
        )
        sections = run("audit_task.py", "123", cwd=parent)
        require(
            sections.returncode == 1 and "[step-sections]" in sections.stdout,
            "a closed step without its closing sections must fail",
            sections.stdout,
        )
        half_step.unlink()

        orphan = standard / "Steps" / "Step-02-result.md"
        orphan.write_text("# Шаг 02 — результат: orphan\n", encoding="utf-8")
        legacy_step = run("audit_task.py", "123", cwd=parent)
        require(
            legacy_step.returncode == 1 and "[legacy-step-file]" in legacy_step.stdout,
            "a v1 result file must be reported",
            legacy_step.stdout,
        )
        orphan.unlink()

        # --- edit-outside-step and exemptions -------------------------------
        late = time.time() + 40 * 60
        fact_path = standard / "Knowledge" / "F-01-problem-and-targets.md"
        os.utime(fact_path, (late, late))
        late_audit = run("audit_task.py", "123", cwd=parent)
        require(
            late_audit.returncode == 0 and "[edit-outside-step]" in late_audit.stdout,
            "an out-of-step edit of a durable file must warn",
            late_audit.stdout,
        )
        os.utime(fact_path, None)
        note = standard / "Notes" / "n1.md"
        note.write_text("черновая заметка о дрейфе\n", encoding="utf-8")
        raw_log = standard / "Logs" / "run.log"
        raw_log.write_text("2026-01-02 10:00 старт\n", encoding="utf-8")
        for path in (note, raw_log, readme):
            os.utime(path, (late, late))
        exempt = run("audit_task.py", "123", cwd=parent)
        require(
            "[edit-outside-step]" not in exempt.stdout,
            "Notes/, Logs/ and README are exempt from the every-edit-is-a-step check",
            exempt.stdout,
        )
        require("[observation-misplaced]" not in exempt.stdout, "a raw .log in root Logs/ is correctly placed", exempt.stdout)

        raw_log.rename(standard / "Notes" / "run.log")
        misplaced = run("audit_task.py", "123", cwd=parent)
        require(
            "[observation-misplaced]" in misplaced.stdout,
            "a raw .log inside Notes/ must be reported",
            misplaced.stdout,
        )
        (standard / "Notes" / "run.log").unlink()
        note.unlink()

        nested = standard / "Notes" / "Logs"
        nested.mkdir()
        (nested / "run.log").write_text("вложенный лог\n", encoding="utf-8")
        nested_audit = run("audit_task.py", "123", cwd=parent)
        require(
            nested_audit.returncode == 1 and "[logs-nested]" in nested_audit.stdout,
            "Logs/ nested inside another folder must be an error",
            nested_audit.stdout,
        )
        (nested / "run.log").unlink()
        nested.rmdir()

        # --- placement and boundaries ---------------------------------------
        tool = standard / "tools" / "calc.py"
        tool.write_text("print(83 / 242)\n", encoding="utf-8")
        tool_green = run("audit_task.py", "123", cwd=parent)
        require(
            tool_green.returncode == 0 and "tool-" not in tool_green.stdout,
            "tools/ is the canonical place for task scripts",
            tool_green.stdout,
        )
        misplaced_tool = standard / "Knowledge" / "calc.py"
        misplaced_tool.write_text("print(1)\n", encoding="utf-8")
        misplaced_audit = run("audit_task.py", "123", cwd=parent)
        require("[tool-misplaced]" in misplaced_audit.stdout, "a script outside tools/ must be reported", misplaced_audit.stdout)
        misplaced_tool.unlink()

        retired = standard / "Traces"
        retired.mkdir()
        (retired / "runs.md").write_text("# runs\n", encoding="utf-8")
        retired_audit = run("audit_task.py", "123", cwd=parent)
        require("[retired-dir]" in retired_audit.stdout, "Traces/ must be reported as retired", retired_audit.stdout)
        (retired / "runs.md").unlink()
        retired.rmdir()

        fact_text = fact_path.read_text(encoding="utf-8")
        result_readme = standard / "Results" / "README.md"
        result_text = result_readme.read_text(encoding="utf-8")
        fact_path.write_text(fact_text + "\n[bad](../Inbox/README.md)\n", encoding="utf-8")
        result_readme.write_text(result_text + "\n[bad](../Knowledge/README.md)\n", encoding="utf-8")
        boundaries = run("audit_task.py", "123", cwd=parent)
        require(
            boundaries.returncode == 1
            and "[inbox-link]" in boundaries.stdout
            and "[result-external-link]" in boundaries.stdout,
            "Inbox/Results boundary checks failed",
            boundaries.stdout,
        )
        fact_path.write_text(fact_text, encoding="utf-8")
        result_readme.write_text(result_text, encoding="utf-8")

        archive_dir = standard / "Archive" / "v1"
        archive_dir.mkdir(parents=True)
        (archive_dir / "dummy.md").write_text("# старый файл\n", encoding="utf-8")
        archive_ok = run("audit_task.py", "123", cwd=parent)
        require(
            archive_ok.returncode == 0 and "[unknown-dir]" not in archive_ok.stdout,
            "Archive/ itself must be ignored by the audit",
            archive_ok.stdout,
        )
        fact_path.write_text(fact_text + "\n[old](../Archive/v1/dummy.md)\n", encoding="utf-8")
        archive_link = run("audit_task.py", "123", cwd=parent)
        require(
            archive_link.returncode == 1 and "[archive-link]" in archive_link.stdout,
            "a durable link into Archive/ must fail",
            archive_link.stdout,
        )
        fact_path.write_text(fact_text, encoding="utf-8")

        # --- second scaffold: structure does not depend on mode -------------
        second = parent / "APP-001"
        second.mkdir()
        second_created = run("init_task.py", "--id", "APP-001", "--mode", "perf", "--date", "2026-01-02", cwd=parent)
        require(second_created.returncode == 0, "perf-mode scaffold failed", second_created.stdout)
        require(not (second / "APP-001").exists(), "existing TaskID folder was nested instead of reused")
        second_names = {entry.name for entry in second.iterdir()}
        for name in ("Context", "Tools", "Traces", "Process", "index.md", "steps.md"):
            require(name not in second_names, f"perf mode created {name}; structure must not depend on mode")
        require((second / "Logs").is_dir() and (second / "tools").is_dir(), "perf mode must create Logs/ and tools/")
        fill_standard(second)
        second_green = run("audit_task.py", "APP-001", cwd=parent)
        require(second_green.returncode == 0, "filled perf-mode scaffold must pass", second_green.stdout)

        second_readme = second / "README.md"
        replace_in(
            second_readme,
            HISTORY_PLACEHOLDER,
            "| 01 | 2026-01-02 | first | done | — |\n| 02 | 2026-01-03 | second | done | — |",
        )
        ascending = run("audit_task.py", "APP-001", cwd=parent)
        require(
            ascending.returncode == 1 and "[readme-steps-order]" in ascending.stdout,
            "ascending README history must fail",
            ascending.stdout,
        )
        replace_in(
            second_readme,
            "| 01 | 2026-01-02 | first | done | — |\n| 02 | 2026-01-03 | second | done | — |",
            HISTORY_PLACEHOLDER,
        )

        replace_in(second_readme, STATE_WAIT, "**Состояние:** almost done")
        garbage_state = run("audit_task.py", "APP-001", cwd=parent)
        require(
            garbage_state.returncode == 1 and "[state-line]" in garbage_state.stdout,
            "an unparseable state line must fail",
            garbage_state.stdout,
        )
        replace_in(second_readme, "**Состояние:** almost done", STATE_WAIT)

        # --- external knowledge base wiring ---------------------------------
        kb = parent / "kb"
        kb.mkdir()
        (kb / "README.md").write_text(
            "# Knowledge — внешняя база знаний\n\n"
            "Последние выданные ID: F-02 · H-01\n\n"
            "## Факты\n\n"
            "| ID | Tags | Problem | Описание | Источник / срез |\n|---|---|---|---|---|\n"
            "| [F-01](single-player.md) | Player | фризы ленты | плеер держит один экземпляр | dev abc1234, 2026-01-02<br>Задачи: WIBE-001 |\n"
            "| [F-02](token-ttl.md) | App, auth | — | токен живёт час | dev abc1234, 2026-01-02 |\n\n"
            "## Гипотезы\n\n"
            "| ID | Tags | Вопрос или механизм | Статус | Источник / срез |\n"
            "|---|---|---|---|---|\n"
            "| [H-01](small-buffer.md) | Player | буфер слишком мал | кандидат | dev abc1234 |\n",
            encoding="utf-8",
        )
        (kb / "single-player.md").write_text("# Плеер держит один экземпляр\n\n> ID: `F-01` · Tags: Player\n", encoding="utf-8")
        (kb / "token-ttl.md").write_text("# Токен живёт час\n\n> ID: `F-02` · Tags: App, auth\n", encoding="utf-8")
        (kb / "small-buffer.md").write_text("# Буфер слишком мал\n\n> ID: `H-01` · Tags: Player · Статус: кандидат\n", encoding="utf-8")

        kb_created = run("init_task.py", "--id", "KB-900", "--date", "2026-01-02", "--kb", str(kb), cwd=parent)
        require(kb_created.returncode == 0, "scaffold with --kb failed", kb_created.stdout)
        kb_task = parent / "KB-900"
        env_file = kb_task / "env.json"
        env_data = json.loads(env_file.read_text(encoding="utf-8"))
        require(env_data.get("external_knowledge") == str(kb), "--kb must fill external_knowledge")
        fill_standard(kb_task)
        kb_green = run("audit_task.py", "KB-900", cwd=parent)
        require(
            kb_green.returncode == 0 and "предупреждений 0" in kb_green.stdout,
            "reachable base must audit clean",
            kb_green.stdout,
        )
        kb_brief = run("restore_task.py", "KB-900", "--section", "kb", cwd=parent)
        require(
            "ВНЕШНЯЯ БАЗА" in kb_brief.stdout
            and "фактов 2" in kb_brief.stdout
            and "гипотез 1" in kb_brief.stdout
            and "Player 2" in kb_brief.stdout,
            "restore must show the base with tag counts",
            kb_brief.stdout,
        )

        kb_fact = kb_task / "Knowledge" / "F-01-problem-and-targets.md"
        original_kb_fact = kb_fact.read_text(encoding="utf-8")
        kb_fact.write_text(original_kb_fact + f"\n[плеер один]({kb}/single-player.md)\n", encoding="utf-8")
        kb_link = run("audit_task.py", "KB-900", cwd=parent)
        require(
            kb_link.returncode == 0 and "[kb-link]" in kb_link.stdout,
            "a Markdown link into the base must warn",
            kb_link.stdout,
        )
        kb_fact.write_text(original_kb_fact, encoding="utf-8")

        kb.rename(parent / "kb-moved")
        unreachable = run("audit_task.py", "KB-900", cwd=parent)
        require(
            unreachable.returncode == 0 and "[kb-unreachable]" in unreachable.stdout,
            "a dead base path must be a warning",
            unreachable.stdout,
        )
        (parent / "kb-moved").rename(kb)

        env_file.write_text("не json\n", encoding="utf-8")
        bad_env = run("audit_task.py", "KB-900", cwd=parent)
        require(bad_env.returncode == 1 and "[env-format]" in bad_env.stdout, "broken env.json must fail", bad_env.stdout)
        env_file.unlink()
        missing_env = run("audit_task.py", "KB-900", cwd=parent)
        require(
            missing_env.returncode == 1 and "[env-missing]" in missing_env.stdout,
            "absent env.json must be an error in v2",
            missing_env.stdout,
        )

        # --- foreign and legacy shapes, migration ---------------------------
        foreign = parent / "OLD-001" / "Process" / "steps"
        foreign.mkdir(parents=True)
        (foreign / "step-01.md").write_text("# step 01\n", encoding="utf-8")
        blocked = run("init_task.py", "--id", "OLD-001", cwd=parent)
        require(blocked.returncode == 2 and "неканоническая структура" in blocked.stdout, "init must refuse a foreign folder", blocked.stdout)
        foreign_audit = run("audit_task.py", "OLD-001", cwd=parent)
        require(
            foreign_audit.returncode == 1 and "[unsupported-layout]" in foreign_audit.stdout,
            "audit must report a foreign folder",
            foreign_audit.stdout,
        )
        foreign_restore = run("restore_task.py", "OLD-001", cwd=parent)
        require(foreign_restore.returncode == 2 and "вне канона" in foreign_restore.stdout, "restore must refuse a foreign folder", foreign_restore.stdout)
        foreign_migrate = run("migrate_task.py", "OLD-001", cwd=parent)
        require(foreign_migrate.returncode == 2, "migrate must refuse a foreign folder", foreign_migrate.stdout)

        legacy = parent / "OLD-100"
        legacy.mkdir()
        build_legacy_fixture(legacy)
        legacy_audit = run("audit_task.py", "OLD-100", cwd=parent)
        require(
            legacy_audit.returncode == 1 and "[legacy-layout]" in legacy_audit.stdout,
            "audit must report a v1 folder instead of reading it",
            legacy_audit.stdout,
        )
        legacy_restore = run("restore_task.py", "OLD-100", cwd=parent)
        require(
            legacy_restore.returncode == 2 and "migrate_task.py" in legacy_restore.stdout,
            "restore must refuse a v1 folder and point at migrate_task.py",
            legacy_restore.stdout,
        )
        legacy_init = run("init_task.py", "--id", "OLD-100", cwd=parent)
        require(legacy_init.returncode == 2 and "v1" in legacy_init.stdout, "init must refuse to overlay a v1 folder", legacy_init.stdout)

        dry = run("migrate_task.py", "OLD-100", "--dry-run", cwd=parent)
        require(dry.returncode == 0 and (legacy / "index.md").is_file(), "dry-run must not change the folder", dry.stdout)

        migrated = run("migrate_task.py", "OLD-100", cwd=parent)
        require(migrated.returncode == 0, "migration failed", migrated.stdout)
        for relative in ("index.md", "steps.md", "Context"):
            require(not (legacy / relative).exists(), f"migration left {relative} at the root")
        for relative in (
            "Archive/v1/index.md", "Archive/v1/steps.md", "Archive/v1/README.md",
            "Archive/v1/Context/00-START-HERE.md", "Archive/v1/Steps/Step-01-result.md",
        ):
            require((legacy / relative).is_file(), f"migration did not archive {relative}")
        require((legacy / "tools" / "calc.py").is_file(), "migration must move Context/tools/ to tools/")
        require((legacy / "env.json").is_file(), "migration must create env.json when absent")
        merged_step = (legacy / "Steps" / "Step-01.md").read_text(encoding="utf-8")
        require("**Вердикт:** пары сливаются" in merged_step, "merged step must carry the verdict")
        require("## Задействованные знания" in merged_step, "merged step must carry the knowledge footer")
        migrated_env_fact = legacy / "Knowledge" / "F-02-environment.md"
        require(migrated_env_fact.is_file(), "migration must extract the environment fact")

        post_audit = run("audit_task.py", "OLD-100", cwd=parent)
        require(post_audit.returncode == 0, "migrated folder must audit clean", post_audit.stdout)
        post_restore = run("restore_task.py", "OLD-100", cwd=parent)
        require(
            post_restore.returncode == 0 and "структура standard" in post_restore.stdout,
            "migrated folder must restore as standard",
            post_restore.stdout,
        )

        already = run("migrate_task.py", "123", cwd=parent)
        require(already.returncode == 2 and "уже" in already.stdout, "migrate must refuse a v2 folder", already.stdout)

        (parent / "left" / "DUP-001").mkdir(parents=True)
        (parent / "right" / "DUP-001").mkdir(parents=True)
        ambiguous = run("resolve_task.py", "DUP-001", cwd=parent)
        require(ambiguous.returncode == 2 and "неоднозначен" in ambiguous.stdout, "duplicate TaskID must not resolve silently", ambiguous.stdout)

    print("task-lab self-test: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
