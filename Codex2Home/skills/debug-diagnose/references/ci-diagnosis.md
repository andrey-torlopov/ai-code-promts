# CI Diagnosis

Check in this order:

1. Failing workflow, job and step.
2. Runner image and environment differences.
3. Cache restore/save behavior.
4. Dependency installation and lockfiles.
5. Secrets and permission boundaries without printing secret values.
6. Template or reusable workflow changes.

External CI mutations require an explicit gate.
