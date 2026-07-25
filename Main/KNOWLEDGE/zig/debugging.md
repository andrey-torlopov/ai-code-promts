# Zig Debugging

Panic messages, poison bytes and allocator diagnostics for Zig. Read on a panic, a crash, a
suspected use-after-free, or a leak report.

> **Version gate:** the API names below track Zig 0.14 through 0.16-dev. Run `zig version`
> and check the installed `lib/std/` before quoting a symbol name. Zig renames aggressively;
> a name from another release is a wrong answer, not a small inaccuracy.

## Build Mode Decides What Is Observable

| Mode | Safety checks | `undefined` filled with `0xaa` | `unreachable` |
|---|---|---|---|
| `Debug` | on | yes | panics with `reached unreachable code` |
| `ReleaseSafe` | on | yes | panics with `reached unreachable code` |
| `ReleaseFast` | off | no | true undefined behavior, optimizer assumes the path is dead |
| `ReleaseSmall` | off | no | true undefined behavior |

Rules:

1. A crash that only happens in `ReleaseFast` is usually a safety check that was compiled out.
   Re-run in `ReleaseSafe` to convert it into a panic with a message and a stack trace.
2. `zig test` keeps safety checks even under `ReleaseFast`, so a green test suite in that mode
   proves nothing about the shipped binary.
3. Do not reason about `0xaa` in a release build. The fill is a Debug and ReleaseSafe
   implementation feature, not a language semantic, and it is not guaranteed to be observable.

## Poison Bytes

| Pattern | Where it comes from | Reading |
|---|---|---|
| `0xaa` in a scalar, `var x: T = undefined` read back as 170 | Zig fills `undefined` memory with `0xaa` in Debug and ReleaseSafe | Use of uninitialized memory |
| `0xaaaaaaaaaaaaaaaa` as a pointer | Same fill seen through an undefined pointer | Dereference of a never-assigned pointer, immediate fault |
| `0xaa` in memory that was valid earlier | `std.mem.Allocator.free` memsets the block to `undefined` | Use-after-free |

On Apple platforms an `0xaa` fault can come from either Zig or libmalloc's `SCRIBBLE_BYTE`.
Attribute it by the faulting image, not by the byte. Cross-reference
`KNOWLEDGE/swift/debugging/hex-codes.md`.

## Safety Panic Messages

The message is the lookup key. Match it verbatim: several strings differ from the intuitive
wording of the function that raises them.

| Message (verbatim) | Cause | Localize by |
|---|---|---|
| `reached unreachable code` | `unreachable` executed, including an unhandled `switch` case or a failed `catch unreachable` | The `unreachable` site; if it is `catch unreachable`, the real problem is the swallowed error |
| `attempt to use null value` | Unwrap of a null optional (`.?`) | The optional's producer, not the unwrap site |
| `cast causes pointer to be null` | `@ptrCast`/`@intCast` chain produced a null pointer | The integer or pointer being cast |
| `incorrect alignment` | Pointer cast to a stricter alignment than the address satisfies | `@alignCast`, packed structs, byte buffers reinterpreted as structs |
| `invalid error code` | Integer converted to an error outside the error set | `@errorFromInt` and the value's origin |
| `integer does not fit in destination type` | `@intCast` out of range | The source range versus destination type width |
| `integer overflow` | Arithmetic overflow with safety on | The operation; use wrapping (`+%`, `*%`) only if wrap is intended, a saturating operator if clamping is intended, or widen the type |
| `left shift overflowed bits` | `<<` discarded significant bits | Shift amount and operand width |
| `right shift overflowed bits` | `>>` discarded significant bits | Same |
| `division by zero` | Zero divisor | The divisor's origin, not the division |
| `exact division produced remainder` | `@divExact` with a remainder | Whether the invariant actually holds |
| `integer part of floating point value out of bounds` | `@intFromFloat` out of range | NaN, infinity, or an unvalidated float |
| `switch on corrupt value` | Switch on a value outside the type's valid set | Where the value was produced, usually a bad cast or uninitialized memory |
| `shift amount is greater than the type size` | Shift amount too large | The shift operand |
| `invalid enum value` | Integer converted to an enum with no matching tag | `@enumFromInt` and the wire or file format it came from |
| `for loop over objects with non-equal lengths` | Multi-object `for` with mismatched lengths | The two slices and where they diverged |
| `source and destination arguments have non-equal lengths` | `@memcpy` length mismatch | Both slice lengths |
| `@memcpy arguments alias` | Overlapping copy | Use `@memmove` or copy through a temporary |
| `'noreturn' function returned` | A `noreturn` function returned | The function's contract, often FFI |
| `sentinel mismatch: expected {any}, found {any}` | Sentinel-terminated pointer or slice lost its sentinel | C string interop, manual slicing of a `[:0]u8` |
| `attempt to unwrap error: {s}` | `catch unreachable`, `orelse unreachable` or `try` in a context that cannot fail | The named error, then its producer |
| `index out of bounds: index {d}, len {d}` | Slice or array bounds | The index computation; both numbers are printed, use them |
| `start index {d} is larger than end index {d}` | Reversed slice bounds | The range computation |
| `access of union field '{s}' while field '{s}' is active` | Wrong active tag on a union | The last write to the union |
| `slice length '{d}' does not divide exactly into destination elements` | `@ptrCast` between slices of different element sizes | Byte length versus element size |

