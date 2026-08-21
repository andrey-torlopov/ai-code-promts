# Performance Patterns

- Avoid repeated filesystem attribute calls in large traversals; batch or use URL resource values.
- Avoid naive directory traversal that does extra path work.
- Prefer `Set` or `Dictionary` for frequent membership checks.
- Avoid repeated string conversions and reflection in hot paths.
- Avoid alternating `NSString` and `String` in tight loops.
- Avoid many small protocol conformances when a single cohesive abstraction is cheaper.
- Cache expensive generic constants or replace with closures where static generic storage is costly.
