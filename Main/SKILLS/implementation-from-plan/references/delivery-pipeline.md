# Delivery Pipeline

Use this sequence:

```text
inspect -> implement -> verify -> self-review -> report
```

Rules:

- Implement only the approved plan or direct request.
- Preserve unrelated user changes.
- Keep diffs minimal.
- Avoid broad refactors that are not needed for the task.
- If acceptance criteria are missing for non-trivial delivery, stop and ask for them.
- Optional tests are not automatic; explain why tests are or are not needed.
