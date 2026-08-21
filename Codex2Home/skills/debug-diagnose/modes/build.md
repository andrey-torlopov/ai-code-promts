# Mode: build

Use for compiler, linker, package and local build failures.

## Knowledge

Load by project:

- Swift/SPM/Xcode: `$CODEX_HOME/custom/KNOWLEDGE/swift/verification.md`
- Zig (`build.zig`, `build.zig.zon`): `$CODEX_HOME/custom/KNOWLEDGE/zig/verification.md` and `$CODEX_HOME/custom/KNOWLEDGE/zig/_rules.md`; record `zig version` before quoting stdlib API names
- Shell/toolchain symptoms: `$CODEX_HOME/custom/KNOWLEDGE/shell/_rules.md`

## References

- `../references/log-analysis.md`
- `../references/build-diagnosis.md`
- `../references/root-cause-format.md`

## Stop

Return root cause and fix plan. Do not implement until the user confirms or the same request explicitly asks for implementation after diagnosis.
