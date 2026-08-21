# Skill Resolver

Global router. Lives in `$CODEX_HOME/custom/RESOLVER.md` and applies to every project.

Use the first concrete deliverable match. If several rows match, choose the skill with the safest stop gate.

## Invocation

The seven workflow skills have their canonical copies in `$CODEX_HOME/skills/`.
`init_codex.sh` exposes each one to Codex discovery through a symlink in the configured
user skill directory, which defaults to `$HOME/.agents/skills/`. Selecting a row means
invoking that native skill when available; otherwise read
`$CODEX_HOME/skills/<skill>/SKILL.md` directly. Both paths are equivalent, and the
`SKILL CONTEXT` block is mandatory either way.

For any native skill, use the skill root exposed by Codex rather than reconstructing its path.
`<selected-skill>` below means that resolved root. The `$CODEX_HOME/skills/<skill>/` fallback is
only for workflow skills shipped by this template.

A project may override a global skill by defining a skill with the same name in its own
`.agents/skills/`. The project version wins.

## Task State Layer

`task-lab` is a state layer, not a deliverable owner. It keeps durable task state on disk — a task
folder with `Context/`, `Knowledge/`, `Steps/`, `Results/`, `Notes/`, `Inbox/` — so work survives
context loss. It does not consume a routing row: the table below still names exactly one workflow
skill for the deliverable, and the layer only decides where that deliverable and its evidence are
recorded.

Availability is a precondition, never an assumption. Resolve `task-lab` from the native skill list
and use the file path Codex exposes. Native local candidates are the nearest
`.agents/skills/task-lab/` from the current directory up to the repository root and then
`$HOME/.agents/skills/task-lab/`; a plugin skill has its own exposed root. A manually installed
`$CODEX_HOME/skills/task-lab/` containing `SKILL.md` is a direct-read compatibility fallback, not
a standard Codex discovery location unless it is linked into a scanned directory. `<task-lab>`
below means the resolved skill root. When it is absent, route normally, declare `TASK: none`, and
never hand-emulate the folder contract.

### Auto-Activation

Activate the layer without being asked when any signal holds:

| Signal | Example |
|---|---|
| the request names a TaskID as a task | `задача 123`, `по APP-001`, `task 42`, `bug 77` |
| a bare ID resolves to exactly one folder | `<task-lab>/scripts/resolve_task.py 123` exits 0 with one path |
| the request points into a task folder | a path whose root holds `index.md`, `steps.md` and `Steps/` |
| the working directory is that folder or below it | same shape at `cwd` or an ancestor |
| the user creates, resumes, audits or closes durable work | «заведи задачу», «продолжим», «что там по …», «закрой задачу» |
| the user requires the work to outlive this session | stated in the request |

Run the resolver from the workspace that holds task folders and pass `--workspace <root>` when they
live elsewhere; exit code 2 means no match or an ambiguous ID.

Do not activate on a number that is a version, port, PR or issue, line, date, size or quantity. A
bare number with no exact folder match and no task wording is not a TaskID: continue without the
layer. Do not scaffold a folder for work that fits one short session; say why instead.

### Composition

1. Skill and state before subject: invoke native `$task-lab` when available, or read
   `<task-lab>/SKILL.md` completely. Then let that skill resolve the folder, run its bounded
   restore and perform its drift check before inspecting or changing the task subject.
2. The routing table still picks the deliverable owner. The layer adds state, not a second
   deliverable, and never overrides that skill's stop gate.
3. Every durable change inside the task folder happens under one open `Step-XX.md` and closes with
   `Step-XX-result.md`. A question the reply itself answers opens no step.
4. Artifacts land by kind: exports in `Results/`, verified claims as `Knowledge/F-NN`, open ones as
   `H-NN`, raw logs and measurements in `Notes/`, task-local scripts in `Context/tools/`, incoming
   material in `Inbox/`.
5. Project files outside the task folder keep their normal location; the step result records what
   changed there.
6. Finish the turn with the skill's audit and restore before reporting; report the folder path.

A request whose entire deliverable is the folder itself — create, resume, audit, restructure, close
— routes to `task-lab` alone: `SKILL: task-lab`, no second skill, no workflow row consumed.

| Request inside an active task | Deliverable owner | Where it lands |
|---|---|---|
| study, plan, review, research, spec | `analysis-plan` | `Results/` plus `Knowledge/` |
| implement, apply an approved plan | `implementation-from-plan` | project files plus `Step-XX-result.md` |
| build, CI, runtime or crash failure | `debug-diagnose` | root cause as `F-NN`, fix plan in `Results/` |
| Xcode/Swift build time | `swift-build-optimization` | benchmarks in `Notes/`, numbers as `F-NN` |
| deploy, release, publish, rollout | `deploy-ops` | gated action plus `Step-XX-result.md` |
| macOS, shell, local diagnosis | `mac-local-ops` | report plus `Notes/` |

`task-lab` ships outside this instruction system, so it stays out of
`$CODEX_HOME/custom/_core/active-skills.txt` and is not structurally linted here, exactly like
`graphify`.

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
| study, analyze, plan, RND, architecture, dependency, repo scout | `analysis-plan` | `plan/refactor/architecture/deps/scout` | selected by scope | Markdown report or plan |
| review, PR review, diff review, find issues without edits | `analysis-plan` | `review` | language-specific patterns | Findings/report |
| standalone research, comparison, external sources | `analysis-plan` | `research` | optional | Source-backed report |
| design spec, brainstorm, product or technical spec | `analysis-plan` | `spec` | optional/domain-specific | Design/spec artifact |
| implement, do from plan, apply fix, concrete edit | `implementation-from-plan` | none | language/project-specific | Changed files plus verification |
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
8. Do not create a new top-level skill for a new language or stack; add `$CODEX_HOME/custom/KNOWLEDGE/<domain>/` first.
9. Xcode build-time optimization routes to `swift-build-optimization` before generic `analysis-plan`, `debug-diagnose` or `implementation-from-plan`; its approval gate decides whether the turn stops at a plan or proceeds to edits.
10. `task-lab` never replaces the deliverable owner; it wraps it. Only a request about the task folder itself routes to `task-lab` alone.
11. When the layer is active, the deliverable is written into the task folder, but the selected skill's stop gate still decides whether project files may change at all.
12. An unresolvable TaskID stops the turn: ask for the path or the search root instead of inventing a folder.

## Canonical Read Order

```text
$CODEX_HOME/AGENTS.md  (then project AGENTS.override.md / AGENTS.md layers)
  -> $CODEX_HOME/custom/CORE.md
  -> $CODEX_HOME/custom/RESOLVER.md
  -> <task-lab>/SKILL.md when the task state layer is active (state before subject)
  -> project PROJECT.md when the repository provides one (injected on SessionStart)
  -> <selected-skill>/SKILL.md for the deliverable-owning workflow skill
     (skip when task-lab alone owns task-folder lifecycle work)
  -> references/scripts/assets named by active skills
  -> $CODEX_HOME/custom/KNOWLEDGE/<domain> packs named by resolver or selected skill
  -> project-local KNOWLEDGE/ or .agents/skills/ only when the project defines them
```

Forbidden active read order:

```text
selected skill -> sibling skill
selected skill -> legacy prompt layers
selected skill -> random role notes
```
