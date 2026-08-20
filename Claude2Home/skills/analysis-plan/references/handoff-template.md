# Handoff

Use this compact state block when a task moves between roles.

```text
task:
scope:
constraints:
decisions:
rejected-options:
artifacts:
done-criteria:
status:
next-role:
```

## Rules

- Preserve previous role notes; append new facts instead of replacing context.
- Separate confirmed facts from assumptions.
- Record why important options were rejected.
- Keep the block short enough to fit in every role handoff.
- If `done-criteria` is missing for non-trivial work, route back to the planner.
