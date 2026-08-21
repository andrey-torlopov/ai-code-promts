# Bootstrap a task folder

## 1. Decide whether persistence is warranted

Use a folder when work spans sessions, has competing explanations, needs user/device actions,
produces reusable research, or compares observations. If one obvious edit closes the request, do
the edit. If the user explicitly requests a task folder, create it regardless of work type.

## 2. Read before asking

Inspect the named subject and existing materials first. Ask only for missing decisions: user goal,
success condition, invalidating constraints, undiscoverable prior attempts, and required output.
Keep `general` unless `bug`, `perf`, or `plan` materially improves the gate.

## 3. Use the canonical structure

Every new task uses `README.md`, `index.md`, root `steps.md`, `Steps/`, `Context/` (with
`Context/tools/`), `Knowledge/`, `Results/` and `Notes/`. Do not create `Process/`, `timeline.md`,
`Steps/README.md`, `_next.md`, root `Tools/` or root `Traces/`. For noisy measurements add
`Notes/runs.md` and narrowly required context files without changing the step contract.

## 4. Resolve TaskID and scaffold

TaskID is the folder name, not a location convention. Search the workspace for one exact match.
For an explicitly new task with no match, create `<workspace>/<TaskID>`. Stop on multiple matches.

```bash
python3 <skill>/scripts/init_task.py \
  --id APP-001 [--workspace <root>] [--title "Task title"] \
  [--mode general] [--with-inbox]
```

The command refuses to overwrite files or overlay a folder built on another shape. It leaves `Steps/`
without an invented future step. If the same user request also asks for substantive work, create
`Step-01.md` after filling the base context and before execution. If the request only asks to
create the folder, leave `Steps/` empty. Generated `{{FILL_*}}` markers are intentionally invalid.

## 5. Fill in dependency order

1. `Context/00-START-HERE.md`: goal, boundaries, current phase, invariants.
2. `Context/10-repo-and-revisions.md` and `20-code-map.md`: authoritative revisions and subject map.
3. `Context/30-method.md`: what counts as a fact, a finding and an acceptance in this task.
4. `Knowledge/F-01-problem-and-targets.md`: definitions, scope, success.
5. `Knowledge/README.md`: facts and hypotheses already discovered.
6. `Context/40-queue.md`: unnumbered candidates, ranking rule, blocking questions.
7. `steps.md`: no current step and no completed history.
8. `README.md` and `index.md`: the same waiting state for different audiences.

If input material exists, pass `--with-inbox`, keep only inputs there, and extract durable
claims into `Knowledge/` without links back to `Inbox/`. Raw material produced while working —
briefs, logs, observation journals — goes to `Notes/`, which every task has regardless of mode.

## 6. Verify

```bash
python3 <skill>/scripts/audit_task.py APP-001 [--workspace <root>]
python3 <skill>/scripts/restore_task.py APP-001 [--workspace <root>]
```

Both must resolve the same absolute folder, report structure `standard`, and say that no step is
open until the user requests work. Report TaskID, resolved path, state, and any remaining user action.
