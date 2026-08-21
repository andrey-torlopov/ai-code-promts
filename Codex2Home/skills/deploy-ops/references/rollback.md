# Rollback

Every deploy plan must state:

1. Last known good version or ref.
2. Rollback command or manual path.
3. Data migration reversibility.
4. Expected time to restore.
5. Verification after rollback.

If rollback is unknown, treat that as a release risk and ask before proceeding.
