# Skill Resolver

Global router. Lives in `~/.claude/custom/RESOLVER.md` and applies to every project.

Use the first concrete deliverable match. If several rows match, choose the skill with the safest stop gate.

## Invocation

The seven workflow skills below, plus the `task-lab` state layer, are installed as native user
skills in `~/.claude/skills/`.
Selecting a row means invoking that skill through the runtime's skill mechanism when one exists,
otherwise reading `~/.claude/skills/<skill>/SKILL.md` directly. Both paths are equivalent;
the `SKILL CONTEXT` block is mandatory either way.

A project may override a global skill by defining a skill with the same name in its own
`.claude/skills/`. The project version wins.

## Task State Layer

`task-lab` is a state layer, not a deliverable owner. It keeps durable task state on disk — a task
folder with `README.md` as the single entry point plus `env.json`, `Knowledge/`, `Steps/`,
`Results/`, `tools/`, `Notes/`, `Logs/`, `Inbox/` — so work survives
context loss. It does not consume a routing row: the table below still names exactly one workflow
skill for the deliverable, and the layer only decides where that deliverable and its evidence are
recorded.

Availability is a precondition, never an assumption. The layer is active only when a `task-lab`
skill is installed, as `~/.claude/skills/task-lab/` or as a plugin skill of that name; `<task-lab>`
below means that skill root. When it is absent, route normally, declare `TASK: none`, and never
hand-emulate the folder contract.

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

1. State before subject: resolve the folder, run `<task-lab>/scripts/restore_task.py`, perform the
   drift check, and only then read the project.
2. The routing table still picks the deliverable owner. The layer adds state, not a second
   deliverable, and never overrides that skill's stop gate.
3. Every durable change inside the task folder happens under one open `Steps/Step-NN.md` and
   closes with that file's «Результат» block. A question the reply itself answers opens no step.
4. Artifacts land by kind: exports in `Results/`, verified claims as `Knowledge/F-NN`, open ones as
   `H-NN`, raw captured output in `Logs/`, observation journals in `Notes/`, task-local scripts in
   `tools/`, incoming material in `Inbox/`.
5. Project files outside the task folder keep their normal location; the step result records what
   changed there.
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
`~/.claude/custom/_core/active-skills.txt` and structurally linted like any workflow skill, even
though it never consumes a routing row. `graphify` is shipped too but stays out of the registry and
out of the structural lint; it is invoked directly, not through this table.

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

## Routing Table

| Request signal | Skill | Mode | Knowledge packs | Deliverable |
|---|---|---|---|---|
| optimize Xcode/iOS/macOS build time, slow clean build, slow incremental build, Swift compile hotspots, Xcode build settings audit, SPM build overhead | `swift-build-optimization` | `benchmark/analyze/fix/verify` | `swift`, `ios` | Benchmark artifacts, optimization plan, approved fixes plus re-benchmark |
| study, analyze, plan, RND, architecture, dependency, repo scout | `analysis-plan` | `plan/refactor/architecture/deps/scout` | selected by scope; `general` fallback | Markdown report or plan |
| review, PR review, diff review, find issues without edits | `analysis-plan` | `review` | language-specific patterns; `general` fallback | Findings/report |
| standalone research, comparison, external sources | `analysis-plan` | `research` | optional | Source-backed report |
| design spec, brainstorm, product or technical spec | `analysis-plan` | `spec` | optional/domain-specific | Design/spec artifact |
| implement, do from plan, apply fix, concrete edit | `implementation-from-plan` | none | language/project-specific; `general` fallback | Changed files plus verification |
| build fails, CI fails, runtime error, crash, logs, root cause | `debug-diagnose` | `build/ci/runtime/environment` | logs/build/CI/language-specific; `swift/debugging/` for Apple crash artifacts; `zig` for Zig panics and builds | Root cause plus fix plan |
| macOS, shell, files, zsh, brew, mise, local diagnosis | `mac-local-ops` | none | `shell`, macOS/project-specific | Safe local action/report |
| deploy, release, publish, rollout, production/staging operation | `deploy-ops` | none | `devops`, project-specific deploy docs | Gated deploy/release action |
| create/update/audit skills, instruction set, registry, lint | `skill-maintenance` | `authoring/audit/registry/lint/ai-context-init` | AI instruction rules | Changed skills or audit report |

## Tie-Breakers

1. Explicit user skill selection wins if it does not contradict the task.
2. If a request contains analysis and code changes, choose `analysis-plan` first unless there is an approved plan or a concrete edit directive.
3. If a request contains debug and "fix it now", choose `debug-diagnose` first, then hand off to `implementation-from-plan` only after a root cause is stated.
4. Deploy/release/publish/rollout never routes to `mac-local-ops`.
5. Destructive local operations require the destructive-action confirmation gate.
6. `analysis-plan` does not change project files except an explicitly requested Markdown artifact.
7. `implementation-from-plan` does not change architecture beyond the approved plan or concrete directive.
8. Do not create a new top-level skill for a new language or stack; add `~/.claude/custom/KNOWLEDGE/<domain>/` first.
9. Xcode build-time optimization routes to `swift-build-optimization` before generic `analysis-plan`, `debug-diagnose` or `implementation-from-plan`; its approval gate decides whether the turn stops at a plan or proceeds to edits.
10. `task-lab` never replaces the deliverable owner; it wraps it. Only a request about the task folder itself routes to `task-lab` alone.
11. When the layer is active, the deliverable is written into the task folder, but the selected skill's stop gate still decides whether project files may change at all.
12. An unresolvable TaskID stops the turn: ask for the path or the search root instead of inventing a folder.
13. On a name or signal collision, a skill from `~/.claude/skills/` wins over a plugin or built-in
    skill of the same purpose, because only the local one carries the `SKILL CONTEXT` and `TRACE`
    contract. Known collisions and their winners:

| Signal | Use | Not |
|---|---|---|
| review a diff or PR | `analysis-plan` mode `review` | `code-review`, `engineering:code-review` |
| build/CI/runtime failure, crash, logs | `debug-diagnose` | `engineering:debug` |
| write docs, README, runbook | `analysis-plan` mode `spec` | `engineering:documentation` |
| test plan, coverage strategy | `analysis-plan` mode `plan` | `engineering:testing-strategy` |
| architecture, ADR, system design | `analysis-plan` mode `architecture` | `engineering:architecture`, `engineering:system-design` |
| deploy, release checklist | `deploy-ops` | `engineering:deploy-checklist` |
| create or audit a skill | `skill-maintenance` | `anthropic-skills:skill-creator` |

14. Rule 13 yields to rule 1: naming a plugin skill explicitly (`/engineering:code-review`) is an
    explicit selection and wins. A plugin skill that has no local counterpart — Office documents,
    scheduling, artifacts, browser work — is used normally and consumes no routing row.

## Canonical Read Order

```text
~/.claude/CLAUDE.md  (or project CLAUDE.md / AGENTS.md)
  -> ~/.claude/custom/CORE.md
  -> ~/.claude/custom/RESOLVER.md
  -> ~/.claude/skills/task-lab/ when the task state layer is active (state before subject)
  -> project PROJECT.md when the repository provides one (injected on SessionStart)
  -> ~/.claude/skills/<selected-skill>/SKILL.md
  -> references/scripts/assets named by selected skill
  -> ~/.claude/custom/KNOWLEDGE/<domain> packs named by resolver or selected skill
  -> project-local KNOWLEDGE/ or .claude/skills/ only when the project defines them
```

Forbidden active read order:

```text
selected skill -> sibling skill
selected skill -> legacy prompt layers
selected skill -> random role notes
```
