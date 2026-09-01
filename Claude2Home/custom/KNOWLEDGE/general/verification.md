# General Verification

For stacks without a dedicated pack:

1. Discover the project's own checks before inventing any: CI config, `Makefile`/`justfile`/task runners, manifest scripts, README.
2. Prefer the narrowest check that covers the change: one test file or target before a full suite.
3. Run configured formatters and linters first, then a build or type check, then focused tests.
4. Report each command verbatim with its observed result.
5. If verification is not run, report the exact blocker as residual risk instead of assuming success.
6. Launching a build, or a test command that triggers one, needs the CORE rule 9 grant:
   the user's explicit request or the project's `PROJECT.md` build policy. Without it,
   name the command and report it as not run.
