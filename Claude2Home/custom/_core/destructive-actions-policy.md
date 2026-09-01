# Destructive Actions Policy

Before destructive work, show this exact information and wait for explicit confirmation:

```text
Operation:
Paths:
Expected effect:
Dry-run available:
Rollback:
Confirmation needed:
```

Destructive work includes:

- file or directory deletion;
- recursive cleanup;
- mass rename or mass move;
- `sudo`;
- install or uninstall;
- permission or ownership changes;
- shell profile, launch agent or system setting changes;
- irreversible cache cleanup.

If a dry run is possible, run or propose the dry run first.

Exception (CORE rule 5): when the user explicitly requested that exact destructive action,
the request itself is the confirmation — show the block for the record and proceed.
