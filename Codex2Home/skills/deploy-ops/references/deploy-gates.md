# Deploy Gates

Release gate and rollback contract in one file; both are mandatory before any mutation.

## Release Gate

Before any deploy/release/publish/rollout mutation, show:

```text
Operation:
Environment:
Version/ref:
Preflight status:
Expected effect:
Rollback:
Verification:
Confirmation needed:
```

Proceed only after explicit confirmation.

## Rollback

Every deploy plan must state:

1. Last known good version or ref.
2. Rollback command or manual path.
3. Data migration reversibility.
4. Expected time to restore.
5. Verification after rollback.

If rollback is unknown, treat that as a release risk and ask before proceeding.
