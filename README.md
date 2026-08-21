<p align="center">
  <img src="Docs/banner.png" alt="Templates Logo" width="600"/>
</p>

# Templates

Шаблон AI-контекста для Codex, Claude Code, Gemini и других agent-рантаймов.

Канонический шаблон лежит в `Main/`. Скрипт `init_ai.sh` копирует его в текущий проект.

Архитектура: **один SSOT → один роутер → ровно один skill → только объявленные им references и knowledge packs.** Ничего лишнего в контекст не загружается.

## Использование

```bash
cd /path/to/project
/path/to/Templates/init_ai.sh
```

Скрипт делает `cp -a Main/. .` — копирует содержимое `Main/` в текущую директорию.

### Алиас

В `~/.zshrc`:

```bash
alias initai='/path/to/Templates/init_ai.sh'
```

После этого:

```bash
cd /path/to/project
initai
```

Скрипт должен быть исполняемым (`chmod +x init_ai.sh`). Вызывайте его напрямую, а не через `source` — внутри стоит `set -euo pipefail`, и при сорсинге эти опции остаются в интерактивном shell.

## Глобальная установка для Codex

Чтобы не копировать `Main/` в каждый проект, установите глобальную Codex-версию:

```bash
./Codex2Home/init_codex.sh
```

По умолчанию инструкции и каноничные skills устанавливаются в
`${CODEX_HOME:-$HOME/.codex}`. Произвольный Codex home задаётся через
`--target DIR`; подробности, backup-стратегия и discovery skills описаны в
[`Codex2Home/README.md`](Codex2Home/README.md).
Установщик также добавляет нативный `SessionStart` hook: он загружает
`.codex/PROJECT.md` или корневой `PROJECT.md`, сохраняя посторонние entries в `hooks.json`.

## Структура

### Entrypoints

Короткие anchor-файлы, которые рантайм находит автоматически. Правил в себе не несут — только read order:

| Файл | Рантайм |
|---|---|
| `Main/AGENTS.md` | Codex и agent-рантаймы |
| `Main/CLAUDE.md` | Claude Code |
| `Main/GEMINI.md` | Gemini |

### Core

- `Main/CORE.md` — SSOT глобальных правил: read order, 7 core rules, языковая политика, skill/knowledge контракты.
- `Main/RESOLVER.md` — единая таблица маршрутизации в один workflow skill + tie-breakers + шаблоны `SKILL CONTEXT` и `TRACE`.
- `Main/COMMON.md` — compatibility bridge на `CORE.md` и `RESOLVER.md`. Новые правила сюда не добавляются.
- `Main/_core/` — общие блоки: `skill-context.md`, `handoff-template.md`, `validation.md`, `destructive-actions-policy.md`, `instruction-style.md`.
- `Main/_ai/` — рантайм-обвязка: hooks и `setup_context.md`.
- `Main/.claude/settings.json` — permissions и регистрация хуков для Claude Code. Личные переопределения в конкретном проекте кладутся в его собственный `.claude/settings.local.json` — он перекрывает project-слой и не коммитится.
- `Main/.aiignore`, `Main/.markdownlint.yaml` — границы контекста и правила markdown-линта.

#### Хуки

Копируются вместе с шаблоном и включаются автоматически в проекте, где выполнен `initai`:

| Хук | Событие | Что делает |
|---|---|---|
| `_ai/hooks/skill-lint.sh` | `PostToolUse` на `Write`/`Edit` | Проверяет только изменённый instruction-файл: frontmatter и обязательные заголовки в `SKILL.md`, anchor'ы на `CORE.md`/`RESOLVER.md`, bridge-статус `COMMON.md`, размер файла, ссылки на legacy-слои. Exit 2 возвращает findings агенту |
| `_ai/hooks/skill-context-lint.sh` | `Stop` | Проверяет, что каждый `SKILLS/*/SKILL.md` требует `SKILL CONTEXT` и финальный `TRACE` |

Оба хука безопасны в проектах без шаблона: если файла нет — `exit 0`.

Ручной прогон полной валидации:

```bash
sh SKILLS/skill-maintenance/scripts/skill-lint.sh .
sh _ai/hooks/skill-context-lint.sh .
```

### Active Skills

Активные маршруты живут в `Main/SKILLS/`. Skills атомарны: выбранный skill не читает соседние.

