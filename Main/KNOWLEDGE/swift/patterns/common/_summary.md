# Common Swift Patterns

## Architecture

- Do not propose a new architecture without checking existing structure.
- Keep module boundaries stable unless the user asks to change them.

## Tests

- Avoid order-dependent tests.
- Avoid static shared test data when it can collide across runs.
- Clean up files, database rows, user defaults and temporary resources created by tests.
- Add assertion messages when failure would otherwise be ambiguous.

## Code Style

- Use clear names that match Swift API Design Guidelines.
- Keep files and types focused.
- Avoid abstraction layers that hide behavior without reducing complexity.
