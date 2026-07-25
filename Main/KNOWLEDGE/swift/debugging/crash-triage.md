# Apple Crash Triage

Classify before decoding. This file decides which field of the report to read next and
which of the sibling files answers it. Read it first for any crash, hang or spin artifact.

## Triage Order

1. Read `Exception Type`. It decides everything downstream.
2. Branch with the routing table below.
3. Decode any constant with `hex-codes.md`, using the field it came from.
4. Confirm symbolication before quoting a backtrace.
5. If the class is a memory bug, pick a reproduction tool from `memory-diagnostics.md`.
6. State root cause only when a specific frame, call or lifecycle transition is named.

## Exception Type Routing

| Exception Type | Signal | Most likely class | Read next |
|---|---|---|---|
| `EXC_BREAKPOINT` | `SIGTRAP` | Swift runtime trap on arm64 (`brk #0x1`) | `Application Specific Information`, then the first app frame |
| `EXC_BAD_INSTRUCTION` | `SIGILL` | The same trap on x86_64, Simulator, Mac Catalyst, Intel Mac (`ud2`, `EXC_I386_INVOP` in LLDB) | same as above |
| `EXC_BAD_ACCESS` | `SIGSEGV` or `SIGBUS` | Memory bug | `Exception Subtype` plus the fault address, then `hex-codes.md` |
| `EXC_CRASH` | `SIGABRT` | `abort()` after an unhandled ObjC or C++ exception | `Last Exception Backtrace` and `Application Specific Information` |
| `EXC_CRASH` | `SIGKILL` | The OS killed the process | `Termination Reason`, then `hex-codes.md` |
| `EXC_RESOURCE` | `SIGKILL` or non-fatal | Resource limit exceeded | `Exception Subtype` (`CPU`, `WAKEUPS`, `MEMORY`, `IO`, `PORT_SPACE`) and the message with limit versus observed |
| `EXC_GUARD` | `SIGKILL` | Guarded resource violated | `Exception Subtype` (`GUARD_TYPE_FD`, `GUARD_TYPE_MACH_PORT`) |

Architecture rule: one logical bug surfaces as `EXC_BREAKPOINT` on Apple Silicon and as
`EXC_BAD_INSTRUCTION` on Intel. Never report them as two different defects, and never
explain differing `Exception Codes` by "different trap kinds" when the architecture differs.

## EXC_BAD_ACCESS Subtypes

The subtype is a `kern_return_t`.

| Subtype | Meaning | Typical cause |
|---|---|---|
| `KERN_INVALID_ADDRESS` | Access to unmapped memory | nil, dangling or garbage pointer. On arm64e the report may add `(possible pointer authentication failure)` |
| `KERN_PROTECTION_FAILURE` | Memory is mapped but protected | Write to a read-only page, write into a string literal or constant, execute data |
| `KERN_MEMORY_ERROR` | Data is unavailable | A memory-mapped file became unreachable: unmounted volume, network share, truncated file |
| `EXC_ARM_DA_ALIGN` | Unaligned data access | Rare on arm64. Misaligned atomic or an over-aligned type expectation |

## pc Versus Fault Address

| Comparison | Reading | Where to look |
|---|---|---|
| `pc` (arm64) or `rip` (x86_64) differs from the fault address | Invalid memory fetch. The code is valid, the data pointer is bad | The object being dereferenced at the crash line |
| `pc` equals the fault address | Invalid instruction fetch. The jump target itself is bad | Corrupted function pointer, block, vtable or a virtual call on a freed object. On arm64 `lr` holds the return address and identifies the caller. On x86_64 the return address is on the stack and is harder to attribute |

## Swift Runtime Traps

Mechanism: the stdlib terminates either through `_assertionFailure` (with a message) or
through `Builtin.int_trap()` / `Builtin.condfail` (without one). arm64 emits `brk #0x1`,
x86_64 emits `ud2`. The text is delivered to the log by `swift_reportError` writing into the
CrashReporter annotations (`__crash_info`), which is why it lands in
`Application Specific Information` and never in the backtrace.

Field fingerprints:

- arm64: `esr: 0xf2000001 (Breakpoint) brk 1`, often `Termination Reason: Namespace SIGNAL, Code 0x5` (SIGTRAP is signal 5).
- x86_64: `Code 0x4` (SIGILL is signal 4).

| Message in Application Specific Information | Bug class | Localize by |
|---|---|---|
| `Fatal error: Unexpectedly found nil while unwrapping an Optional value` | Force unwrap of nil | The `!`, `try!` or IBOutlet on the first app frame |
| `Fatal error: Index out of range` | Array or slice bounds | Index computation, off-by-one, concurrent mutation of the collection |
| `Fatal error: Unexpectedly found nil while implicitly unwrapping an Optional value` | Implicitly unwrapped optional (`T!`) not set | Storyboard or XCTest property initialization order |
| `Fatal access conflict detected` or `Simultaneous accesses to ..., but modification requires exclusive access` | Exclusivity violation (SE-0176), enforced in Release since Swift 5 | `inout` aliasing, a mutating method reentering the same value, a struct captured by two closures |
| A trap with no message, process exits with 132 | `precondition` in `-O`: the text is compiled out | Reproduce in Debug to recover the message before diagnosing further |
| Arithmetic trap with no message | Integer overflow. Swift traps by default | The arithmetic expression. Wrapping operators (`&+`, `&*`) are correct only when wrap is intended |
| `Fatal error: Unexpectedly found nil` from `as!` or `try!` | Bad force cast or force try | The cast source type and the thrown error |

