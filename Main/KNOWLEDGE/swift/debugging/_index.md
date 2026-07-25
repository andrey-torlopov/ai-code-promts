# Swift/iOS Debugging Knowledge

Lazy-loaded pack for crash and log diagnosis on Apple platforms.
This is a lookup pack, not an active skill and not a fix guide.

> **Lazy Load Protocol:** read a file only after a concrete signal appears in the artifact
> being analyzed. Preloading the pack is prohibited (Token Economy).

## Available Files

| File | Use when | Answers |
|---|---|---|
| `hex-codes.md` | a crash report, hang report, stackshot, device log, register dump or file header contains an unexplained hex constant | what killed the process, what a fault address pattern means, which artifact a magic number belongs to |

## Signals

Read `hex-codes.md` when any of these appear:

- `Termination Reason`, `Exception Type`, `Exception Codes`, `EXC_BAD_ACCESS`, `EXC_CRASH`,
  `EXC_BREAKPOINT`, `EXC_GUARD`, `EXC_RESOURCE`
- a bare hex constant of 8 or 16 digits in a log, register, or fault address
- watchdog, jetsam, thermal, force-quit, dyld launch failure, code-signing kill
- `.ips`, `.crash`, `.diag`, `.hang`, `sysdiagnose` artifacts
- "corrupted" binary, framework, asset or download

## Protocol

1. Identify the field the constant came from before looking it up.
2. Read only `hex-codes.md`, then quote the matched row in the diagnosis.
3. Treat a decoded code as evidence about the killer, never as the root cause.
4. If a constant is not listed, report it as unknown with the missing evidence named.
