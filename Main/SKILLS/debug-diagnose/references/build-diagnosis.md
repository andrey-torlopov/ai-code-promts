# Build Diagnosis

Check in this order:

1. Project type and build command.
2. Toolchain version and selected SDK when relevant.
3. Dependency resolution state.
4. Generated files or codegen steps.
5. Compiler or linker first error.
6. Recent local changes in the failing target.

Prefer focused commands over full rebuilds when the failure is already isolated.
