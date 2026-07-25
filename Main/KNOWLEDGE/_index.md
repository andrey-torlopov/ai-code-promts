# Knowledge Index

Load knowledge only when the selected skill or scope needs it.

| Signal | Load knowledge |
|---|---|
| Xcode build-time optimization, slow clean build, slow incremental build, `.build-benchmark/` | `swift`, `ios` |
| `.swift`, `Package.swift`, `Package.resolved` | `swift` |
| crash report, hang report, stackshot, `.ips`/`.crash`/`.diag`, `Exception Type`, `EXC_*`, `Fatal error:`, watchdog, jetsam, thermal kill, dyld launch failure | `swift/debugging/crash-triage.md`, then only the file it names |
| unexplained hex constant in a log, fault address, register or file header | `swift/debugging/hex-codes.md` |
| ASan/TSan report, shadow bytes, `0x55`/`0xaa`/`0xdd` fault address, `objc_msgSend` crash, leaks, backtraces that differ every run | `swift/debugging/memory-diagnostics.md` |
| `.zig`, `build.zig`, `build.zig.zon`, `zig build`, `thread <id> panic:`, Zig safety panic message | `zig` |
| `.xcodeproj`, `.xcworkspace`, Tuist, iOS app modules | `swift`, `ios` |
| `.gitlab-ci.yml`, `.github/workflows`, CI logs, runners | `devops` |
| deploy, release, publish, rollout | `devops`, project-specific deploy docs |
| `.sh`, `.zshrc`, `mise`, `brew`, shell errors | `shell` |
| `.py`, `pyproject.toml`, `requirements.txt` | `python` |
| Markdown docs, specs, plans | selected skill references first; add docs pack only if created later |

Always show loaded and skipped packs in `SKILL CONTEXT`.
