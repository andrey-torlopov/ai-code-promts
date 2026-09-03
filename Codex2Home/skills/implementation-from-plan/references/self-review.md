# Review and Audit Checklist

Before final response, check the changed scope for (Swift-specific items apply only to
Swift code):

- Correctness against acceptance criteria.
- Potential crashes.
- Retain cycles.
- Data races and actor isolation issues.
- Error handling.
- Sensitive data logging.
- Public API or module boundary changes.
- Test gap or verification gap.
- Unrelated refactors.

Final output:

```text
Changed Files:
Implementation Notes:
Verification:
Residual Risk:
```
