# Anti-Pattern: Check only HTTP code without business error

## Problem

Error handling only checks the HTTP status (`400`, `422`), without checking `body.code` / `body.errorType`.
The code considers the request to be unsuccessful, but the real reason (invalid business error code) is not detected.

## Bad Example

```swift
// ❌ BAD: check only HTTP status
func register(_ request: RegisterRequest) async throws -> RegisterResponse {
    let (data, response) = try await session.data(for: buildRequest(request))
    guard let httpResponse = response as? HTTPURLResponse else {
        throw APIError.invalidResponse
    }

    guard httpResponse.statusCode == 201 else {
        throw APIError.serverError(statusCode: httpResponse.statusCode)
        // Business code is not verified - any non-201 is treated the same
    }

    return try decoder.decode(RegisterResponse.self, from: data)
}
```

## Good Example

```swift
// ✅ GOOD: checking HTTP status + business error code
func register(_ request: RegisterRequest) async throws -> RegisterResponse {
    let (data, response) = try await session.data(for: buildRequest(request))
    guard let httpResponse = response as? HTTPURLResponse else {
        throw APIError.invalidResponse
    }

    guard httpResponse.statusCode == 201 else {
        let errorBody = try? decoder.decode(ErrorResponse.self, from: data)
        throw APIError.businessError(
            statusCode: httpResponse.statusCode,
            code: errorBody?.code ?? "UNKNOWN",
            field: errorBody?.field,
            message: errorBody?.message ?? "No error details"
        )
    }

    return try decoder.decode(RegisterResponse.self, from: data)
}

// Calling code can differentiate between error types
do {
    let response = try await apiClient.register(request)
} catch let APIError.businessError(statusCode, code, field, message) where code == "VALIDATION_ERROR" {
    showFieldError(field: field, message: message)
} catch let APIError.businessError(statusCode, code, _, _) where code == "DUPLICATE_EMAIL" {
    showDuplicateEmailAlert()
} catch {
    showGenericError()
}
```

## Why

- HTTP `400` can arrive for many reasons (auth, schema, rate limit)
- Without `body.code` it is impossible to distinguish `VALIDATION_ERROR` ​​from `MISSING_FIELD` or `RATE_LIMITED`
- UI cannot show the correct message to the user
- Regression in business logic errors goes unnoticed

## Detection

```bash
grep -rn "statusCode ==" --include="*.swift" Sources/ | grep -v "body\.\|errorBody\.\|errorResponse"
```
