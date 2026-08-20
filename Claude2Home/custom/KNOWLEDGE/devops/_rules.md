# DevOps Rules

1. Separate diagnosis from deploy/release actions.
2. Treat CI templates, runners, secrets and environments as high blast radius.
3. Do not mutate external systems without explicit confirmation.
4. Verify current pipeline state before claiming latest status.
5. Do not print secret values.
6. Every deploy needs preflight, confirmation, rollback and verification.
