# Skill Context

Use this block before substantial work.

```text
SKILL: <skill> (mode=<mode-or-none>)
TASK: <TaskID -> absolute task-folder path, or none>
REASON: <why this skill owns the deliverable>
PROJECT: <project context file path or none>
KNOWLEDGE: <loaded packs or none>
SKIPPED: <relevant packs intentionally not loaded>
REFERENCES: <local references loaded or none>
RULES: <CORE rules and local gates>
ARTIFACT: <path or none>
STOP: <deliverable boundary; no hidden next phase>
```

Use this trace after substantial work.

```text
TRACE:
- Skill:
- Task folder:
- References read:
- Knowledge read:
- Patterns/policies applied:
- Verification:
- Residual risk:
```

## Validity

A substantial response is invalid if it omits:

1. selected skill;
2. mode, if applicable;
3. the project context file or explicit `none`;
4. the task folder or explicit `none`;
5. loaded `KNOWLEDGE` packs or explicit `none`;
6. stop gate;
7. deliverable boundary.
