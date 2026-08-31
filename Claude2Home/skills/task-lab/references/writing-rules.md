# Writing rules

## Audience

- `README.md`, `Steps/`, `Results/`: user-facing language, observable outcome first.
- `index.md`, `Context/`: agent instructions, invariants, IDs, thresholds.
- `Knowledge/`: concise claim first, evidence and scope next; heavy detail in `_context.md`.

Use the user's language. Do not mix languages inside one file unless quoting a technical symbol.

The user does not read `Context/`. `Q-NN` and other `Context/`-registry ids appear only
inside `Context/`; in `README.md`, `steps.md`, `Steps/`, `Knowledge/`, and `Results/` the
item is restated in plain self-contained words. The user-facing queue projection is the
recommended-order block in root `steps.md`.

## Journals and registries

```text
first column is time/date → observation journal → newest first
root steps.md history     → newest/highest step first
fact/hypothesis ID        → registry → ascending by ID
```

`Notes/runs.md` is an observation journal. `Knowledge/README.md`, decisions, questions, and
change logs are registries. Root `steps.md` is a history view, not an ascending ID registry.
The external base fact row is `ID | Tags | Problem | Описание | Источник / срез`
(hypotheses have no Problem column), the ID cell linking to the topic file; task folders
that touched the entry are listed as `Задачи:` inside the source cell.

For `steps.md`, insert the newest completed pair as the first data row. Never append it below older
history. Observation journals use local task time as `YYYY-MM-DD HH:MM` and also insert newest rows
first.

## Numbers

Write the full derivation:

```text
83 / 242 = 34.3% of commits touched the integration contour
```

Include units and scope. Calculate nontrivial values with a script and record its output. A copied
number has one authoritative home; other files link to it or restate it explicitly only at the
`Results/` export boundary.

## Links

- Relative and resolvable.
- Link an entity on first mention; later use its ID.
- Never link a durable artifact into `Inbox/`; a link into `Notes/` or `Logs/` means the claim
  should have been extracted into `Knowledge/` already. Quote the log line, do not link the file.
- Never link from `Results/` outside `Results/`; exported deliverables must stand alone.
- Cite external-base entries as dated plain text (`база F-12 (player), снимок 2026-08-28`),
  never as a Markdown link; restate the substance you rely on.
- Link both directions when one claim supersedes or refutes another.

## Anti-bloat

- One claim per file.
- One current step.
- Put long tables, stacks, diffs, and line-by-line code analysis in `_context.md`.
- Do not duplicate status prose beyond the compact projections that audit compares.
- Delete no historical evidence; add a banner and superseding link.

## Status prose

Use explicit, machine-checkable language: "current step 05", "steps 01–04 completed", "Results
contains 10 tasks". Avoid ambiguous phrases such as "almost done". Never leave a sentence like
"Results is empty" after result payloads exist.
