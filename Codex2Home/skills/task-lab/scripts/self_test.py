#!/usr/bin/env python3
"""Regression smoke tests for task-lab scripts; standard library only."""

from __future__ import annotations

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
            "README.md", "index.md", "steps.md",
            "Context/00-START-HERE.md", "Context/10-repo-and-revisions.md",
            "Context/20-code-map.md", "Context/30-method.md",
            "Context/40-queue.md", "Context/90-session-restore.md",
            "Knowledge/README.md", "Knowledge/F-01-problem-and-targets.md",
            "Results/README.md", "Inbox/README.md",
        ):
            require((standard / relative).is_file(), f"canonical scaffold missed {relative}")
        for relative in ("Steps", "Notes", "Context/tools"):
            require((standard / relative).is_dir(), f"canonical scaffold missed {relative}/")
        for relative in ("Process", "Tools", "Traces", "Hypotheses", "timeline.md",
                         "Steps/README.md", "Steps/_next.md", "Context/10-subject.md",
                         "Context/20-map.md"):
            require(not (standard / relative).exists(), f"canonical scaffold created forbidden {relative}")

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
        # scratch in Notes/ and the projections synchronised while closing must not.
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
        os.utime(note, (late, late))
        for projection in ("README.md", "index.md", "steps.md", "Context/90-session-restore.md"):
            os.utime(standard / projection, (late, late))
        exempt_audit = run("audit_task.py", "123", cwd=parent)
        require(
            "[edit-outside-step]" not in exempt_audit.stdout,
            "Notes/ and the closing projections are exempt from the every-edit-is-a-step check",
            exempt_audit.stdout,
        )
        note.unlink()

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
