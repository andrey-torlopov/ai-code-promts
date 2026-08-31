# Maintenance

## After every canonical step

```text
[ ] Step-XX.md preserves the user request, scope, actions, and completion criterion
[ ] Step-XX-result.md exists and starts with an honest verdict/status
[ ] result records evidence, changed artifacts, limits, and debts
[ ] durable claims are in Knowledge and registered
[ ] completed pair is the first data row in root steps.md; older steps descend below it
[ ] no speculative future Step file exists
[ ] README, index, steps.md, and restore assumptions agree
[ ] Results status matches actual payloads
[ ] every durable file changed in this turn is covered by the open step, not edited on the side
[ ] no durable Markdown link targets Inbox/
[ ] task-local scripts are in Context/tools/; raw output is in Logs/; scratch prose is in Notes/
[ ] no folder outside the canonical set appeared
[ ] exported claims carry the export mark and agree with the external base registry
[ ] base deletions happened only on an explicit user request and are listed in the step result
[ ] every file exported to the base passes the single-copy test (self-contained, distilled)
[ ] audit_task.py exits 0
[ ] restore_task.py reports no open step or the sole request actually in progress
```

## Re-rank after evidence

Re-rank the unnumbered queue after each verdict. A queue item is not a step and has no step number.
A demoted hypothesis stays discoverable; a refuted one records what failed. A debt carried through
three completed steps is a decision: do it or record why it remains deferred and what it blocks.

## Drift

Before quoting a line, number, pin, or status, verify its scope. Repair drift with a superseding
fact or later step. Do not edit a historical result into agreement with today.

## Inbox retirement

Inbox deletion is separate and user-authorized: audit must report no Inbox dependency, durable
claims must have non-Inbox evidence, Results must be self-contained, and removal/recoverability
must be recorded.

## Close the task

Close the final user request with a normal plan/result pair and an overall verdict against `F-01`.
Leave no unmatched plan, update all projections, record remaining questions/debts and owners, and
run audit/restore. Do not create a synthetic next-step or closed-state file.
