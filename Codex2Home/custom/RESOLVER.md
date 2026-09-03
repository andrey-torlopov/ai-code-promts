# Skill Resolver

Global router. Lives in `$CODEX_HOME/custom/RESOLVER.md` and applies to every project.

Use the most specific matching row: a row that names the failure, domain or system beats a
generic analysis row. Only on a true tie between equally specific rows choose the skill with
the safest stop gate.

## Invocation

The seven workflow skills below, plus the `task-lab` state layer, have canonical copies in
`$CODEX_HOME/skills/`. `init_codex.sh` exposes each one to native discovery through a symlink in
the configured user skill directory, which defaults to `$HOME/.agents/skills/`.

Selecting a row means invoking the resolved native skill when available, or reading
`$CODEX_HOME/skills/<skill>/SKILL.md` directly — equivalent paths; the `SKILL CONTEXT` block is
mandatory either way. A project skill with the same name in `.agents/skills/` wins over the
global one.

## Task State Layer

`task-lab` is a state layer, not a deliverable owner. It keeps durable task state on disk — a task
folder with `README.md` as the single entry point plus `env.json`, `Knowledge/`, `Steps/`,
`Results/`, `tools/`, `Notes/`, `Logs/`, `Inbox/` — so work survives
context loss. Except for a folder-only request (see below), it does not consume a routing row:
the table below still names exactly one workflow skill for the deliverable, and the layer only
decides where that deliverable and its evidence are recorded.

Availability is a precondition, never an assumption. Resolve `task-lab` from the native skill list
and use the path Codex exposes. Native candidates are the nearest `.agents/skills/task-lab/` from
the current directory up to the repository root and then `$HOME/.agents/skills/task-lab/`; a plugin
skill has its own exposed root. The shipped `$CODEX_HOME/skills/task-lab/` is the canonical
direct-read fallback. `<task-lab>` below means the resolved skill root. When it is absent, route
normally, declare `TASK: none`, and never hand-emulate the folder contract.

### Auto-Activation

Activate the layer without being asked when any signal holds:

| Signal | Example |
|---|---|
| the request names a TaskID as a task | `задача 123`, `по APP-001`, `task 42`, `bug 77` |
| a bare ID resolves to exactly one folder | `<task-lab>/scripts/resolve_task.py 123` exits 0 with one path |
| the request points into a task folder | a path whose root holds `README.md` with a `**Состояние:**` state line and `Steps/` |
| the working directory is that folder or below it | same shape at `cwd` or an ancestor |
| the user creates, resumes, audits or closes durable work | «заведи задачу», «продолжим», «что там по …», «закрой задачу» |
| the user requires the work to outlive this session | stated in the request |

Run the resolver from the workspace that holds task folders and pass `--workspace <root>` when they
live elsewhere; exit code 2 means no match or an ambiguous ID.

Do not activate on a number that is a version, port, PR or issue, line, date, size or quantity. A
bare number with no exact folder match and no task wording is not a TaskID: continue without the
layer. Do not scaffold a folder for work that fits one short session; say why instead.

### Composition

1. Skill and state before subject: invoke `task-lab` when available, or read
   `<task-lab>/SKILL.md` completely. Then let that skill resolve the folder, restore its bounded
   context and perform its drift check before inspecting the project.
2. The routing table still picks the deliverable owner; the layer adds state, never a second
   deliverable, and never overrides that skill's stop gate.
3. Every durable change inside the task folder happens under one open `Steps/Step-NN.md` and
   closes with its «Результат» block; a question the reply itself answers opens no step.
4. Artifacts land by kind: exports in `Results/`, verified claims as `Knowledge/F-NN`, open ones
   as `H-NN`, raw output in `Logs/`, journals in `Notes/`, task-local scripts in `tools/`,
   incoming material in `Inbox/`.
5. Project files outside the task folder keep their normal location; the step result records
   what changed there.
6. Finish the turn with the skill's audit and restore before reporting; report the folder path.

A request whose entire deliverable is the folder itself — create, resume, audit, restructure, close
— routes to `task-lab` alone: `SKILL: task-lab`, no second skill, no workflow row consumed.

| Request inside an active task | Deliverable owner | Where it lands |
|---|---|---|
| study, plan, review, research, spec | `analysis-plan` | `Results/` plus `Knowledge/` |
| implement, apply an approved plan | `implementation-from-plan` | project files plus the step's «Результат» block |
| build, CI, runtime or crash failure | `debug-diagnose` | root cause as `F-NN`, fix plan in `Results/` |
| Xcode/Swift build time | `swift-build-optimization` | benchmarks in `Notes/`, numbers as `F-NN` |
| deploy, release, publish, rollout | `deploy-ops` | gated action plus the step's «Результат» block |
| macOS, shell, local diagnosis | `mac-local-ops` | report plus `Notes/` |

`task-lab` is shipped and versioned by this instruction system: it is listed in
`$CODEX_HOME/custom/_core/active-skills.txt` and structurally linted like any workflow skill, even
though it never consumes a routing row. A skill invoked directly outside this table (one that
consumes no routing row) still emits the context block, declaring `SKILL: <name> (mode=direct)`.

## Skill Context Template

Substantial work must start with this flat block:

```text
SKILL: <skill> (mode=<mode-or-none>)
TASK: <TaskID -> absolute task-folder path, or none>
REASON: <why this skill owns the deliverable>
PROJECT: <project context file path or none>
KNOWLEDGE: <loaded packs or none>
SKIPPED: <relevant packs intentionally not loaded>
REFERENCES: <local references loaded or none>
RULES: <CORE rules and local gates>
ARTIFACT: <path or none>
STOP: <deliverable boundary; no hidden next phase>
```

