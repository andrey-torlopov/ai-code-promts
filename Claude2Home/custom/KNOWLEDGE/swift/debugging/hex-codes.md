# Crash Hex Codes

Lookup tables for hex constants in Apple crash reports, device logs, register dumps and file
headers. Classification happens in `crash-triage.md`; reproduction tools are in
`memory-diagnostics.md`. This file only answers "what does this number mean".

## Field Discipline

A hex value means something only inside the field it appears in. Same digits in another field
means another cause.

| Report field | What the hex is | Table to use |
|---|---|---|
| `Termination Reason: Namespace <NS>, Code 0x...` | Why the OS killed the process | System Termination Codes |
| `Exception Codes` or `Exception Subtype: KERN_INVALID_ADDRESS at 0x...` | Faulting memory address | Memory Sentinels |
| Register dump (`x0`..`x28`, `pc`, `lr`, `sp`) | A value or pointer in flight | Memory Sentinels |
| First bytes of a file (`xxd`, `otool -h`) | File format magic | File And Mach-O Magics |
| Third-party or cross-platform SDK log | Poison from a non-Apple runtime | Foreign Poison Values |

Non-negotiable rules:

1. A termination code names who killed the process and why. It is never the root cause by
   itself. The root cause is in the backtrace of the blocked or faulting thread.
2. Some fields print the code in decimal. Convert before lookup:
   `printf '0x%x\n' 2343432205` gives `0x8badf00d`.
3. If a code is not in these tables, report it as unknown and name the missing evidence.
   Do not invent a meaning.
4. Never read a termination code as an address, or an address as a termination code.
5. Quote the provenance tier when the code is not in current Apple documentation.

## System Termination Codes

Appear with `Exception Type: EXC_CRASH (SIGKILL)` and a `Termination Reason` namespace such as
`SPRINGBOARD`, `FRONTBOARD`, `RUNNINGBOARD`, `ASSERTIOND`, `JETSAM`.

| Hex | Decimal | Reads as | Meaning | Localize by |
|---|---|---|---|---|
| `0x8badf00d` | 2343432205 | ate bad food | Watchdog. A lifecycle transition (launch, resume, suspend, scene connect or update) did not finish inside its allowance because the main thread was blocked | Thread 0 backtrace at kill time: sync network, `Data(contentsOf:)`, `DispatchSemaphore.wait`, `performAndWait`, keychain or disk I/O, lock contention in `application(_:didFinishLaunchingWithOptions:)` or `scene(_:willConnectTo:)`. The allowance and the transition are printed in `Termination Description` |
| `0xc00010ff` | 3221229823 | cool off | Thermal event. The system shed the app under thermal pressure | Sustained CPU, GPU, location or radio work, polling loops, unthrottled sync. Instrument `ProcessInfo.processInfo.thermalState` |
| `0xdead10cc` | 3735883980 | dead lock | The process was suspended while still holding a system resource: a file lock or SQLite lock on a shared volume or App Group container, or an address-book style shared resource. Usually namespace `RUNNINGBOARD` | Core Data or SQLite store in the App Group container, `NSFileCoordinator` scopes, work continuing past the `beginBackgroundTask` expiration handler, an extension writing the same store |
| `0xbaadca11` | 3131951633 | bad call | A PushKit VoIP push was delivered but the app did not report an incoming call to CallKit inside the allowed window (a few seconds) | `pushRegistry(_:didReceiveIncomingPushWith:for:completion:)` must reach `CXProvider.reportNewIncomingCall(with:update:)` on every push, before returning, including all error and early-return paths |
| `0xbad22222` | 3134333474 | bad too repeatedly | A VoIP app was resumed in the background too frequently | PushKit push rate, keepalive interval, server-side retry loop |
| `0xbaddd15c` | 3135099228 | bad disc | Killed over disk or shared-resource access, typically to let the system reclaim space | Unbounded caches, log files, downloaded assets never evicted, in the app and in its extensions |
| `0xc51bad01` | 3306925313 | none | Background task exceeded its CPU budget (watchOS background task family) | CPU profile of the background task body; move work off the watch |
| `0xc51bad02` | 3306925314 | none | Background task exceeded its allowed wall-clock time | Shorten the session, split the work, honor the expiration handler |
| `0xc51bad03` | 3306925315 | none | Background task ran out of time without completing | Same as above, plus verify the completion call is always reached |
| `0xdeadfa11` | 3735943697 | dead fall | User force-quit the app, usually from the app switcher. Namespace `SPRINGBOARD` | Often not a defect, but not proof of innocence: check for a preceding hang report, users force-quit apps that look frozen |
| `0xbaaaaaad` | 3131746989 | none | Not a crash. The file is a whole-system stackshot, frequently created accidentally by the user | Stop analyzing it as a crash and locate the real report |
| `0xdeadfeed` | 3735944941 | dead feed | A service the process depends on timed out while spawning | Mostly system-side. Look for the service or XPC name near the entry |
| `0x2bad45ec` | 732775916 | too bad sec | Claimed security-policy violation. Folklore only | Treat as unverified: absent from current Apple documentation. Do not report it as a known cause |

