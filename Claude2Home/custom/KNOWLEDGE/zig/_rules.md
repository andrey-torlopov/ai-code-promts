# Zig Rules

1. Establish the toolchain version with `zig version` before quoting any stdlib API; names
   move between releases and a plausible-looking name from another version is a wrong answer.
2. Read `build.zig` and `build.zig.zon` before choosing any command; do not assume `zig build`
   targets, steps or option names.
3. Never diagnose a crash from a `ReleaseFast` or `ReleaseSmall` build. Reproduce in `Debug`
   or `ReleaseSafe` first, because safety checks and the `0xaa` fill exist only there.
4. Treat `undefined` as poison, not as zero. Reading it is illegal behavior even when the
   observed byte pattern looks stable.
5. Pass allocators explicitly. In tests use `std.testing.allocator` so leaks fail the test.
6. Pair every acquisition with `defer` or `errdefer` at the point of acquisition.
7. Use wrapping (`+%`, `-%`, `*%`) or saturating (`+|`, `-|`, `*|`) operators only where wrap
   or clamp is the intended semantics, never to silence an overflow panic.
8. Quote panic messages verbatim. The exact string is the lookup key into
   `debugging.md`.
9. Do not add C interop, `@cImport` or a new dependency without an explicit request.
10. Verification is a named command with its output, not an assumption that it compiles.