Final reports for substantial work must include:

```text
TRACE:
- Skill:
- Task folder:
- References read:
- Knowledge read:
- Patterns/policies applied:
- Verification:
- Residual risk:
```

When `TASK` and `PROJECT` are `none` and no domain pack beyond the `general` fallback is
loaded, a three-line form is sufficient: `SKILL:`, `REASON:`, `STOP:`. Every other case uses
the full block.

## Routing Table

Row order aids scanning; matching is by specificity (see the meta-rule above), not by table
position.

| Request signal | Skill | Mode | Knowledge packs | Deliverable |
|---|---|---|---|---|
| optimize Xcode/iOS/macOS build time, slow clean build, slow incremental build, Swift compile hotspots, Xcode build settings audit, SPM build overhead | `swift-build-optimization` | `benchmark/analyze/fix/verify` | `swift`, `ios` | Benchmark artifacts, optimization plan, approved fixes plus re-benchmark |
| build fails, CI fails, runtime error, crash, logs, root cause, environment/toolchain/config failure | `debug-diagnose` | `build/ci/runtime/environment` | logs/build/CI/language-specific; `swift/debugging/` for Apple crash artifacts; `zig` for Zig panics and builds | Root cause plus fix plan |
| deploy, release, publish, rollout, production/staging operation | `deploy-ops` | none | `devops`, project-specific deploy docs | Gated deploy/release action |
| create/update/audit skills, instruction set, registry, lint | `skill-maintenance` | `authoring/audit/registry/lint/ai-context-init` | AI instruction rules | Changed skills or audit report |
| study, analyze, plan, RND, architecture, dependency, repo scout | `analysis-plan` | `plan/refactor/architecture/deps/scout` | selected by scope; `general` fallback | Markdown report or plan |
| review, PR review, diff review, find issues without edits | `analysis-plan` | `review` | language-specific patterns; `general` fallback | Findings/report |
| standalone research, comparison, external sources | `analysis-plan` | `research` | optional | Source-backed report |
| design spec, brainstorm, product or technical spec | `analysis-plan` | `spec` | optional/domain-specific | Design/spec artifact |
| implement, do from plan, apply fix, concrete edit | `implementation-from-plan` | none | language/project-specific; `general` fallback | Changed files plus verification |
| macOS, shell, files, zsh, brew, mise; file operations, inventory and local execution without a failure symptom | `mac-local-ops` | none | `shell`, macOS/project-specific | Safe local action/report |

## Tie-Breakers

1. Explicit user skill selection wins if it does not contradict the task.
2. A failure, crash, error or red pipeline routes to `debug-diagnose` before `analysis-plan`,
   even when the request says analyze, study or investigate.
3. An audit of skills, instructions, routing or knowledge packs routes to `skill-maintenance`
   before `analysis-plan` mode `review`.
4. If a request contains analysis and code changes, choose `analysis-plan` first unless there is an approved plan or a concrete edit directive. The later implementation is a skill switch inside the same context: files already inspected stay inspected.
5. If a request contains debug and "fix it now", choose `debug-diagnose` first, then hand off to `implementation-from-plan` only after a root cause is stated. That handoff is a skill switch inside the same context, not a new agent or session.
6. Deploy/release/publish/rollout never routes to `mac-local-ops`.
7. Destructive local operations require the destructive-action confirmation gate.
8. `analysis-plan` does not change project files except an explicitly requested Markdown artifact.
9. `implementation-from-plan` does not change architecture beyond the approved plan or concrete directive.
10. Do not create a new top-level skill for a new language or stack; add `$CODEX_HOME/custom/KNOWLEDGE/<domain>/` first.
11. Xcode build-time optimization routes to `swift-build-optimization` before generic `analysis-plan`, `debug-diagnose` or `implementation-from-plan`; its approval gate decides whether the turn stops at a plan or proceeds to edits.
12. `task-lab` never replaces the deliverable owner; it wraps it. Only a request about the task folder itself routes to `task-lab` alone.
13. When the layer is active, the deliverable is written into the task folder, but the selected skill's stop gate still decides whether project files may change at all.
14. An unresolvable TaskID stops the turn: ask for the path or the search root instead of inventing a folder.
15. On a name or signal collision, a shipped skill resolved through `.agents/skills/` or
    `$CODEX_HOME/skills/` wins over a plugin or built-in skill of the same purpose, because only
    the shipped one carries this system's `SKILL CONTEXT` and `TRACE` contract. Known collisions
    and their winners:

| Signal | Use | Do not substitute implicitly |
|---|---|---|
| review a code diff or PR | `analysis-plan` mode `review` | a generic review skill |
| build/CI/runtime failure, crash, logs | `debug-diagnose` | a generic debugging skill |
| write Markdown docs, README, runbook | `analysis-plan` mode `spec` | a document-format skill |
| test plan or coverage strategy | `analysis-plan` mode `plan` | a generic testing skill |
| architecture, ADR, system design | `analysis-plan` mode `architecture` | a generic architecture skill |
| deploy or release checklist | `deploy-ops` | a generic deployment skill |
| create or audit this instruction system | `skill-maintenance` | a generic skill creator |

16. Rule 15 yields to rule 1: explicitly naming another installed skill or plugin is an explicit
    selection and wins. A plugin skill with no local counterpart — Office documents, scheduling,
    artifacts or browser work — is used normally and consumes no routing row.

## Read Order

The canonical read order lives in `$CODEX_HOME/custom/CORE.md`. Forbidden active reads:
selected skill -> sibling skill, legacy prompt layers or random role notes.
