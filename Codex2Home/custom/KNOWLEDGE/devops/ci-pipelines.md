# CI Pipelines

Inspect:

1. Trigger conditions and target branch or tag.
2. Reusable workflow/template inputs.
3. Runner image and tags.
4. Cache keys.
5. Dependency install steps.
6. Required checks and protected environments.
7. Secrets and permissions, without printing secret values.
8. Artifact provenance.

When a failure appears, identify the first meaningful failing step.
Do not modify pipeline state outside an explicit gate.
