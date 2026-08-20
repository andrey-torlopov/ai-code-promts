# Interaction Guide

Use short clarification loops. Ask at most three questions at once.

Required discovery:

1. Purpose: what recurring task does the skill perform?
2. Trigger phrases: what will the user say?
3. Inputs: paths, files, domain details or artifacts.
4. Output: report, code, edits, validation result or generated files.
5. Anti-examples: tasks this skill must refuse or route away from.
6. Atomicity: which local references/scripts/assets are required inside the skill folder?

Confirmation checkpoint before writing:

```text
Skill:
Purpose:
Inputs:
Output:
Local files:
Not handled:
```

Do not save a broad or vague skill. A vague skill becomes an unreliable agent prompt.
