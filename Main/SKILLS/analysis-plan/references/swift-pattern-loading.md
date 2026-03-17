# Local Pattern Loading

Use this reference only after seeing a concrete signal.

| Signal | Check |
|---|---|
| `URLSession.shared` inline | Infrastructure dependency hidden inside code; prefer injectable client/session |
| `[String: Any]` for API data | Prefer `Codable` model unless dynamic schema is required |
| `Thread.sleep` or arbitrary `Task.sleep` in tests | Prefer deterministic waiting |
| Force unwrap in XCTest property setup | Move fallible setup into `setUpWithError` or test method |
| `print` in production | Prefer project logger and avoid secrets |
| `error.localizedDescription` returned to user | Check information leakage |
| Repeated `String(describing:)` in hot path | Avoid reflection-style conversion in hot loops |
| `attributesOfItem` repeated for many paths | Prefer URL resource values when traversing directories |

Quote the local pattern signal in the finding only when it directly supports the issue.
