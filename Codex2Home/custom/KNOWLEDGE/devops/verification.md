# DevOps Verification

Use direct evidence and the narrowest reliable checks:

1. CI job result or deployment status.
2. Commit, tag, version or artifact digest — for deploys, visible in the target environment.
3. Smoke test, health check or status endpoint.
4. Logs for the changed service, job or surface.
5. Rollback readiness.

Report any checks that could not be performed, with the exact blocker.
