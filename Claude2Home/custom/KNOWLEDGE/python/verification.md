# Python Verification

Prefer focused checks:

1. `pytest` for test suites when configured.
2. Project-defined lint/type commands when present.
3. Direct script execution only when inputs and side effects are clear.
4. If dependencies are missing, report the missing package and installation boundary.
