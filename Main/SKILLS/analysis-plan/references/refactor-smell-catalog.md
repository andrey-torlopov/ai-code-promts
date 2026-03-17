# Swift Smell Catalog

## Structural

- Large file: more than 500 lines.
- Large type: more than 300 lines.
- Long method: more than 50 lines.
- Deep nesting: more than 4 levels.
- Massive ViewController or ViewModel.

## Design

- Business logic in View.
- UI rendering details in ViewModel.
- Fat model with persistence, networking or UI logic.
- Hard dependency where an existing protocol boundary is expected.
- Cyclic dependencies between modules or types.

## Swift-Specific

- Completion handlers where async/await fits the existing codebase.
- Shared mutable state without actor, lock or isolation.
- `DispatchQueue.main` scattered around UI state.
- Force unwraps in production path.
- Escaping closures capturing `self` strongly.
