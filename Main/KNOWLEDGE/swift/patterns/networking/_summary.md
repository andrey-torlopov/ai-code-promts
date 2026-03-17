# Networking Patterns

- Prefer `Codable` request and response models over `[String: Any]`.
- Validate status code and business error body when the API has business error envelopes.
- Validate expected `Content-Type` when parsing response bodies.
- Avoid inline `URLSession.shared` in domain code; inject a session or client boundary.
- Configure timeouts and cache policy intentionally.
- Wrap infrastructure errors so callers can distinguish transport failure from domain failure.
- Check security headers when the product relies on them.
