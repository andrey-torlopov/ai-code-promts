# Crash Hex Codes

Decode hex constants found in Apple crash reports, device logs, register dumps and hex
dumps into a localized cause. This is a lookup pack for diagnosis, not a fix guide.

## When To Load

Load on a concrete signal:

- an `.ips`, `.crash`, `.diag`, `.hang` or `sysdiagnose` artifact is being analyzed
- a log contains `Termination Reason`, `Exception Type`, `Exception Codes`, `EXC_*`
- an unexplained hex constant appears in a fault address, register, or file header
- symptom is "app killed by the system", watchdog, jetsam, thermal, dyld launch failure

Do not load for compile or link errors without a crash artifact.

## Field Discipline

Read this before any lookup. A hex value means something only inside the field it appears
in. Same digits in a different field means a different cause.

| Report field | What the hex is | Table to use |
|---|---|---|
| `Termination Reason: Namespace <NS>, Code 0x...` | why the OS killed the process | System Termination Codes |
| `Exception Codes` or `Exception Subtype: KERN_INVALID_ADDRESS at 0x...` | faulting memory address | Memory Sentinels |
| register dump (`x0`..`x28`, `pc`, `lr`, `sp`) | a value or pointer in flight | Memory Sentinels |
| first bytes of a file (`xxd`, `otool -h`) | file format magic | File And Mach-O Magics |
| third-party or cross-platform SDK log | poison from a non-Apple runtime | Foreign Poison Values |

Non-negotiable rules:

1. A termination code names who killed the process and why. It is never the root cause by
   itself. The root cause is in the backtrace of the blocked or faulting thread.
2. Some fields print the code in decimal. Convert before lookup:
   `printf '0x%x\n' 2343432205` gives `0x8badf00d`.
3. If a code is not in these tables, report it as unknown and say what evidence is missing.
   Do not invent a meaning.
4. Never mix a termination code with a fault address. They live in different namespaces.

## System Termination Codes

Appear with `Exception Type: EXC_CRASH (SIGKILL)` and a `Termination Reason` namespace such
as `SPRINGBOARD`, `FRONTBOARD`, `RUNNINGBOARD`, `ASSERTIOND`, `JETSAM`.

| Hex | Decimal | Reads as | Meaning | Localize by |
|---|---|---|---|---|
| `0x8badf00d` | 2343432205 | ate bad food | Watchdog. A lifecycle transition (launch, resume, suspend, scene connect or update) did not finish inside its budget because the main thread was blocked | Thread 0 backtrace at kill time: sync network, `Data(contentsOf:)`, `DispatchSemaphore.wait`, `performAndWait`, disk or keychain I/O, lock contention in `application(_:didFinishLaunchingWithOptions:)` or `scene(_:willConnectTo:)`. The namespace names the transition |
| `0xdeadfa11` | 3735943697 | dead fall | User force-quit the app from the app switcher | Usually not a defect. Check for a preceding hang report: users force-quit apps that look frozen |
| `0xbaaaaaad` | 3131746989 | baaaaaad | Not a crash. The file is a whole-system stackshot, often triggered accidentally by the user | Stop analyzing it as a crash and locate the real report |
| `0xdead10cc` | 3735883980 | dead lock | The process was suspended while still holding a file lock or an SQLite lock on a file in a shared container (App Group) | Core Data or SQLite store inside the App Group container, `NSFileCoordinator` scopes, work continuing past the `beginBackgroundTask` expiration handler, an extension writing the same store |
| `0xc00010ff` | 3221229823 | cool off | Thermal event. The system shed the app under thermal pressure | Sustained CPU, GPU, location or radio work, polling loops, unthrottled background sync. Instrument `ProcessInfo.processInfo.thermalState` |
| `0xbad22222` | 3134333474 | bad too repeatedly | A VoIP app was resumed in the background too frequently | PushKit push rate, keepalive interval, server-side retry loop |
| `0xbaadca11` | 3131951633 | bad call | A PushKit VoIP push was delivered but the app did not report an incoming call to CallKit in the allowed window (a few seconds) | `pushRegistry(_:didReceiveIncomingPushWith:for:completion:)` must reach `CXProvider.reportNewIncomingCall(with:update:)` on every push, before returning, including all error and early-return paths |
| `0xbaddd15c` | 3135099228 | bad disc | Killed so the system could reclaim disk space | Unbounded caches, log files, downloaded assets never evicted, in the app and in extensions |
| `0xdeadfeed` | 3735944941 | dead feed | A service the process depends on timed out while spawning | Mostly system-side. Look for the service or XPC name near the entry |
| `0xc51bad01` | 3306925313 | (watchOS family) | watchOS background or extended-runtime task exceeded its budget | Shorten the session, honor the expiration handler, move work off the watch |
| `0xc51bad02` | 3306925314 | (watchOS family) | Same family, different budget variant (time versus CPU) | Same as above; treat the family as one signal unless Apple docs for the OS version differentiate |
| `0xc51bad03` | 3306925315 | (watchOS family) | Same family, repeated or aggregate violation | Same as above |