## Panic Handler API Drift

| Toolchain | Interface |
|---|---|
| 0.13 and earlier | One root `pub fn panic(msg, error_return_trace, ret_addr)` plus the `std.builtin.panic.messages` struct with fields such as `reached_unreachable`, `unwrap_null` |
| 0.14 and later | `std.builtin.panic` is a namespace; the individual safety panics are camelCase functions on `std.debug.FullPanic` in `lib/std/debug.zig`. The `messages` struct was removed (ziglang/zig PR 22594). Default is `std.debug.FullPanic(std.debug.defaultPanic)`; minimal backends use `std.debug.simple_panic`. The legacy root `panic` function still works through a deprecated shim |

Customization point: declare `pub const panic` in the root source file to override the handler.
Never quote `std.builtin.panic.messages` for a 0.14+ toolchain.

## Allocator Diagnostics

`std.heap.DebugAllocator` was named `GeneralPurposeAllocator` before 0.14.0; the rename landed
in the 0.14.0 cycle (commit `cd99ab3`, PR 20511) and a deprecated alias was kept, slated for
removal after 0.15.0. If a code base still says `GeneralPurposeAllocator`, that is a version
signal, not necessarily an error.

| Capability | What it catches | How it shows up |
|---|---|---|
| Stack traces captured on alloc and free | Attribution of both sides of a lifetime bug | Three traces printed for a double free |
| Double-free detection | `free` of an already freed block | `log.err("Double free detected...")` then `@panic("Unrecoverable double free")` |
| Leak detection | Blocks alive at `deinit()` | `deinit()` returns `.leak`; in tests `std.testing.allocator` fails the test |
| Addresses are never reused | Use-after-free and dangling pointers | The stale pointer faults instead of silently hitting a new object |

There is no fixed canary constant in the allocator. Detection rests on non-reuse of addresses,
per-allocation metadata with stack traces, and the `0xaa` fill on free. Do not look for a
`0xdeadbeef`-style guard value.

Allocator choice changes what is observable:

- `DebugAllocator` in Debug and tests: full lifetime diagnostics.
- `ArenaAllocator`, `FixedBufferAllocator`: no use-after-free detection. If a bug disappears
  when switching to an arena, it is a lifetime bug that the arena is masking, not a fixed bug.
- `std.testing.allocator`: leak-checked, use it in every test that allocates.

## Reading A Panic

Output shape: `thread <id> panic: <message>` followed by a stack trace with file, line and
column per frame. Steps:

1. Copy the message verbatim and match it in the table above.
2. Read the deepest frame that belongs to project code, not to `std`.
3. Distinguish the two traces: an error return trace shows where an error was created and
   propagated through `try`; the stack trace shows where the process died. They answer
   different questions.
4. Stack traces need debug info. `ReleaseSmall` and stripped builds lose it, so a missing
   trace is a build-configuration fact, not a mystery.
5. `-fstack-check` adds stack-overflow detection when a deep recursion is suspected.

Under a debugger:

```bash
zig build -Doptimize=Debug
lldb ./zig-out/bin/<app>
```

```text
run
bt all                            # after the stop
image lookup -r -n panic          # resolve the actual panic symbol for this toolchain
frame variable
memory read -f x -c 8 <addr>      # look for 0xaa fills
```

Resolve the panic symbol from the binary instead of assuming its name: it differs across
toolchain versions.

## Anti-Patterns

- Quoting a stdlib API name without checking `zig version`.
- Diagnosing a `ReleaseFast` crash without reproducing it in `ReleaseSafe`.
- Reading `0xaa` as valid data, or as proof of a Zig bug on Apple platforms without checking
  the faulting image.
- Replacing an overflow panic with a wrapping operator to make the crash disappear.
- Using `catch unreachable` to move an error into a panic and then debugging the panic.
- Reporting "leak detected" without the allocator and the trace that produced it.
- Switching to an arena allocator to make a use-after-free go away.

## Sources

- `ziglang.org/documentation/master/` section on `undefined`; 0.14.0 release notes.
- `lib/std/builtin.zig`, `lib/std/debug.zig`, `lib/std/heap/debug_allocator.zig`,
  `lib/std/mem/Allocator.zig` of the installed toolchain.
- ziglang/zig PR 22594 (panic interface), PR 20511 and commit `cd99ab3` (allocator rename).
