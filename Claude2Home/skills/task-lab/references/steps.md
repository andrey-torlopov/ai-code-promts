# Steps

## When a step is required

The line is not "how big was the request" but **"did anything in the folder change"**.

```text
the reply is the whole deliverable        → no step
a file changed because the user asked     → step, every time
```

A step is required for: any edit inside `Results/`, `Knowledge/`, `Context/`, `Steps/`, and the
root `README.md` / `index.md` / `steps.md`; any edit to code or documents outside the folder made
on the user's request; a correction of a single sentence, number, heading or link in an existing
report. Size is not a criterion — a one-line fix is a short plan and a short result, which costs a
minute and keeps the history honest.

No step is required for: explaining what was done and why; pointing at where something lives;
quoting or summarising an existing file; reading the subject; running `audit_task.py`,
`restore_task.py` or a search. These produce a reply and nothing else.

Three edits are exempt, and there are no other exemptions:

| Exempt | Why |
|---|---|
| scratch written into `Notes/` | it is working material, not task state; nothing durable depends on it |
| raw output captured into `Logs/` | it is what a command printed, not a claim about the task; the claim is extracted into `Knowledge/` |
| the drift record in `Context/90-session-restore.md` on resume | it states what the world looks like now, not what was done to it |

Failure modes this rule is written against:

- **Silent maintenance.** "While I was here I also fixed…" — an edit nobody requested and nobody
  can find later. Either the user asked (step) or it waits in `Context/40-queue.md`.
- **The tiny-edit exception.** One sentence today, a re-cut table tomorrow, and the history no
  longer explains how the report reached its current shape.
- **The step that eats two requests.** Two requests, even one minute apart, are two verdicts.
  Close the open pair before opening the next one.
- **The opposite failure.** Opening a plan/result pair for a question that never touched a file
  fills the history with rows that record nothing.

If a question becomes a request inside one turn, split the turn: answer, then create the plan,
then edit. If an answer surfaces something worth keeping, recording it is itself an edit — that
recording gets its own step, and the step's request is "record what the question surfaced".

## The step contract

A concrete user request creates `Steps/Step-XX.md`, where `XX` is
`max(existing step numbers) + 1` padded to at least two digits. The step is open until a
matching `Steps/Step-XX-result.md` exists. The folder may validly have no open step while it waits
for the user's next request. Never create a speculative future step.

Required `Step-XX.md` sections:

```markdown
# Шаг XX — action

**Статус:** выполняется

## Запрос пользователя
The request that caused this file to be created.

## Вопрос шага
One answer that closes the step.

## Границы
In scope and out of scope.

## Входы
Durable inputs only; no Inbox links.

## Действия
Executable actions.

## Критерий завершения
Observable done condition.

## Карта вердиктов
Outcome → conclusion → following action, declared before execution where useful.

## Записывает в
The matching result and other durable outputs.
```

When execution ends:

1. create `Step-XX-result.md` with status `завершён`, `отменён`, or `заблокирован`;
2. start with the answer/verdict, then record work, evidence, changed artifacts, limits, debts,
   and knowledge changes;
3. update entities and self-contained results;
4. prepend the completed row in root `steps.md`, preserving descending step order;
5. refresh the recommended-order block in root `steps.md`: re-rank after the verdict and
   restate the top candidates as short self-contained items — no `Q-NN`, no `Context/`
   links; an item is the wording of a future user request, not a pre-numbered step;
6. synchronize README, index, `steps.md`, and restore assumptions to say that no step is
   open unless a newer user request has already opened one;
7. run audit and restore.

Do not rewrite the plan into a result: keep both files. Do not mutate a completed pair to reflect
later knowledge; add a correction in a later pair and link the superseding fact.

## Scope changes

Before substantive execution starts, correct `Step-XX.md` if it misstates the same user request.
After execution starts, a materially changed request is not an edit to history: close the current
step with an `отменён` or `заблокирован` result, then create the next numbered step for the new
request.

## Folders built on another shape

`Process/steps/step-NN.md` and `Steps/_next.md` are not step contracts this skill reads. The scripts
stop on them instead of guessing a current step. Converting such a folder is a separate explicit
change, because it rewrites task history and all entry points.

## One step means one verdict

"Analyse A and implement B" is two steps unless B is a deterministic part of the same gate. A
choice step recommends one option; it does not hand the user an unranked menu. Invalid observation,
wrong question, cancellation, blocking, or early refutation are valid verdicts and close the step
honestly.
