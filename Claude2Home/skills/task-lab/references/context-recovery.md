# Context recovery contract

A fresh agent must identify the correct current action from a bounded read, regardless of folder
size.

## Canonical recovery budget

```text
restore_task.py output
  + index.md
  + Context/00-START-HERE.md
  + steps.md
  + the sole unmatched Steps/Step-XX.md, if one exists
```

Open additional files only when the request and plan require them. If no plan is unmatched, the
correct recovered action is to wait for the user's request, not to promote a queue item silently.

## Projection roles

| File | Owns |
|---|---|
| unmatched `Steps/Step-XX.md` | current request, scope, actions, completion gate |
| matching `Step-XX-result.md` | verdict, evidence, outputs, limits, debts |
| `steps.md` | current pointer and completed history, newest/highest first |
| `index.md` | agent read order, invariants, compact state |
| `README.md` | human status and navigation |
| `Context/90-session-restore.md` | assumptions that must be rechecked |
| `Knowledge/README.md` | claim inventory and statuses |
| root `env.md` (optional) | external knowledge sources for this task |

State duplication is deliberate because audiences differ; contradiction is a defect. Update all
affected projections in the same turn when a step opens or closes.

## Bounded brief contents

`restore_task.py` shows structure, state, invariants, open step or waiting state, latest completed
pairs, facts/hypotheses, the external base named by `env.md` (path, reachability, counts),
blocking queue items, and exact next reads. It must not dump full entities
or Inbox materials.

## Recovery failure signals

- more than one unmatched `Step-XX.md`;
- a `Step-XX-result.md` without its plan;
- README, index, and `steps.md` name different current steps;
- completed rows in `steps.md` are not descending;
- README says Results is empty while payload files exist;
- a plan depends on an Inbox link;
- generated `{{FILL_*}}` markers appear in the brief.

Any signal above blocks a clean-state claim.
