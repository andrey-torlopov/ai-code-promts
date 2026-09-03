# Zig Verification

Prefer focused verification and name the command in the report.

1. `zig version` first. Record it: every other answer depends on it.
2. `zig build --summary all` when `build.zig` exists; read declared steps instead of guessing.
3. `zig build test --summary all`, or `zig test src/<file>.zig` for a single file.
4. `zig build -Doptimize=Debug` and `-Doptimize=ReleaseSafe` for any crash or memory
   investigation; `ReleaseFast` and `ReleaseSmall` only for performance claims.
5. `zig fmt --check .` for formatting, never `zig fmt` on files outside the task scope.
6. `zig build --verbose` or `-freference-trace` when a compile error points into generic or
   comptime code and the chain of instantiations is unclear.
7. `zig env` when the failure looks like a toolchain, cache or target problem.
8. If verification is not run, report the exact blocker instead of implying success.
9. Launching `zig build`, `zig build test` or `zig test` is gated by CORE rule 9: it needs
   the user's explicit request or a `PROJECT.md` build policy. `zig version`, `zig env` and
   `zig fmt --check` are not builds and stay free.

Notes:

- The build cache hides source-of-truth problems. When results look impossible, re-run with a
  clean cache path rather than reasoning about stale artifacts.
- `zig test` keeps safety checks enabled even under `ReleaseFast`, so a test pass in that mode
  is not evidence that a release binary is safe.
- Cross-compilation targets change which safety and libc behavior applies; state the target
  when it is not the host.
