# Swift Scope Rules

- Verify the requested path exists.
- Prefer reading complete files in the target scope over relying on snippets.
- Expand scope only when the first findings prove it is necessary.
- For `Package.swift`, inspect targets, products, dependencies and platforms.
- For Xcode projects, inspect project and scheme structure before inventing build commands.
- Keep architecture changes explicit; do not silently change module boundaries or public contracts.
- If current Apple or dependency information is required, verify it with current sources before using it.
