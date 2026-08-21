# Durable entities

## Locations

| Entity | Where it lives |
|---|---|
| Fact `F-NN` | `Knowledge/F-NN-*.md` |
| Hypothesis `H-NN` | `Knowledge/H-NN-*.md` |
| Decision `D-NN` | `Context/decisions.md`, or a compact registry inside `Context/40-queue.md` |
| Question `Q-NN` | `Context/40-queue.md` |
| Experimental change `P-NN` | `Context/change-log.md`, added when the subject is modified |
| Invariant `INV-NN` | `Context/00-START-HERE.md` |

IDs are permanent, never reused, and sorted ascending in registries. Status lives inside the file:
a finished or refuted claim keeps its ID and its place, with the status written at the top. There is
no archive folder — moving a claim breaks every link to it.

## F-NN — fact

A fact is measured, observed, or read in the authoritative subject. Required:

- atomic claim;
- durable evidence: command, observation, log, or `file:line` at a named revision;
- scope: revision, environment, device/dataset/configuration where relevant;
- full number derivation when numeric;
- consequence and limit of the claim.

`Inbox/` is not durable evidence. An Inbox draft may suggest a fact, but the fact file cites the
real subject or the reproducible check used to verify it.

A contradiction does not erase an old observation. Add a new fact, mark the old conclusion
superseded or refuted, and link both ways. A fact that is finished but still true keeps its file and
gains a status line with the date and the condition that would reopen it.

## H-NN — hypothesis

A hypothesis is an unverified cause, change, or design premise. Required:

- status;
- concrete mechanism or question;
- facts it is based on, or an explicit `guess` label;
- falsifiable expected outcome with a threshold;
- cheapest discriminating gate;
- outcome map: what confirmation and refutation each imply;
- risk and how to notice it when the hypothesis proposes a change.

Useful statuses: `candidate`, `in progress`, `confirmed`, `demoted`, `refuted`, `blocked`,
`deferred`. Demotion is not refutation. Preserve refutations because they prevent repeated work.

Use [`../templates/items/standard/H-NN-slug.md`](../templates/items/standard/H-NN-slug.md) as the
skeleton; keep the local wording of the folder you are working in.

## D-NN — decision

Record a decision when it changes scope, ranking, method, or future work. Include date, choice,
rationale, and a revision trigger. When the trigger fires, add a superseding decision; do not edit
the old row into its opposite.

## Q-NN — question

Include the question, why it matters, what it blocks, and who or what closes it. Do not answer an
open question from memory. When answered, keep the answer and source discoverable so it is not
asked again.

## INV-NN — invariant

Keep invariants in `Context/00-START-HERE.md`. Each says what must remain true and why a violation
invalidates the result. Add on evidence; remove only by decision.

## P-NN — experimental/scaffolding change

Use only when the subject is temporarily modified for observation. Record it before applying it,
including purpose, exact diff/revision, and `reverted: yes/no`. An unrecorded or unreverted probe
makes following observations unattributable.

## File versus registry row

Start with a registry row only when the claim is genuinely self-contained. Create a file when it
needs evidence, another artifact links to it, or it exceeds roughly ten lines. Split heavy tables,
stacks, diffs, and rejected alternatives into `<entity>_context.md`; the main file holds the claim,
evidence summary, consequences, and limits.
