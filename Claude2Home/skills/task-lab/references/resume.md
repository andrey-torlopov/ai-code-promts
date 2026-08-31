# Resume an existing task

## 1. Get the bounded brief

```bash
python3 <skill>/scripts/restore_task.py APP-001 [--workspace <search-root>]
```

An explicit path wins. A bare TaskID requires one exact directory-name match; ambiguity is an
error. The brief reports what the folder claims, not proof that the world still matches.

## 2. Run drift checks

Read `Context/90-session-restore.md` and verify authoritative revision, dependency pins,
toolchain/environment, relevant working-tree changes, comparable observations, and task files
newer than the first history row. Record drift before acting.

## 3. Check the structure

- `steps.md` plus `Steps/` → canonical; the unmatched `Step-XX.md` is current.
- `Process/steps/` or `Steps/_next.md` → stop. The folder was built on another shape: the scripts
  refuse it, and reading it as if it were canonical produces a wrong current step. Say so, and offer
  a migration as its own explicitly requested task.
- neither `Steps/` nor `steps.md` → this is not a task folder; do not scaffold over it silently.

Never silently migrate a folder built on another shape: migration rewrites history and every entry
point.

## 4. Read only what execution requires

Canonical order:

1. `index.md`;
2. `Context/00-START-HERE.md` in full;
3. `steps.md`;
4. the unmatched `Steps/Step-XX.md`, if one exists;
5. only files required by that plan;
6. `Knowledge/README.md` only when registry context is needed;
7. root `env.json` and the external base registry it names — only when the pointer is
   non-empty and the step needs base context.

If there is no unmatched plan, wait for the user's concrete request. When it arrives, create the
next sequential `Step-XX.md` before substantive execution. Never infer and pre-create a future
step from the queue.

## 5. Continue, do not restart

Search Knowledge — and the external base named by `env.json`, when the pointer is set —
before proposing a direction already tested. Persist findings during the turn.
When execution ends for any reason, write the matching result, update the descending root history,
synchronize projections, and run audit plus restore.
