# Steps

## When a step is required

The line is not "how big was the request" but **"did anything durable change"**.

```text
the reply is the whole deliverable        → no step
a file changed because the user asked     → step, every time
```

A step is required for: any edit inside `Results/`, `Knowledge/`, `Steps/`, root files
(`README.md`, `decisions.md`, `change-log.md`, `acceptance.md`); any edit to code or documents
outside the folder made on the user's request; a correction of a single sentence, number, heading
or link in an existing report. Size is not a criterion — a one-line fix is a short step, which
costs a minute and keeps the history honest.

No step is required for: explaining what was done and why; pointing at where something lives;
quoting or summarising an existing file; reading the subject; running `audit_task.py`,
`restore_task.py` or a search. These produce a reply and nothing else.

Two edits are exempt, and there are no other exemptions:

| Exempt | Why |
|---|---|
| scratch written into `Notes/` | working material, not task state; nothing durable depends on it — the on-resume drift record included |
| raw output captured into `Logs/` | what a command printed, not a claim about the task; the claim is extracted into `Knowledge/` |

Failure modes this rule is written against:

- **Silent maintenance.** "While I was here I also fixed…" — an edit nobody requested and nobody
  can find later. Either the user asked (step) or it waits in the README queue.
- **The tiny-edit exception.** One sentence today, a re-cut table tomorrow, and the history no
  longer explains how the report reached its current shape.
- **The step that eats two requests.** Two requests, even one minute apart, are two verdicts.
  Close the open step before opening the next one.
- **The opposite failure.** Opening a step for a question that never touched a file fills the
  history with rows that record nothing.

If a question becomes a request inside one turn, split the turn: answer, then open the step, then
edit. If an answer surfaces something worth keeping, recording it is itself an edit — that
recording gets its own step, and the step's request is "record what the question surfaced".

## The step file

One file per step: `Steps/Step-NN.md`, `NN` = `max(existing step numbers) + 1`, zero-padded to at
least two digits. Copy the skeleton from `templates/items/standard/Step-NN.md`.

**At open** the file contains the header and two sections, written before any durable file is
touched:

```markdown
# Шаг NN — action

**Статус:** выполняется · **Дата:** YYYY-MM-DD

## Запрос
The user's request that caused this file to exist, plus the one question that closes the step.

## План
**Границы:** in and out of scope.
**Действия:** 1–5 executable actions.
**Критерий завершения:** the observable done condition — fixed BEFORE execution, otherwise the
criterion gets fitted to the numbers (see references/gates.md). Where useful, add the verdict map:
outcome → conclusion → following action.
```

Update the README state line to «шаг NN открыт · дата» in the same turn.

«Запрос» and «План» are frozen once execution starts. Before substantive execution, correct the
plan if it misstates the same request. After execution starts, a materially changed request closes
the step (`отменён`) and opens the next number.

**At close** — status `завершён`, `отменён`, or `заблокирован` (cancellation and blocking close
the step honestly) — append exactly three sections and delete the skeleton comment:

```markdown
## Что сделано
Actual actions, including deviations from the plan.

## Результат
**Вердикт:** the answer that closes the step, first line.
Evidence and its scope; changed files and artifacts; what was NOT done; limits and debts.

## Задействованные знания
| ID | Роль в шаге |
|---|---|
| F-03 | опора: срез подтверждён |
| H-05 | проверялась; опровергнута — см. Результат |
| F-07 | создан этим шагом |
```

`| — | знаний не задействовано |` is a valid single row. Every F/H the step used, checked,
refuted, or created must be named — the footer is the checkpoint's map back into `Knowledge/`.

The open step is mechanically defined: status `выполняется` and no `## Результат` heading. At
most one step is open, and its number is the highest existing one.

## Closing synchronization (same turn)

1. README state line → «открытого шага нет · ждём запрос пользователя · дата», unless a newer
   user request already opened the next step.
2. The completed step becomes the **first** data row of README «Шаги»; older rows descend below.
3. «Рекомендуемая очередность» is re-ranked after the verdict: short self-contained items, the
   wording of a future user request, never a pre-numbered step, no internal ids.
4. `Knowledge/` updated: new and changed claims, «Шаги» column of the registry.
5. Run audit and restore.

Do not mutate a closed step to reflect later knowledge; add a correction in a later step and link
the superseding fact.

## One step means one verdict

"Analyse A and implement B" is two steps unless B is a deterministic part of the same gate. A
choice step recommends one option; it does not hand the user an unranked menu. Invalid
observation, wrong question, cancellation, blocking, or early refutation are valid verdicts and
close the step honestly.

## Folders built on another shape

`Step-NN-result.md` files, root `steps.md`, `index.md`, and `Context/` are the v1 layout: the
scripts stop on them and point at `migrate_task.py`. `Process/steps/` and `Steps/_next.md` are
foreign shapes: the scripts stop without guessing a current step. Converting either is its own
explicitly requested run, because it rewrites task history and the entry point.