Provenance tiers, quote them when relevant:

- Current Apple documentation: `0x8badf00d`, `0xc00010ff`, `0xdead10cc`, `0xbaadca11`,
  `0xbad22222`, `0xbaddd15c`, `0xc51bad01`, `0xc51bad02`, `0xc51bad03`.
- Archived TN2151 and Apple Developer Forums: `0xdeadfa11`, `0xbaaaaaad`.
- Community and third-party lists only: `0xdeadfeed`, `0x2bad45ec`.

## Termination Namespaces With Non-Hexspeak Codes

| Namespace and code | Meaning | Localize by |
|---|---|---|
| `JETSAM` | Memory-pressure kill | Footprint versus limit, and the jetsam reason (`per-process-limit`, `highwater`, `vm-pageshortage`). App extensions have far smaller limits than the host app |
| `DYLD, Code 0x1` | Library missing. A dependent dylib or framework was not found at launch | `@rpath` and `LC_RPATH`, Embed and Sign, framework absent from the `.ipa`, SPM binary target, dynamic versus static product |
| `DYLD, Code 0x4` | Symbol missing. The library loaded but a symbol is absent | SDK versus deployment-target mismatch, missing weak linking or `if #available`, stale build products, ABI change in a dependency |
| `CODESIGNING` | Signature or page-hash validation failed | Re-signing step, bundle mutated after signing, corrupted transfer |
| `OBJC` | The Objective-C runtime aborted the process | Read `Application Specific Information`; the real message is there, not in the code |
| `SIGNAL, Code 0x5` | SIGTRAP, on arm64 almost always a Swift runtime trap | See the Swift trap section of `crash-triage.md` |
| `SIGNAL, Code 0x4` | SIGILL, the same trap on x86_64 and in Simulator | Same as above |

Namespace names also appear as numbers (`domain:10`). The numeric map is in `crash-triage.md`.

## Memory Sentinels

Apply to fault addresses (`EXC_BAD_ACCESS`, `SIGSEGV`, `SIGBUS`) and to register values.

| Value or pattern | Meaning | Localize by |
|---|---|---|
| `0x0` | nil dereference | Force unwrap, `unsafelyUnwrapped`, a C API returning NULL, an ObjC `nil` where a value was required |
| `0x8`, `0x10`, `0x18`, any address under `0x1000` | nil object plus a member offset. The offset identifies the accessed field | Same as `0x0`; use the offset to name the property or ivar |
| `0xaa` repeated (`0xaaaaaaaaaaaaaaaa`) | Read of memory that was allocated but never initialized (`SCRIBBLE_BYTE`) | Uninitialized struct or C buffer, missing `memset`, partially decoded model, `UnsafeMutablePointer.allocate` without `initialize` |
| `0x55` repeated (`0x5555555555555555`) | Use-after-free: freed memory poisoned on `free()` (`SCRABBLE_BYTE`) | `unowned`, ObjC `assign` properties, manual `free`, C buffers outliving their Swift owner |
| `0xdd` repeated | Page was released with `madvise(MADV_FREE)` and then read (`SCRUBBLE_BYTE`) | A pointer kept across a large deallocation, or a cache that hands out memory it already returned |
| Garbage in the high bits with plausible low bits, for example `0x0020000105394398` where the real address is `0x0000000105394398` | Pointer authentication failure on arm64e. The subtype stays `KERN_INVALID_ADDRESS` and the report adds `(possible pointer authentication failure)` | Corrupted vtable or function pointer, `unsafeBitCast` of a signed pointer, mismatched virtual method signature, C interop passing signed pointers across boundaries. Not "just nil" |
| High bit set on arm64 (`0xb000000000000012`), or an odd address on x86_64 | Tagged pointer holding a small `NSNumber`, `NSString` or `NSDate`. Not corruption | Inspect the object and its use, not the allocator. Mask or `ptrauth_strip` before decoding |
| `0xbbadbeef` | WebKit's deliberate crash (`WTFCrash` / `CRASH()`), usually on WebThread or in JavaScriptCore | Treat as a WebKit assert, not heap corruption. Check WKWebView lifetime versus its delegates, JS bridge threading, message handlers retained after teardown |
| ASCII-looking value: every byte in `0x20`..`0x7e`. `0x41414141` decodes to `AAAA`, `0x6f6c6c6548` decodes to `olleH`, which is `Hello` stored little-endian | A string or buffer was written over a pointer, or text is being used as a pointer | Decode the address bytes as ASCII in both byte orders. Suspect a bad cast, an over-long copy, type confusion at a C boundary |
| `0xffffffffffffffff` or `-1` | A failed API return value used as a pointer or handle | Unchecked return from a POSIX or C call |
| `0xdeadbeefdeadbeef` in a kernel panic string | XNU zone corruption, for example `a freed zone element has been modified: expected 0xdeadbeefdeadbeef` | Kernel or driver scope, not app scope. Do not attribute to app code without kext evidence |

With `NSZombieEnabled` the log reports `message sent to deallocated instance 0x...`, which
names the class of the dead object. That is the fastest route from a `0x55...` fault to a type.

## Foreign Poison Values