Build-mode rule: `assert` and `assertionFailure` are removed in Release. `precondition`,
`preconditionFailure` and `fatalError` keep trapping but may lose their text. A textless trap
means "Release build", not "no reason available".

## Stack-Top Fingerprints

| Top frames or log line | Reading |
|---|---|
| `objc_msgSend`, `objc_retain`, `objc_release`, or `unrecognized selector sent to instance` | Use-after-free on an ObjC object. Enable Zombie Objects to get the dead class name |
| `swift_retain`, `swift_release`, `swift_getObjectType` with a garbage address | Freed Swift object, usually behind `unowned` or an unsafe pointer |
| `WTFCrash`, `WTFCrashWithInfo`, `WebKit::` or `JavaScriptCore` frames | Deliberate WebKit assert. See `0xbbadbeef` in `hex-codes.md`, do not call it heap corruption |
| `gpus_ReturnNotPermittedKillClient` | GPU work (Metal or OpenGL ES) submitted while the app was backgrounded |
| `_dispatch_assert_queue_fail` | A queue-asserted API called from the wrong queue |
| Thread 0 parked in `__CFRunLoopServiceMachPort`, `semaphore_wait_trap` or `__psynch_mutexwait` on a SIGKILL | Main thread was blocked. Cross-check the watchdog codes |
| `_dyld_start` or `dyld4::` frames | Launch-time link failure. Read the `DYLD` termination namespace |

## os_reason Namespaces

Reports print `Namespace <name>` and RunningBoard contexts print `domain:<number>`. The
namespace and code are packed into one 64-bit Mach exception code, which is why large
decimals appear (`RUNNINGBOARD 3735883980` is `0xdead10cc`). Numbers come from XNU
`bsd/sys/reason.h` and may grow in newer OS releases.

| ID | Namespace | ID | Namespace |
|---|---|---|---|
| 0 | `INVALID` | 12 | `REPORTCRASH` |
| 1 | `JETSAM` | 13 | `COREANIMATION` |
| 2 | `SIGNAL` | 14 | `AGGREGATED` |
| 3 | `CODESIGNING` | 15 | `RUNNINGBOARD` (also `ASSERTIOND`) |
| 4 | `HANGTRACER` | 16 | `SKYWALK` |
| 5 | `TEST` | 17 | `SETTINGS` |
| 6 | `DYLD` | 18 | `LIBSYSTEM` |
| 7 | `LIBXPC` | 19 | `FOUNDATION` |
| 8 | `OBJC` | 20 | `WATCHDOG` |
| 9 | `EXEC` | 21 | `METAL` |
| 10 | `SPRINGBOARD` | 22 | `WATCHKIT` |
| 11 | `TCC` | 23 | `GUARD` |

## Watchdog Thresholds

The exact allowance is printed in `Termination Description`, for example:

```text
Termination Reason: FRONTBOARD 2343432205
<RBSTerminateContext| domain:10 code:0x8BADF00D explanation:process-launch watchdog
transgression: application<...>:23483 exhausted real (wall clock) time allowance
of 20.00 seconds>
```

Order of magnitude only: process-launch and foreground transitions allow about 20 seconds of
wall-clock time, background and checkin events allow more, up to about 60 seconds. Always
quote the number from the report, never the typical value.

## ips Reports

A modern `.ips` file is a JSON header line followed by a JSON body. Fields worth reading:
`exception` (`type`, `signal`, `subtype`), `termination` (`namespace`, `code`, `indicator`,
`details`), `asi` (Application Specific Information), `faultingThread`, `threads`,
`usedImages`. Example: `"termination":{"namespace":"WATCHDOG","code":1,"indicator":"monitoring timed out for service"}`.
Parse with `plutil -p` or `jq` instead of grepping the whole file.

## MetricKit As A Source

`MXCrashDiagnostic` exposes `exceptionType`, `exceptionCode`, `signal`, `terminationReason`
and `virtualMemoryRegionInfo`; `callStackTree` is only available through its JSON
representation. MetricKit itself exists since iOS 13, but crash diagnostics were added in
iOS 14. Payloads are aggregated out of process and delivered about once a day at next
launch, so absence of a payload is not evidence of no crash.

## Escalation Rule

Many `EXC_BAD_ACCESS` crashes with *different* backtraces mean memory corruption: the cause
is not in any single backtrace. Stop reading individual stacks and switch to
`memory-diagnostics.md`.

## Anti-Patterns

- Quoting a backtrace without stating whether it is symbolicated.
- Splitting one bug into two because arm64 and x86_64 report different exception types.
- Diagnosing a `SIGKILL` crash without reading `Termination Reason`.
- Treating an `EXC_RESOURCE` non-fatal note as a crash.
- Concluding "random crash" or "iOS bug" instead of escalating to sanitizers.
- Using the typical watchdog threshold instead of the one printed in the report.
- Reading a Release-mode textless trap as an unknown cause.