## Termination Contexts Without A Hexspeak Code

| Namespace or type | Meaning | Localize by |
|---|---|---|
| `JETSAM` | Memory-pressure kill | Footprint versus limit, jetsam reason (`per-process-limit`, `highwater`, `vm-pageshortage`). App extensions have far smaller limits than the host app |
| `DYLD, Code 0x1` | Library missing. A dependent dylib or framework was not found at launch | `@rpath` and `LC_RPATH`, Embed and Sign setting, framework absent from the `.ipa`, SPM binary target, dynamic versus static product |
| `DYLD, Code 0x4` | Symbol missing. The library loaded but a symbol is absent | SDK versus deployment-target mismatch, missing weak linking or `if #available`, stale build products, ABI change in a dependency |
| `CODESIGNING` | Signature or page-hash validation failed | Re-signing step, mutated bundle contents after signing, corrupted transfer |
| `OBJC` | The Objective-C runtime aborted the process | Read `Application Specific Information`; the real message is there, not in the code |
| `EXC_RESOURCE` (`CPU`, `MEMORY`, `WAKEUPS`, `IO`) | A resource limit was exceeded. Often non-fatal, still a real defect | The subtype line carries the limit and the observed value |
| `EXC_GUARD` | A guarded resource was violated (file descriptor, vnode, mach port) | Double-close, closing a guarded fd, writing to a guarded file |
| `EXC_BREAKPOINT (SIGTRAP)` on arm64, `EXC_BAD_INSTRUCTION (SIGILL)` in Simulator | A Swift runtime trap: force unwrap of nil, index out of range, `fatalError`, precondition, arithmetic overflow, bad `as!` cast | The message is in `Application Specific Information`. No hex lookup applies |

## Memory Sentinels

Apply to fault addresses (`EXC_BAD_ACCESS`, `SIGSEGV`, `SIGBUS`) and to register values.

| Value or pattern | Meaning | Localize by |
|---|---|---|
| `0x0` | nil dereference | Force unwrap, `unsafelyUnwrapped`, a C API returning NULL, an ObjC `nil` where a value was required |
| `0x8`, `0x10`, `0x18`, any address under `0x1000` | nil object plus a member offset. The offset tells which field was accessed | Same as `0x0`; use the offset to identify the property or ivar |
| `0x55` repeated (`0x5555555555555555`) | Freed memory. `MallocScribble` fills deallocated bytes with `0x55`, so this is use-after-free | Enable Malloc Scribble and Zombie Objects in the scheme. Suspect `unowned`, ObjC `assign` properties, manual `free`, C buffers outliving their Swift owner |
| `0xaa` repeated (`0xaaaaaaaaaaaaaaaa`) | Allocated but never initialized. `MallocScribble` fills fresh allocations with `0xaa` | Uninitialized struct or C buffer, missing `memset`, partially decoded model, `UnsafeMutablePointer.allocate` without `initialize` |
| `0xbbadbeef` | WebKit's deliberate crash (`WTFCrash` / `CRASH()`), usually on WebThread or in JavaScriptCore | Treat as a WebKit assertion, not heap corruption. Check WKWebView lifetime versus its delegates, JS bridge threading, main-thread rules, message handlers retained after teardown |
| ASCII-looking value: every byte in `0x20`..`0x7e`. `0x41414141` decodes to `AAAA`, `0x6f6c6c6548` decodes to `olleH`, which is `Hello` stored little-endian | A string or buffer was written over a pointer, or text is being used as a pointer | Decode the address bytes as ASCII in both byte orders. Suspect a bad cast, an over-long copy, type confusion at a C boundary |
| `0xffffffffffffffff` or `-1` | A failed API return value used as a pointer or handle | Unchecked return from a POSIX or C call |
| arm64 high bit set (`0xb000000000000012`), or an odd address on x86_64 | Tagged pointer holding a small `NSNumber`, `NSString`, `NSDate`. Not corruption | Inspect the object and its use, not the allocator |
| Plausible low bits with garbage high bits on arm64e | Pointer authentication failure. A signed pointer was corrupted or signed with the wrong key or context | Corrupted function pointer or vtable, `unsafeBitCast` of a signed pointer, C interop passing signed pointers across boundaries |