| Skill | Modes | Назначение |
|---|---|---|
| `swift-build-optimization` | `benchmark/analyze/fix/verify` | Замер и оптимизация времени сборки Xcode/Swift/iOS/macOS, SPM overhead, аудит build settings |
| `analysis-plan` | `plan/refactor/architecture/scout/deps/review/research/spec` | Анализ, планы, review, research, repo scout, dependency report, специи. Read-only, кроме явно запрошенного Markdown-артефакта |
| `implementation-from-plan` | — | Правки по утверждённому плану или прямой директиве + верификация |
| `debug-diagnose` | `build/ci/runtime/environment` | Диагностика build/CI/runtime/environment. Root cause и fix plan без скрытого перехода к правкам |
| `mac-local-ops` | — | Безопасные локальные shell/filesystem операции с destructive-action gate |
| `deploy-ops` | — | Deploy/release/publish/rollout с явным gate, rollback и верификацией |
| `skill-maintenance` | `authoring/audit/lint/registry/ai-context-init` | Обслуживание самой instruction/skill системы |

`swift-build-optimization` дополнительно несёт исполняемые Python-скрипты (`benchmark_builds.py`, `diagnose_compilation.py`, `summarize_build_timing.py`, `check_spm_pins.py`, генераторы отчётов) и JSON-схему бенчмарка.

`analysis-plan` несёт скрипты визуального компаньона (`server.cjs`, `start-server.sh`, `stop-server.sh`, `frame-template.html`).

### Knowledge

Lazy-loaded доменные правила в `Main/KNOWLEDGE/`. Загружаются только по сигналу из `KNOWLEDGE/_index.md` или по требованию выбранного skill; загруженные и пропущенные packs показываются в `SKILL CONTEXT`.

| Pack | Содержимое |
|---|---|
| `swift/` | Конвенции, верификация + каталог паттернов `swift/patterns/` |
| `ios/` | Feature-first архитектура, CI/CD |
| `devops/` | CI pipelines, deploy checks, verification |
| `shell/` | zsh, brew, mise |
| `python/` | Правила и верификация |

#### Каталог Swift-паттернов

`KNOWLEDGE/swift/patterns/` — 39 файлов в шести категориях, каждый с Bad/Good Example. Читается по одному файлу при обнаружении сигнала, превентивная загрузка всего каталога запрещена (token economy).

| Категория | Файлов | Фокус |
|---|---|---|
| `common/` | 10 | Гигиена кода, конвенции именования, дисциплина тестов |
| `performance/` | 10 | Горячие пути, строки, обход файловой системы, generic-константы |
| `networking/` | 7 | URLSession, Codable, валидация ответов, обёртка ошибок |
| `platform/` | 6 | Swift Concurrency и XCTest, flaky-тесты, таймауты |
| `best-practices/` | 3 | `final`, `let` по умолчанию, value types |
| `security/` | 3 | PII, логирование, утечки через ошибки |

## Роутинг

Рантайм читает строго по цепочке:

```text
AGENTS.md / CLAUDE.md / GEMINI.md
  -> CORE.md
  -> RESOLVER.md
  -> SKILLS/<selected-skill>/SKILL.md
  -> references/modes/scripts/assets, объявленные этим skill
  -> KNOWLEDGE/<domain> packs, названные резолвером или skill
```

Запрещено: выбранный skill → соседний skill, legacy prompt-слои, произвольные role-заметки.

### Ключевые границы

- Analysis/review/planning **не** подразумевает implementation.
- Deploy/release/publish/rollout **никогда** не идёт через `mac-local-ops`.
- Debug + «почини сейчас» → сначала `debug-diagnose`, передача в `implementation-from-plan` только после сформулированного root cause.
- Оптимизация времени сборки Xcode перехватывается `swift-build-optimization` раньше общих `analysis-plan` / `debug-diagnose`.
- Новый язык или стек не создаёт новый top-level skill — сначала добавляется `KNOWLEDGE/<domain>/`.
- Деструктивные операции требуют явного confirmation gate из `_core/destructive-actions-policy.md`.

## Обязательные блоки ответа

Перед существенной работой рантайм печатает `SKILL CONTEXT` (skill, mode, причина, загруженные и пропущенные knowledge packs, references, правила, артефакт, stop-граница), после — `TRACE` (что прочитано, какие паттерны применены, верификация, остаточный риск). Шаблоны — в `RESOLVER.md` и `_core/skill-context.md`.
