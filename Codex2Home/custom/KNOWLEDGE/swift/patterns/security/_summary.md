# Security Patterns

- Do not log PII, tokens, cookies, credentials, private keys or sensitive payloads.
- Do not include real PII in tests, previews or mock data.
- Avoid surfacing `localizedDescription` from infrastructure errors directly to users.
- Redact secrets in reports and logs.
- If a secret is found, report path and remediation, not the secret value.
