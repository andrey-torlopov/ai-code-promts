# Anti-Pattern: PII in code and test data

**Applies to:** Tests, Previews, Mock data

## Problem

Personal data (real or "realistic") in code:
- Code ends up in Git - PII leaks when publishing repository
- SwiftUI Previews with real data visible in screenshots
- Violation of GDPR / 152-FZ when auditing the code base
- “Vasya’s test account” is still PII

## Bad Example

```swift
// ❌ BAD: real domains and formats
enum TestData {
    static func validRequest() -> RegisterRequest {
        RegisterRequest(
            email: "ivan.petrov@gmail.com", // real domain
            phone: "+79161234567", // real format
            fullName: "Petrov Ivan Sergeevich" // looks like a real person
        )
    }
}

let testEmail = "vasya.dev@company.com" // PII colleagues
let testPhone = "+79031112233" // someone's number

// ❌ BAD: PII in SwiftUI Preview
struct ProfileView_Previews: PreviewProvider {
    static var previews: some View {
        ProfileView(user: User(
            name: "Maria Ivanova",
            email: "m.ivanova@gmail.com",
            phone: "+79161234567"
        ))
    }
}
```

## Good Example

```swift
// ✅ GOOD: RFC 2606 + clearly invalid formats
enum TestData {
    static func validRequest() -> RegisterRequest {
        let suffix = Int(Date().timeIntervalSince1970)
        return RegisterRequest(
            email: "auto_\(suffix)@example.com",   // RFC 2606
            phone: "+70000000000", // clearly test (zeros)
            fullName: "Test User \(UUID().uuidString.prefix(4))"
        )
    }
}

// ✅ GOOD: Safe Preview data
struct ProfileView_Previews: PreviewProvider {
    static var previews: some View {
        ProfileView(user: User(
            name: "Test User",
            email: "preview@example.com",
            phone: "+70000000000"
        ))
    }
}

// ✅ GOOD: Mock namespace for preview/test data
extension User {
    enum Mock {
        static let standard = User(
            name: "Test User",
            email: "test@example.com",
            phone: "+70000000000"
        )

        static let empty = User(name: "", email: "", phone: "")
    }
}
```

## Safe Patterns

| Type | Safe | Prohibited |
|-----|-----------|-----------|
| Email | `@example.com`, `@example.org` (RFC 2606) | `@gmail.com`, `@yandex.ru`, `@company.com` |
| Phone | `+70000000000`, `+79999999999` | `+7916...`, `+7903...` |
| Name | `Test User`, `QA Bot`, `Auto Test 123` | Full name in the format "Last Name First Name Patronymic" |
| Card | links to test cards from payment system docs | any 16-digit numbers without reference |
| Address | `123 Test Street, City 00000` | real addresses |

## Detection

```bash
grep -rn "@gmail\.com\|@yandex\.ru\|@mail\.ru" --include="*.swift" Sources/ Tests/
grep -rn "+7916\|+7903\|+7925\|+7926" --include="*.swift" Sources/ Tests/
```

## References

- (ref: security/pii-in-code.md)
- RFC 2606: Reserved Example Domains
