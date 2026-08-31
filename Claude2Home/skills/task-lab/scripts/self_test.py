#!/usr/bin/env python3
"""Regression smoke tests for task-lab scripts; standard library only."""

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


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="task-lab-self-test-") as temporary:
        parent = Path(temporary)

        created = run(
            "init_task.py",
            "--id", "123",
            "--date", "2026-01-02",
            "--with-inbox",
            cwd=parent,
        )
        require(created.returncode == 0, "standard scaffold failed", created.stdout)
        standard = parent / "123"

        # The canonical shape is exactly the one of the reference task folder.
        for relative in (
            "README.md", "index.md", "steps.md", "env.json",
            "Context/00-START-HERE.md", "Context/10-repo-and-revisions.md",
            "Context/20-code-map.md", "Context/30-method.md",
            "Context/40-queue.md", "Context/90-session-restore.md",
            "Knowledge/README.md", "Knowledge/F-01-problem-and-targets.md",
            "Results/README.md", "Inbox/README.md",
        ):
            require((standard / relative).is_file(), f"canonical scaffold missed {relative}")
        env_default = json.loads((standard / "env.json").read_text(encoding="utf-8"))
        require(
            env_default.get("external_knowledge") == "",
            "default env.json must carry an empty external_knowledge pointer",
        )
        require(
            "Рекомендуемая очередность" in (standard / "steps.md").read_text(encoding="utf-8"),
            "steps.md template must carry the recommended-order block",
        )
        for relative in ("Steps", "Notes", "Logs", "Context/tools"):
            require((standard / relative).is_dir(), f"canonical scaffold missed {relative}/")
        require(
            not (standard / "Notes" / "Logs").exists(),
            "Logs/ must be a root sibling of Notes/, not nested inside it",
        )
        for relative in ("Process", "Tools", "Traces", "Hypotheses", "timeline.md",
                         "Steps/README.md", "Steps/_next.md", "Context/10-subject.md",
                         "Context/20-map.md"):
            require(not (standard / relative).exists(), f"canonical scaffold created forbidden {relative}")
        require(not (standard / "env.md").exists(), "legacy env.md must not be scaffolded")

        red = run("audit_task.py", "123", cwd=parent)
        require(red.returncode == 1 and "[placeholder]" in red.stdout, "unfilled standard scaffold must fail", red.stdout)

        fill_standard(standard)
        green = run("audit_task.py", "123", cwd=parent)
        require(green.returncode == 0, "filled standard scaffold must pass", green.stdout)
        require("предупреждений 0" in green.stdout, "clean scaffold must not warn", green.stdout)

        brief = run("restore_task.py", "123", "--section", "step", cwd=parent)
        require(
            brief.returncode == 0
            and "структура standard" in brief.stdout
            and "открытого шага нет; ждать запроса пользователя" in brief.stdout,
            "new scaffold must wait for a user request",
            brief.stdout,
        )

        step_01 = standard / "Steps" / "Step-01.md"
        step_01.write_text(
            "# Шаг 01 — проверить парный контракт\n\n"
            "**Статус:** выполняется\n\n"
            "## Запрос пользователя\nПроверить шаг.\n\n"
            "## Вопрос шага\nРаботает ли контракт?\n\n"
            "## Границы\nТолько self-test.\n\n"
            "## Действия\n1. Запустить аудит.\n\n"
            "## Критерий завершения\nАудит проходит.\n",
            encoding="utf-8",
        )
        readme = standard / "README.md"
        readme.write_text(
            readme.read_text(encoding="utf-8").replace(
                "| Текущий шаг | Нет. Следующий запрос пользователя создаст `Steps/Step-01.md` |",
                "| Текущий шаг | **Шаг 01** — [план](Steps/Step-01.md) |",
            ),
            encoding="utf-8",
        )
        index = standard / "index.md"
        index.write_text(
            index.read_text(encoding="utf-8").replace(
                "| Следующее действие | Ждать запроса пользователя; он создаст `Steps/Step-01.md` |",
                "| Следующее действие | Выполнить **шаг 01** из `Steps/Step-01.md` |",
            ),
            encoding="utf-8",
        )
        history = standard / "steps.md"
        history.write_text(
            history.read_text(encoding="utf-8").replace(
                "**Нет.** Следующий запрос пользователя создаст `Steps/Step-01.md`.",
                "**Шаг 01** — [план](Steps/Step-01.md), выполняется.",
            ),
            encoding="utf-8",
        )
        open_green = run("audit_task.py", "123", cwd=parent)
        require(open_green.returncode == 0, "one unmatched canonical step must be valid", open_green.stdout)
        open_brief = run("restore_task.py", "123", "--section", "step", cwd=parent)
        require("номер: 01" in open_brief.stdout, "restore did not locate canonical Step-01", open_brief.stdout)

        step_01_result = standard / "Steps" / "Step-01-result.md"
        step_01_result.write_text(
            "# Шаг 01 — результат: контракт работает\n\n"
            "**Статус:** завершён\n"
            "**Дата:** 2026-01-02\n"
            "**Вердикт:** парный контракт проверен.\n\n"
            "## Доказательства\nАудит завершился без ошибок.\n\n"
            "## Ограничения и долги\nНет.\n",
            encoding="utf-8",
        )
        history.write_text(
            history.read_text(encoding="utf-8").replace(
                "| — | — | завершённых шагов нет | — | — |",
                "| 01 | 2026-01-02 | проверить парный контракт | работает | "
                "[план](Steps/Step-01.md) · [результат](Steps/Step-01-result.md) |",
            ).replace(
                "**Шаг 01** — [план](Steps/Step-01.md), выполняется.",
                "**Нет.** Следующий запрос пользователя создаст `Steps/Step-02.md`.",
            ),
            encoding="utf-8",
        )
        readme.write_text(
            readme.read_text(encoding="utf-8").replace(
                "| Текущий шаг | **Шаг 01** — [план](Steps/Step-01.md) |",
                "| Текущий шаг | Нет. Следующий запрос пользователя создаст `Steps/Step-02.md` |",
            ),
            encoding="utf-8",
        )
        index.write_text(
            index.read_text(encoding="utf-8").replace(
                "| Следующее действие | Выполнить **шаг 01** из `Steps/Step-01.md` |",
                "| Следующее действие | Ждать запроса пользователя; он создаст `Steps/Step-02.md` |",
            ),
            encoding="utf-8",
        )
        paired_green = run("audit_task.py", "123", cwd=parent)
        require(paired_green.returncode == 0, "completed canonical pair must pass", paired_green.stdout)

        # An edit to a durable file after the last step closed must be reported;
        # scratch in Notes/, raw output in Logs/, and the projections synchronised
        # while closing the step must not be.
        late = time.time() + 40 * 60
        fact_path = standard / "Knowledge" / "F-01-problem-and-targets.md"
        os.utime(fact_path, (late, late))
        late_audit = run("audit_task.py", "123", cwd=parent)
        require(
            "[edit-outside-step]" in late_audit.stdout and late_audit.returncode == 0,
            "edit of a durable file outside a step must be a warning, not an error",
            late_audit.stdout,
        )
        os.utime(fact_path, None)
        note = standard / "Notes" / "n1.md"
        note.write_text("черновая заметка\n", encoding="utf-8")
        raw_log = standard / "Logs" / "run.log"
        raw_log.write_text("2026-01-02 10:00 старт\n", encoding="utf-8")
        os.utime(note, (late, late))
        os.utime(raw_log, (late, late))
        for projection in ("README.md", "index.md", "steps.md", "Context/90-session-restore.md"):
            os.utime(standard / projection, (late, late))
        exempt_audit = run("audit_task.py", "123", cwd=parent)
        require(
            "[edit-outside-step]" not in exempt_audit.stdout,
            "Notes/, Logs/ and the closing projections are exempt from the every-edit-is-a-step check",
            exempt_audit.stdout,
        )
        require(
            "[observation-misplaced]" not in exempt_audit.stdout,
            "a raw .log in root Logs/ is correctly placed",
            exempt_audit.stdout,
        )

        # Logs/ is a sibling of Notes/, not its content: the same file inside Notes/ is misplaced.
        raw_log.rename(standard / "Notes" / "run.log")
        misplaced_log = run("audit_task.py", "123", cwd=parent)
        require(
            "[observation-misplaced]" in misplaced_log.stdout,
            "a raw .log inside Notes/ must be reported; it belongs in root Logs/",
            misplaced_log.stdout,
        )
        (standard / "Notes" / "run.log").unlink()
        note.unlink()

        nested_logs = standard / "Notes" / "Logs"
        nested_logs.mkdir()
        (nested_logs / "run.log").write_text("вложенный лог\n", encoding="utf-8")
        nested_audit = run("audit_task.py", "123", cwd=parent)
        require(
            nested_audit.returncode == 1 and "[logs-nested]" in nested_audit.stdout,
            "Logs/ nested inside another folder must be an error, not a silent second location",
            nested_audit.stdout,
        )
        (nested_logs / "run.log").unlink()
        nested_logs.rmdir()

        orphan = standard / "Steps" / "Step-02-result.md"
        orphan.write_text("# Шаг 02 — результат: orphan\n", encoding="utf-8")
        orphan_audit = run("audit_task.py", "123", cwd=parent)
        require("[step-orphan]" in orphan_audit.stdout, "orphan result must fail audit", orphan_audit.stdout)
        orphan.unlink()

        tool = standard / "Context" / "tools" / "calc.py"
        tool.write_text("print(83 / 242)\n", encoding="utf-8")
        tool_green = run("audit_task.py", "123", cwd=parent)
        require(
            tool_green.returncode == 0 and "tool-" not in tool_green.stdout,
            "Context/tools/ is the canonical place for task scripts",
            tool_green.stdout,
        )
        misplaced = standard / "Knowledge" / "calc.py"
        misplaced.write_text("print(1)\n", encoding="utf-8")
        misplaced_audit = run("audit_task.py", "123", cwd=parent)
        require(
            "[tool-misplaced]" in misplaced_audit.stdout,
            "script outside Context/tools/ must be reported",
            misplaced_audit.stdout,
        )
        misplaced.unlink()

        retired = standard / "Traces"
        retired.mkdir()
        (retired / "runs.md").write_text("# runs\n", encoding="utf-8")
        retired_audit = run("audit_task.py", "123", cwd=parent)
        require(
            "[retired-dir]" in retired_audit.stdout,
            "Traces/ is no longer part of the structure and must be reported",
            retired_audit.stdout,
        )
        (retired / "runs.md").unlink()
        retired.rmdir()

        fact = standard / "Knowledge" / "F-01-problem-and-targets.md"
        fact.write_text(fact.read_text(encoding="utf-8") + "\n[bad](../Inbox/README.md)\n", encoding="utf-8")
        result = standard / "Results" / "README.md"
        result.write_text(result.read_text(encoding="utf-8") + "\n[bad](../Knowledge/README.md)\n", encoding="utf-8")
        boundaries = run("audit_task.py", "123", cwd=parent)
        require(
            boundaries.returncode == 1
            and "[inbox-link]" in boundaries.stdout
            and "[result-external-link]" in boundaries.stdout,
            "Inbox/Results boundary checks failed",
            boundaries.stdout,
        )

        second = parent / "APP-001"
        second.mkdir()
        second_created = run(
            "init_task.py",
            "--id", "APP-001",
            "--mode", "perf",
            "--date", "2026-01-02",
            cwd=parent,
        )
        require(second_created.returncode == 0, "perf-mode scaffold failed", second_created.stdout)
        require(not (second / "APP-001").exists(), "existing TaskID folder was nested instead of reused")
        for relative in ("Traces", "Tools", "Process"):
            require(not (second / relative).exists(), f"perf mode created {relative}; structure must not depend on mode")
        require((second / "Logs").is_dir(), "perf mode must create root Logs/ like every other mode")
        fill_standard(second)
        second_green = run("audit_task.py", "APP-001", cwd=parent)
        require(second_green.returncode == 0, "filled perf-mode scaffold must pass", second_green.stdout)

        steps_registry = second / "steps.md"
        original_steps = steps_registry.read_text(encoding="utf-8")
        ascending_steps = original_steps.replace(
            "| — | — | завершённых шагов нет | — | — |",
            "| 01 | 2026-01-02 | first | done | Steps/Step-01-result.md |\n"
            "| 02 | 2026-01-03 | second | done | Steps/Step-02-result.md |",
        )
        steps_registry.write_text(ascending_steps, encoding="utf-8")
        bad_step_order = run("audit_task.py", "APP-001", cwd=parent)
        require(
            bad_step_order.returncode == 1 and "[step-registry-order]" in bad_step_order.stdout,
            "ascending completed-step registry must fail",
            bad_step_order.stdout,
        )
        steps_registry.write_text(original_steps, encoding="utf-8")

        # Q-NN is Context-internal: leaking it into a user-facing file must fail.
        steps_registry.write_text(
            original_steps + "\nСледующим стоит закрыть Q-01 из очереди.\n", encoding="utf-8"
        )
        queue_leak = run("audit_task.py", "APP-001", cwd=parent)
        require(
            queue_leak.returncode == 1 and "[queue-leak]" in queue_leak.stdout,
            "Q-NN outside Context/ must fail the audit",
            queue_leak.stdout,
        )
        steps_registry.write_text(original_steps, encoding="utf-8")

        # --- External knowledge base wiring: env.json, restore section, audit checks ---
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
        (kb / "single-player.md").write_text(
            "# Плеер держит один экземпляр\n\n> ID: `F-01` · Tags: Player\n", encoding="utf-8"
        )
        (kb / "token-ttl.md").write_text(
            "# Токен живёт час\n\n> ID: `F-02` · Tags: App, auth\n", encoding="utf-8"
        )
        (kb / "small-buffer.md").write_text(
            "# Буфер слишком мал\n\n> ID: `H-01` · Tags: Player · Статус: кандидат\n", encoding="utf-8"
        )

        kb_created = run(
            "init_task.py",
            "--id", "KB-900",
            "--date", "2026-01-02",
            "--kb", str(kb),
            cwd=parent,
        )
        require(kb_created.returncode == 0, "scaffold with --kb failed", kb_created.stdout)
        kb_task = parent / "KB-900"
        env_file = kb_task / "env.json"
        require(env_file.is_file(), "scaffold must create root env.json")
        env_data = json.loads(env_file.read_text(encoding="utf-8"))
        require(
            env_data.get("external_knowledge") == str(kb),
            "--kb must fill external_knowledge with the base path",
        )
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
        kb_fact.write_text(
            original_kb_fact + f"\n[плеер один]({kb}/single-player.md)\n", encoding="utf-8"
        )
        kb_link = run("audit_task.py", "KB-900", cwd=parent)
        require(
            kb_link.returncode == 0 and "[kb-link]" in kb_link.stdout,
            "Markdown link into the base must warn: cite as dated text",
            kb_link.stdout,
        )
        kb_fact.write_text(original_kb_fact, encoding="utf-8")

        kb.rename(parent / "kb-moved")
        unreachable = run("audit_task.py", "KB-900", cwd=parent)
        require(
            unreachable.returncode == 0 and "[kb-unreachable]" in unreachable.stdout,
            "dead base path must be a warning, not an error",
            unreachable.stdout,
        )
        (parent / "kb-moved").rename(kb)

        env_file.write_text("не json\n", encoding="utf-8")
        bad_env = run("audit_task.py", "KB-900", cwd=parent)
        require(
            bad_env.returncode == 1 and "[env-format]" in bad_env.stdout,
            "broken env.json must fail",
            bad_env.stdout,
        )
        env_file.unlink()
        missing_env = run("audit_task.py", "KB-900", cwd=parent)
        require(
            missing_env.returncode == 0 and "[env-missing]" in missing_env.stdout,
            "absent env.json must be a warning, not an error",
            missing_env.stdout,
        )

        foreign = parent / "OLD-001" / "Process" / "steps"
        foreign.mkdir(parents=True)
        (foreign / "step-01.md").write_text("# step 01\n", encoding="utf-8")
        blocked_overlay = run("init_task.py", "--id", "OLD-001", cwd=parent)
        require(
            blocked_overlay.returncode == 2 and "неканоническая структура" in blocked_overlay.stdout,
            "initializer must refuse to overlay a non-canonical folder",
            blocked_overlay.stdout,
        )
        foreign_audit = run("audit_task.py", "OLD-001", cwd=parent)
        require(
            foreign_audit.returncode == 1 and "[unsupported-layout]" in foreign_audit.stdout,
            "audit must report a non-canonical folder instead of reading it",
            foreign_audit.stdout,
        )
        foreign_restore = run("restore_task.py", "OLD-001", cwd=parent)
        require(
            foreign_restore.returncode == 2 and "вне канона" in foreign_restore.stdout,
            "restore must refuse a non-canonical folder",
            foreign_restore.stdout,
        )

        (parent / "left" / "DUP-001").mkdir(parents=True)
        (parent / "right" / "DUP-001").mkdir(parents=True)
        ambiguous = run("resolve_task.py", "DUP-001", cwd=parent)
        require(
            ambiguous.returncode == 2 and "неоднозначен" in ambiguous.stdout,
            "duplicate TaskID must not resolve silently",
            ambiguous.stdout,
        )

    print("task-lab self-test: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
