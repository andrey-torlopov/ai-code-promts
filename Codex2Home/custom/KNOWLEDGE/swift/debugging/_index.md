# Swift/iOS Debugging Knowledge

Lazy-loaded pack for crash, hang and memory diagnosis on Apple platforms.
Lookup and methodology only; it does not authorize code changes.

> **Lazy Load Protocol:** read a file only after a concrete signal appears in the artifact
> being analyzed. Preloading the whole pack is prohibited (Token Economy).

## Available Files

| File | Read when | Answers |
|---|---|---|
| `crash-triage.md` | any crash, hang, spin or stackshot artifact is opened | which exception class this is, which field to read next, what the exception subtype and `pc` versus fault address mean, which namespace killed the process |
| `hex-codes.md` | a constant needs a meaning: termination code, fault address pattern, register value, file magic | what the number means in the field it came from, and how trustworthy that meaning is |
| `memory-diagnostics.md` | the class is a memory bug, or backtraces differ every run | which sanitizer or malloc switch to enable, how to read ASan shadow bytes, how to symbolicate |

## Signals

| Signal in the artifact | Load |
|---|---|
| `Exception Type`, `EXC_BAD_ACCESS`, `EXC_BREAKPOINT`, `EXC_CRASH`, `EXC_RESOURCE`, `EXC_GUARD` | `crash-triage.md` |
| `Termination Reason`, watchdog, jetsam, thermal, force-quit, dyld or code-signing kill | `crash-triage.md`, then `hex-codes.md` |
| `Fatal error:`, `Simultaneous accesses`, textless trap, exit code 132 | `crash-triage.md` |
| A bare 8 or 16 digit hex constant anywhere | `hex-codes.md` |
| `0x55...`, `0xaa...`, `0xdd...`, `objc_msgSend` crash, backtraces that differ every run | `hex-codes.md`, then `memory-diagnostics.md` |
| ASan or TSan report, shadow bytes, `leaks`, `malloc_history` | `memory-diagnostics.md` |
| "corrupted" binary, framework, asset or download | `hex-codes.md` |

Non-Apple stacks: Zig panics and `0xaa` fills are in `$CODEX_HOME/custom/KNOWLEDGE/zig/debugging.md`.

## Protocol

1. Classify with `crash-triage.md` before decoding anything.
2. Identify the field a constant came from, then read only the matching table.
3. Quote the matched row and its provenance tier in the diagnosis.
4. Treat a decoded code as evidence about the killer, never as the root cause.
5. If a constant is not listed, report it as unknown and name the missing evidence.
