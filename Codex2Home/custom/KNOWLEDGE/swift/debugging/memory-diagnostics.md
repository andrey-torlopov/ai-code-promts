# Memory Diagnostics

How to reproduce and localize a memory bug once `crash-triage.md` classified it as one.
Sentinel values themselves are decoded in `hex-codes.md`.

## Allocator Poison Bytes

libmalloc hard-codes these. They are an implementation detail, not a public contract, and
they cannot be reconfigured.

| Byte | Source constant | Written when | Reading in a crash |
|---|---|---|---|
| `0xaa` | `SCRIBBLE_BYTE` | On allocation, under `MallocScribble` or `MallocPreScribble` | Read of memory that was never initialized |
| `0x55` | `SCRABBLE_BYTE` | On `free()`, under `MallocScribble` | Use-after-free or double free |
| `0xdd` | `SCRUBBLE_BYTE` | On `madvise(MADV_FREE)` | Page was returned to the system and then read |

A pointer-sized field full of one of these bytes (`0xaaaaaaaaaaaaaaaa`,
`0x5555555555555555`) is a poisoned pointer, not a valid address.

## Environment Switches

Set as environment variables in the Xcode scheme (Run, Arguments) or before a CLI run.

| Variable | Effect | Cost |
|---|---|---|
| `MallocScribble=1` | `0xaa` on allocation, `0x55` on free | Low. Enable by default while debugging |
| `MallocPreScribble=1` | Legacy switch for the allocation-side `0xaa` fill | Low |
| `MallocGuardEdges=1` | Guard pages around large blocks | Low |
| `MallocStackLogging=1` | Records allocation stacks for `leaks` and `malloc_history` | Memory and startup cost |
| `MallocStackLoggingNoCompact=1` | Keeps free records too, needed for use-after-free history | Higher |
| `MallocStackLoggingDirectory=<dir>` | Where logs are written | None |
| `NSZombieEnabled=1` | Freed ObjC objects become zombies and report the class on message send | Leaks every object, never ship |
| `DYLD_INSERT_LIBRARIES=/usr/lib/libgmalloc.dylib` | Guard Malloc: one page per block, faults on the first overflow or use-after-free | Very slow, small heaps only |

Xcode scheme equivalents, in the Diagnostics tab: Address Sanitizer, Thread Sanitizer,
Undefined Behavior Sanitizer, Malloc Scribble, Malloc Guard Edges, Guard Malloc,
Zombie Objects, Malloc Stack Logging, Main Thread Checker.

## Tool Selection

| Symptom | Tool | Why this one |
|---|---|---|
| Fault address of `0x55...` or `0xaa...`, or backtraces that differ every run | Address Sanitizer | Reports the allocation and the free stack, so the cause stops depending on the crash site |
| Crash inside `objc_msgSend`, `objc_release`, or `unrecognized selector` | Zombie Objects | Names the class of the dead object |
| Small overflow past a buffer, silent corruption of a neighbour field | Guard Malloc | Page-granular, faults on the first byte out of bounds instead of later |
| Corrupted-looking pointers only under load or only on device | Thread Sanitizer | The corruption is a data race, not an allocator bug |
| Misalignment, signed overflow, bad enum value in C or ObjC code | Undefined Behavior Sanitizer | Traps at the operation, not at the consequence |
| Growing footprint, `JETSAM` kills | Instruments Allocations plus Xcode Memory Graph | Finds retain cycles and unbounded caches |
| Leak without a crash | `leaks`, `malloc_history` | Needs `MallocStackLogging` to be useful |

Constraints: Address Sanitizer and Thread Sanitizer cannot be enabled together. Both change
timing, so an ASan build can hide a race and a TSan build can hide a use-after-free. Run them
in separate passes and say which pass produced the evidence.

## ASan Shadow Byte Legend

One shadow byte maps 8 application bytes. ASan prints the legend itself; this table is for
reading a pasted report where the legend was cut off.

| Shadow byte | Meaning |
|---|---|
| `0x00` | Addressable |
| `0x01`-`0x07` | Partially addressable |
| `0xfa` | Heap left redzone (heap buffer overflow) |
| `0xfd` | Freed heap region (use-after-free) |
| `0xf1` | Stack left redzone |
| `0xf2` | Stack mid redzone |
| `0xf3` | Stack right redzone |
| `0xf5` | Stack use after return |
| `0xf8` | Stack use after scope |
| `0xf9` | Global redzone |
| `0xf6` | Global init order |
| `0xf7` | Poisoned by user |
| `0xfc` | Container overflow |
| `0xac` | Array cookie |
| `0xbb` | Intra-object redzone |
| `0xfe` | ASan internal |
| `0xca` | Left alloca redzone |
| `0xcb` | Right alloca redzone |

## Symbolication And LLDB

Symbolication is a precondition, not a later step. A backtrace of hex addresses proves
nothing about root cause.

```bash
dwarfdump --uuid MyApp.app/MyApp                 # binary UUID per architecture
dwarfdump --uuid MyApp.app.dSYM                  # must match usedImages in the report
atos -o MyApp.app.dSYM/Contents/Resources/DWARF/MyApp -arch arm64 -l <loadAddress> <addr>
swift demangle '$s...'                           # decode a mangled Swift symbol
xcrun symbolicatecrash report.crash MyApp.app.dSYM
```

Inside LLDB after a stop:

```text
bt all                      # every thread, not only the faulting one
thread info                 # stop reason and the mach exception detail
frame variable              # locals at the faulting frame
register read pc lr sp x0    # compare pc with the fault address
image lookup --address 0x...  # which image and symbol owns an address
memory read -f x -c 8 0x...  # inspect the suspected object for 0xaa / 0x55 patterns
```

## Reproduction Discipline

1. Reproduce in the same build configuration as the report before changing anything.
2. If the symptom exists only in Release, suspect optimization-sensitive UB, a compiled-out
   `precondition` message, or a timing-dependent race, not a different bug.
3. If the symptom disappears under ASan or Guard Malloc, it is timing-dependent: keep the
   sanitizer pass as evidence collection, not as verification.
4. Verify a fix in the configuration that produced the crash, and say which one that was.

## Anti-Patterns

- Naming a root cause from an unsymbolicated stack.
- Enabling every diagnostic at once and reporting a mixture of unrelated findings.
- Shipping a build with `NSZombieEnabled` or Guard Malloc.
- Treating "does not crash under ASan" as proof the bug is fixed.
- Reading a poisoned pointer (`0xaa...`, `0x55...`, `0xdd...`) as a real address.
- Skipping the dSYM UUID check and blaming a wrong symbol on the compiler.
