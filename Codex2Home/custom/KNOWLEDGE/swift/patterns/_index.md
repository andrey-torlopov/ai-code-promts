# Swift/iOS Patterns Index

Canonical pattern guidance lives in `$CODEX_HOME/custom/KNOWLEDGE/swift/patterns/`.
This directory is a lazy-loaded knowledge pack, not an active skill.

> Each file contains a Bad Example (how not to) and a Good Example (how to).
> Used both when generating new code and during code review.

> **Lazy Load Protocol:** Read the file ONLY when a violation is detected or when code is generated in the appropriate area.
> Preventative downloading of all files is PROHIBITED (Token Economy).

## Naming Convention

`{category}/{pattern-name}.md` - description of the pattern with Bad/Good Example.

## Available Patterns

### common/ - Basic code hygiene

| File | Pattern |
|------|---------|
| `common/architecture.md` | Don't propose an architecture without asking, keep the existing one |
| `common/swift-conventions.md` | Swift API Design Guidelines, value types, modern concurrency, error handling |
| `common/naming-conventions.md` | UpperCamelCase/lowerCamelCase, `-able` protocols, boolean prefixes |
| `common/code-style.md` | No em dash, no obvious comments, no unrequested MARK/docstrings/`#if DEBUG` |
| `common/assertion-without-message.md` | XCTAssert without message |
| `common/hardcoded-test-data.md` | Hardcoded data in tests |
| `common/no-abstraction-layer.md` | Direct URLSession calls in tests |
| `common/static-test-data.md` | Static test data without randomization |
| `common/no-order-dependent-tests.md` | Tests depend on each other |
| `common/no-cleanup-pattern.md` | No cleanup after tests |

### networking/ - HTTP and URLSession specifics

| File | Pattern |
|------|---------|
| `networking/dictionary-instead-of-model.md` | `[String: Any]` ​​instead of Codable |
| `networking/missing-content-type-validation.md` | Content-Type is not validated |
| `networking/configure-urlsession.md` | URLSession not configured (default timeouts) |
| `networking/wrap-infrastructure-errors.md` | URLError is indistinguishable from a business error |
| `networking/inline-urlsession-calls.md` | URLSession.shared inline in code |
| `networking/missing-security-headers.md` | No security headers check |
| `networking/missing-error-body-check.md` | Testing HTTP Code Only Without Business Error |

### platform/ - Swift Concurrency + XCTest

| File | Pattern |
|------|---------|
| `platform/async-test-pitfalls.md` | `Task {}` ​​in sync tests, legacy XCTestExpectation for async |
| `platform/xctest-setup-crashes.md` | Force unwrap / try! in property init XCTestCase |
| `platform/flaky-sleep-tests.md` | `Thread.sleep()` ​​/ `Task.sleep()` instead of polling |
| `platform/no-hardcoded-timeouts.md` | Magic numbers in timeouts |
| `platform/no-shared-mutable-state.md` | Shared mutable state, no actor/Sendable |
| `platform/controlled-retries.md` | Uncontrolled retry logic |

### performance/ - Performance (source: T-Bank perf research)

| File | Pattern |
|------|---------|
| `performance/naive-disk-space-check.md` | Memoization of disk space with TTL instead of repeated calls |
| `performance/nsdictionary-file-attributes.md` | URL `resourceValues(forKeys:)` ​​instead of `attributesOfItem(atPath:)` |
| `performance/naive-directory-traversal.md` | `enumerator(at:includingPropertiesForKeys:)` ​​instead of piece bypass |
| `performance/string-ops-in-hot-path.md` | `[UInt8]`/`Data` instead of String in the hot path |
| `performance/string-search-in-collection.md` | `Set`/`Dictionary` instead of searching for a substring in a large string |
| `performance/nsstring-swift-bridging.md` | Do not alternate NSString/String in tight loop |
| `performance/protocol-cast-over-class-cast.md` | Cast to class instead of cast to protocol in hot way |
| `performance/string-describing-reflection.md` | `_typeName`/`ObjectIdentifier` instead of `String(describing:)` |
| `performance/expensive-generic-constants.md` | Closures instead of generic constants in mass registrations |
| `performance/multiple-protocol-conformance.md` | One protocol instead of many small ones for UI components |

### security/ - Data and security

| File | Pattern |
|------|---------|
| `security/no-sensitive-data-logging.md` | PII in logs, print(), os_log |
| `security/information-leakage-in-errors.md` | Data leak via error.localizedDescription |
| `security/pii-in-code.md` | PII in Tests, Previews and Mock Data |

### best-practices/ - General Swift recommendations

| File | Pattern |
|------|---------|
| `best-practices/prefer-final-class.md` | Mark classes `final` ​​if inheritance is not planned |
| `best-practices/prefer-let-over-var.md` | `let` ​​by default, `var` only if mutation is necessary |
| `best-practices/prefer-value-types.md` | `struct` ​​> `class`, default value semantics |

## QA mapping (Kotlin) -> Swift

| QA (Kotlin/JUnit) | Swift/iOS | Changes |
|---|---|---|
| `HttpClient` / Ktor | `URLSession` ​​/ `URLRequest` | The API is completely different |
| `@Test` / JUnit 5 | `func test*()`/XCTest | Lifecycle: `setUp()`/`tearDown()` instead of `@BeforeEach`/`@AfterEach` |
| `runBlocking {}` | `async throws` ​​test methods | Native support in Xcode 13+ |
| `Awaitility` | `XCTestExpectation` ​​/ custom polling | There is no direct analogue, you need a helper |
| `@Serializable` (Kotlin) | `Codable` ​​(Swift) | `CodingKeys` instead of `@SerialName` |
| `companion object` | `static` ​​properties | `actor` for thread-safe state |
| `lateinit var` | `var ... : T!` ​​in XCTestCase | Dangerous during init crash |
| Allure steps | `XCTContext.runActivity` | Less developed, but similar |
| `@BeforeAll` | `override class func setUp()` ​​| Called once per class |

## Usage (for developer)

When you find a problem or write new code:
1. Define a category: common / networking / platform / performance / security / best-practices
2. Read only the matching `$CODEX_HOME/custom/KNOWLEDGE/swift/patterns/<category>/` file after a signal appears.
3. If reference is not found - BLOCKER, do not guess fix

## Usage (for code review)

```bash
# Scan by category
ls $CODEX_HOME/custom/KNOWLEDGE/swift/patterns/

# Grep in the project
grep -rn "URLSession.shared\|[String: Any]\|Thread.sleep\|attributesOfItem" --include="*.swift" Sources/ Tests/

# Read the file on match
sed -n '1,220p' $CODEX_HOME/custom/KNOWLEDGE/swift/patterns/performance/_summary.md
```