Relevant when the app embeds cross-platform C or C++ (shared Android code, Chromium, Unity, a
Windows-ported library). Seeing one means the poison came from that runtime, so do not
attribute it to Apple's libmalloc.

| Value | Origin | Meaning |
|---|---|---|
| `0xdeadbeef` | Generic, embedded and C libraries | Uninitialized or freed marker |
| `0xbaadf00d` | Windows `LocalAlloc` debug heap | Uninitialized heap memory |
| `0xbaddcafe` | libumem | Uninitialized memory |
| `0xdead2bad` | Sequent DYNIX/ptx | Uninitialized memory |
| `0xdeadc0de` | OpenWrt jffs2 | Erased or marker block |
| `0xdeadbaad` | Android libc `abort_message` | Native heap corruption detected |
| `0xdeadd00d` | Android Dalvik or ART | VM abort |
| `0xcdcdcdcd`, `0xdddddddd`, `0xfdfdfdfd` | MSVC debug CRT | Uninitialized heap, freed block, guard fence |
| `0xaa` repeated in a Zig binary | Zig `undefined` fill in Debug or ReleaseSafe | See `~/.claude/custom/KNOWLEDGE/zig/debugging.md` |

## File And Mach-O Magics

Use when a binary, framework, asset or download is suspected of being the wrong artifact.

| Magic | Kind | Note |
|---|---|---|
| `0xfeedfacf` | `MH_MAGIC_64` | 64-bit Mach-O, all current Apple targets |
| `0xfeedface` | `MH_MAGIC` | 32-bit Mach-O |
| `0xcefaedfe`, `0xcffaedfe` | `MH_CIGAM`, `MH_CIGAM_64` | Byte-swapped. The header is being read with the wrong endianness |
| `0xcafebabe` | `FAT_MAGIC` | Universal (fat) binary. Also the Java class-file magic: if `file` reports Java for a framework binary, the artifact is wrong |
| `0xcafebabf` | `FAT_MAGIC_64` | 64-bit fat header |
| `0xbebafeca` | `FAT_CIGAM` | Byte-swapped fat header |
| `0x3c21444f`, `0x3c3f786d` | `"<!DO"`, `"<?xm"` | HTML or XML. A "corrupted binary" that is really an error page saved under a binary name |
| `0x7b22`, `0x7b0a`, `0x5b7b` | JSON text (`{"`, `{` plus newline, `[{`) | A JSON body, often an API error payload, where a binary was expected |
| `0x504b0304` | zip | `.ipa`, `.xcarchive`, `.jar` container, not a Mach-O |
| `0x1f8b` | gzip | Double-compressed or undecoded response |
| `0x62706c69` | `"bpli"` | Binary plist (`bplist00`). Read with `plutil`, not as text |

## Decode Commands

```bash
printf '0x%x\n' 2343432205                              # decimal termination code to hex
grep -iE 'Exception Type|Exception Codes|Termination|Triggered by' crash.ips
grep -oiE '0x[0-9a-f]{8,16}' crash.ips | sort | uniq -c | sort -rn | head -20
plutil -p crash.ips                                     # ips reports are JSON
xxd -l 16 suspect.bin                                   # file magic
otool -h /path/to/binary                                # Mach-O magic and cputype
```

## Reporting Format

Report a decoded value as evidence, never as a conclusion:

```text
CODE: 0x8badf00d (Termination Reason: Namespace FRONTBOARD, decimal 2343432205)
MEANS: watchdog kill during <named transition>, allowance <value from the report>
EVIDENCE: <artifact:line>; thread 0 blocked in <symbol>
ROOT CAUSE CANDIDATE: <specific call on the blocked thread>
NEXT CHECK: <command, instrument or scheme diagnostic>
PROVENANCE: <Apple docs | TN2151 | community>
UNKNOWNS: <codes or fields that could not be attributed>
```

## Anti-Patterns

- Reporting the hexspeak code as the root cause instead of as the kill reason.
- Analyzing `0xbaaaaaad` as a crash.
- Quoting `0x2bad45ec` or another community-only code as documented behavior.
- Guessing the meaning of a code that is not in these tables.
- Calling `0xbbadbeef`, a tagged pointer or a PAC fault "heap corruption".
- Reading a PAC fault as a nil dereference because the low bits look plausible.
- Assuming `0x8badf00d` always means slow launch. The namespace and transition matter.
- Attributing a foreign poison value to Apple's allocator.

## Sources

- Apple: Understanding the exception types in a crash report, Examining the fields in a crash
  report, Identifying the cause of common crashes, Addressing watchdog terminations,
  Addressing crashes from Swift runtime errors, `EXC_GUARD`, Technical Q&A QA1592,
  Technical Note TN2151 (archived), Malloc Debug Environment Variables release notes,
  `man malloc(3)`.
- Sources: `apple-oss-distributions/libmalloc` (`src/base.h`), XNU `bsd/sys/reason.h`,
  `swiftlang/swift` (`stdlib/public/runtime/Errors.cpp`), `<mach-o/loader.h>`,
  `<mach-o/fat.h>`.
- Hexspeak constant list: `https://en.wikipedia.org/wiki/Hexspeak`.
