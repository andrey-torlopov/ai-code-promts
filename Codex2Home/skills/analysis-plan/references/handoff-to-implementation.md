# Handoff To Implementation

```text
task:
scope:
constraints:
confirmed-facts:
files-inspected:
assumptions:
decisions:
rejected-options:
artifacts:
done-criteria:
status:
next-step:
```

`files-inspected:` lists path, line ranges and the key fact per file, so an implementing
session re-reads only the files it edits, not the whole discovery scope. Inside the same
session the handoff is a skill switch: inspected files stay inspected and this block is
context, not a reason to re-read. Work that must outlive the session belongs in the
`task-lab` layer (facts as `F-NN`), not in a chain of handoff files.
