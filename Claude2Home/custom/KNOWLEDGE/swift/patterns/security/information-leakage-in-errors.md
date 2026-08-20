# Information Leakage in Error Responses

**Applies to:** Networking layer, Error handling, Logging

## Why this is bad

Leakage of internal information via error handling:
- Stack traces in the logs reveal the structure of the code and libraries
- Internal paths expose the file system (`/Users/developer/...`)
- Debug info reveals SQL queries, table names, connection strings
- `localizedDescription` may contain internal details
- Crash logs with sensitive data go to Crashlytics/Sentry

## Bad Example

```swift
// ❌ BAD: The complete error goes to the UI
func handleError(_ error: Error) {
    showAlert(message: error.localizedDescription)
    // "The operation couldn't be completed. (NSURLError -1001: request timed out, URL: https://internal-api.company.com/v2/users)"
}

// ❌ BAD: Stack trace in logs without filtering
func logError(_ error: Error) {
    logger.error("Request failed: \(String(describing: error))")
    // Logs the full NSError with userInfo, including URLs, headers, etc.
}

// ❌ BAD: Debug description gets into production logs
func handleAPIError(_ response: HTTPURLResponse, data: Data) {
    let body = String(data: data, encoding: .utf8) ?? ""
    logger.error("API error \(response.statusCode): \(body)")
    // Body may contain: stack trace, SQL query, internal paths
}
```

## Good Example

```swift
// ✅ GOOD: Generic message for the user
func handleError(_ error: Error) {
    switch error {
    case APIError.noConnection:
        showAlert(message: "No internet connection")
    case APIError.timeout:
        showAlert(message: "The server is not responding. Please try later")
    case let APIError.serverError(statusCode, _) where statusCode >= 500:
        showAlert(message: "Server error. We are already working on a solution")
    default:
        showAlert(message: "An error has occurred. Please try later")
    }
}

// ✅ GOOD: Logging without sensitive data
func logError(_ error: Error, context: String) {
    switch error {
    case let APIError.serverError(statusCode, body):
        logger.error("[\(context)] Server error: \(statusCode), code: \(body?.code ?? "unknown")")
        // We do not log body.message, body.details - may contain PII
    case let urlError as URLError:
        logger.error("[\(context)] Network error: \(urlError.code.rawValue)")
        // Don't log URLs, headers
    default:
        logger.error("[\(context)] Error type: \(type(of: error))")
    }
}

// ✅ GOOD: Test checks for leaks
func testErrorResponseDoesNotLeakInternals() async throws {
    let response = try await apiClient.sendCorruptedRequest()
    let body = response.rawBody

    XCTAssertFalse(body.contains("Exception"), "Error should not contain Exception")
    XCTAssertFalse(body.contains("/Users/"), "Error should not contain file paths")
    XCTAssertFalse(body.contains(".swift:"), "Error should not contain source references")
    XCTAssertFalse(body.contains("SELECT"), "Error should not contain SQL")
}
```

## What to look for in code review

- `error.localizedDescription` is displayed directly to the user
- `String(describing: error)` or `\(error)` ​​in production logs
- Error body is logged entirely without filtering fields
- No mapping internal errors -> user-facing messages
- `debugDescription` in production code
- URL with query parameters in logs (may contain tokens)
