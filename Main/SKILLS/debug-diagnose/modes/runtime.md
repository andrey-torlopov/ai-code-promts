# Mode: runtime

Use for crashes, runtime errors, logs and incorrect behavior after startup.

## Knowledge

Load language and platform packs only after identifying the affected stack.

Apple platforms (iOS, macOS, watchOS, tvOS), in this order:

1. `../../../KNOWLEDGE/swift/debugging/crash-triage.md` before reading any backtrace or
   decoding any constant. `Exception Type` decides the branch.
2. `../../../KNOWLEDGE/swift/debugging/hex-codes.md` for a `Termination Reason` code, a fault
   address pattern, a register value or a file magic.
3. `../../../KNOWLEDGE/swift/debugging/memory-diagnostics.md` when the class is a memory bug,
   or when backtraces differ across otherwise identical crashes.
4. `../../../KNOWLEDGE/swift/_rules.md` only when the fix scope reaches Swift code style.

Zig: `../../../KNOWLEDGE/zig/debugging.md` for a `thread <id> panic:` message, a `0xaa` fill,
an allocator double-free or leak report. Confirm `zig version` first; API names are
version-bound. Build and command choices come from `../../../KNOWLEDGE/zig/verification.md`.

## References

- `../references/log-analysis.md`
- `../references/root-cause-format.md`

## Gates

- State symbolication status before quoting a backtrace.
- Reproduce in the configuration that produced the report, or say it was not reproduced.
- For Zig, never diagnose from `ReleaseFast` or `ReleaseSmall`; re-run in `ReleaseSafe`.

## Stop

Return reproduction notes, root cause and fix plan. Do not edit code unless the user explicitly requests the implementation handoff.
