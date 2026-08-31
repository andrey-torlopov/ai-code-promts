# Writing rules

## Audience

- `README.md`: the shared entry point — human-readable prose and tables, with the machine-readable
  state line on top; invariants and thresholds live here too, stated in plain words.
- `Steps/`, `Results/`: user-facing language, observable outcome first.
- `Knowledge/`: concise claim first, evidence and scope next; heavy detail in `_context.md`.

Use the user's language. Do not mix languages inside one file unless quoting a technical symbol.
No internal ids in user-facing prose: queue items and questions are short self-contained sentences
— the wording of a possible future request, not a reference the reader must resolve.

## Journals and registries

```text
first column is time/date → observation journal → newest first
README «Шаги» history     → newest/highest step first
fact/hypothesis ID        → registry → ascending by ID
```

`Notes/runs.md` is an observation journal. `Knowledge/README.md`, `decisions.md`, and
`change-log.md` are registries or journals per this rule. README «Шаги» is a history view, not an
ascending ID registry: insert the newest completed step as the first data row, never below older
history. Observation journals use local task time as `YYYY-MM-DD HH:MM` and also insert newest
rows first.

The external base fact row is `ID | Tags | Problem | Описание | Источник / срез` (hypotheses have
no Problem column), the ID cell linking to the topic file; task folders that touched the entry are
listed as `Задачи:` inside the source cell.

## Numbers

Write the full derivation:

```text
83 / 242 = 34.3% of commits touched the integration contour
```

Include units and scope. Calculate nontrivial values with a script in `tools/` and record its
output. A copied number has one authoritative home; other files link to it or restate it
explicitly only at the `Results/` export boundary.

## Links

- Relative and resolvable.
- Link an entity on first mention; later use its ID.
- Never link a durable artifact into `Inbox/` or `Archive/`; a link into `Notes/` or `Logs/` means
  the claim should have been extracted into `Knowledge/` already. Quote the log line, do not link
  the file.
- Never link from `Results/` outside `Results/`; exported deliverables must stand alone.
- Cite external-base entries as dated plain text (`база F-12 (player), снимок 2026-08-28`),
  never as a Markdown link; restate the substance you rely on.
- Link both directions when one claim supersedes or refutes another.

## Anti-bloat

- One claim per file.
- One open step, one synchronized projection (`README.md`).
- Put long tables, stacks, diffs, and line-by-line code analysis in `_context.md`.
- Delete no historical evidence; add a banner and superseding link.

## Status prose

The state line is the only status claim the audit trusts; keep the rest of the prose explicit and
machine-checkable: "шаги 01–04 завершены", "Results содержит 10 задач". Avoid ambiguous phrases
such as "almost done". Never leave a sentence like "результатов пока нет" after result payloads
exist.