Related runtime aid, not a hex value: with `NSZombieEnabled` the log reports
`message sent to deallocated instance 0x...`, which names the class of the dead object.

## Foreign Poison Values

Relevant when the app embeds cross-platform C or C++ (shared Android code, Chromium, Unity,
a Windows-ported library). Seeing one of these means the poison came from that runtime, so
do not attribute it to Apple's libmalloc.

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

## File And Mach-O Magics

Use when a binary, framework, asset or download is suspected of being the wrong artifact.

| Magic | Kind | Note |
|---|---|---|
| `0xfeedface` | `MH_MAGIC` | 32-bit Mach-O |
| `0xfeedfacf` | `MH_MAGIC_64` | 64-bit Mach-O, all current Apple targets |
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
xxd -l 16 suspect.bin                                   # file magic
otool -h /path/to/binary                                # Mach-O magic and cputype
plutil -p crash.ips                                     # newer .ips reports are JSON-lines
```

Scheme diagnostics that produce these sentinels on purpose:

```text
Malloc Scribble      -> 0xaa on allocation, 0x55 on deallocation
Zombie Objects       -> "message sent to deallocated instance"
Guard Malloc         -> fault on the first out-of-bounds access
Address Sanitizer    -> exact allocation and free stacks instead of a sentinel
Thread Sanitizer     -> data races behind "random" corrupted pointers
Main Thread Checker  -> UIKit called off the main thread
```

## Reporting Format

When a hex value is decoded, report it as evidence, not as a conclusion:

```text
CODE: 0x8badf00d (Termination Reason: Namespace FRONTBOARD)
MEANS: watchdog kill during <named transition>
EVIDENCE: <artifact:line>; thread 0 blocked in <symbol>
ROOT CAUSE CANDIDATE: <specific call on the blocked thread>
NEXT CHECK: <command, instrument or scheme diagnostic>
UNKNOWNS: <codes or fields that could not be attributed>
```

## Anti-Patterns

- Reporting the hexspeak code as the root cause instead of as the kill reason.
- Analyzing `0xbaaaaaad` as a crash.
- Reading a termination code as a memory address, or a fault address as a termination code.
- Guessing the meaning of a code that is not in these tables.
- Calling `0xbbadbeef` or a tagged pointer "heap corruption".
- Assuming `0x8badf00d` always means slow launch. The namespace and the transition matter.
- Drawing conclusions from an unsymbolicated backtrace without stating that symbolication
  is missing.
- Attributing a foreign poison value to Apple's allocator.

## Sources

- Hexspeak constant list: `https://en.wikipedia.org/wiki/Hexspeak`
- Apple: Identifying the cause of common crashes, Addressing watchdog terminations,
  `EXC_CRASH (SIGKILL)`, Examining the fields in a crash report
- `man malloc` on macOS for the `MallocScribble` `0xaa` and `0x55` patterns
- `<mach-o/loader.h>` and `<mach-o/fat.h>` for Mach-O magics
