# Lifecycle: create → resume → close

## 1. Decide whether persistence is warranted

Use a folder when work spans sessions, has competing explanations, needs user/device actions,
produces reusable research, or compares observations. If one obvious edit closes the request, do
the edit. If the user explicitly requests a task folder, create it regardless of work type.

## 2. Bootstrap

Read the named subject and existing materials before asking. Ask only for missing decisions: user
goal, success condition, invalidating constraints, undiscoverable prior attempts, required output.
Keep `general` unless `bug`, `perf`, or `plan` materially improves the gate.

```bash
python3 <skill>/scripts/init_task.py --id APP-001 \
  [--workspace <root>] [--title "..."] [--mode general] [--with-inbox] [--kb <path>]
```

The command refuses to overwrite files, to overlay a v1 folder (`index.md`, `steps.md`,
`Context/` → `migrate_task.py`), and to overlay a foreign shape. It leaves `Steps/` empty: the
initializer never invents a step.

Fill in dependency order, replacing every `{{FILL_*}}` marker:

1. `Knowledge/F-01-problem-and-targets.md` — goal, scope, success criterion.
2. `Knowledge/F-02-environment.md` — authoritative subject, revisions, check commands.
3. `README.md` — «Задача», «Правила задачи» (invariants), drift table, queue candidates.
4. `Knowledge/README.md` — facts and hypotheses already discovered from reading the subject.

If input material exists, pass `--with-inbox`, keep only inputs there, and extract durable claims
into `Knowledge/` without links back. When `env.json` points at an external base (`--kb <path>`),
read the base registry filtered by relevant `Tags` before filling `Knowledge/` — settled entries
are cited as dated text instead of being rediscovered.

If the same user request also asks for substantive work, create `Steps/Step-01.md` after the base
context is filled and before execution. Verify: `audit_task.py` and `restore_task.py` must both
resolve the same folder, report structure `standard`, and accept the no-open-step state.

## 3. Resume

```bash
python3 <skill>/scripts/restore_task.py APP-001 [--workspace <search-root>]
```

The brief reports what the folder claims, not proof that the world still matches. Then:

1. **Drift check** — the README table «Проверить при возобновлении»: authoritative revision,
   working tree, pins, environment, task files newer than the top history row, external base.
   Record observed drift as scratch in `Notes/` (exempt edit); repair it with a superseding fact
   or a later step — never by editing a historical result into agreement with today.
2. **Structure check** — `README.md` with a state line plus `Steps/` → canonical. `index.md`,
   root `steps.md`, or `Context/` → v1: stop, offer `migrate_task.py` as its own explicitly
   requested run. `Process/steps/` or `Steps/_next.md` → foreign shape: stop. Neither `README.md`
   nor `Steps/` → not a task folder; do not scaffold over it silently.
3. **Continue, do not restart.** Search `Knowledge/` — and the external base named by `env.json`,
   when the pointer is set — before proposing a direction; respect «Не предлагать повторно».

## Recovery budget

A fresh agent must identify the correct current action from a bounded read, regardless of folder
size:

```text
restore_task.py output
  + README.md, целиком
  + the open Steps/Step-NN.md — or, when none is open, the latest closed one (the checkpoint:
    verdict + «Задействованные знания»)
  + Knowledge/README.md — only when changing direction or after a dead end
  + only files the open plan names; the external base only when env.json points at one
```

Continuing the same direction needs the first three items: the checkpoint's knowledge footer leads
straight to the F/H files that matter. If no step is open, the correct recovered action is to wait
for the user's request, not to promote a queue item silently.

Recovery failure signals — any one blocks a clean-state claim:

- more than one step with status `выполняется`, or an open step that is not the highest number;
- the README state line contradicts the actual open step;
- a closed step misses «Что сделано», «Результат» with a verdict, or «Задействованные знания»;
- completed rows in README «Шаги» are not descending, or a closed step has no row;
- README claims Results is empty while payload files exist;
- a durable file links into `Inbox/` or `Archive/`;
- generated `{{FILL_*}}` markers remain.

## After every step close

```text
[ ] Step-NN.md preserves the request and the frozen plan; «Что сделано» records actual actions
[ ] «Результат» starts with an honest verdict; evidence, changed artifacts, limits, debts recorded
[ ] «Задействованные знания» names every F/H used, checked, refuted, or created («нет» is valid)
[ ] durable claims are in Knowledge/ and registered; «Шаги» column updated
[ ] README state line says «открытого шага нет…» (unless a newer request already opened one)
[ ] completed step is the first row of README «Шаги»; older steps descend below it
[ ] «Рекомендуемая очередность» re-ranked: short self-contained items, no internal ids
[ ] no speculative future Step file exists
[ ] no durable Markdown link targets Inbox/ or Archive/
[ ] task scripts are in tools/; raw output in Logs/; scratch prose in Notes/
[ ] no folder outside the canonical set appeared
[ ] exported claims carry the export mark and agree with the external base registry
[ ] audit_task.py exits 0; restore_task.py prints the correct next action
```

A debt carried through three completed steps is a decision: do it or record why it remains
deferred and what it blocks (`decisions.md`).

## Inbox retirement

Inbox deletion is separate and user-authorized: audit must report no Inbox dependency, durable
claims must have non-Inbox evidence, Results must be self-contained, and removal/recoverability
must be recorded in the step result.

## Close the task

Close the final user request with a normal step and an overall verdict against `F-01`. Leave no
open step, update the README, record remaining questions/debts and owners, and run audit plus
restore. Do not create a synthetic closed-state file.
