<p align="center">
  <img src="Docs/banner.png" alt="Templates Logo" width="600"/>
</p>

# Templates

Шаблон AI-контекста для Claude Code, Codex и других agent-рантаймов.

Инструкции ставятся **в домашний каталог рантайма**, а не копируются в каждый проект:

| Шаблон | Устанавливает в | Скрипт |
|---|---|---|
| [`Claude2Home/`](Claude2Home/) | `~/.claude` | `./Claude2Home/init_claude.sh` |
| [`Codex2Home/`](Codex2Home/) | `${CODEX_HOME:-~/.codex}` | `./Codex2Home/init_codex.sh` |

Проект после этого не содержит инструкций вообще — только опциональный `PROJECT.md` с
проверенными фактами, который подхватывается хуком на старте сессии.

Архитектура: **один SSOT → один роутер → ровно один skill → только объявленные им references и
knowledge packs.** Ничего лишнего в контекст не загружается.

> Прежний маршрут «копировать `Main/` в каждый проект скриптом `init_ai.sh`» выведен из
> обращения и лежит в `Archive/`. Он использует структуру `SKILLS/` и `_ai/layers/`, которую
> текущий валидатор помечает как запрещённую. Не используйте его.

## Установка

```bash
./Claude2Home/init_claude.sh --dry-run   # показать, что изменится
./Claude2Home/init_claude.sh             # установить в ~/.claude
```

Заменяемые файлы сначала копируются в `~/.claude/backups/home-template-<timestamp>/`.
После копирования установщик прогоняет валидатор и падает, если что-то сломано.
Произвольная цель — `--target DIR`; подробности в [`Claude2Home/README.md`](Claude2Home/README.md).

Для Codex — [`Codex2Home/README.md`](Codex2Home/README.md): тот же набор скиллов, нативный
`SessionStart` hook и symlink-discovery в `${CODEX_USER_SKILLS_DIR:-~/.agents/skills}`.

## Что попадает в `~/.claude`

```text
~/.claude/
├── CLAUDE.md                 anchor: личные правила + read order в custom/
├── settings.json             модель, permissions, регистрация хуков
├── hooks/                    4 хука, см. ниже
├── skills/                   7 workflow-скиллов + task-lab + graphify
└── custom/
    ├── CORE.md               SSOT глобальных правил
    ├── RESOLVER.md           таблица маршрутизации + tie-breakers
    ├── COMMON.md             compatibility bridge, новых правил не несёт
    ├── _core/                skill-context, handoff, validation, destructive-actions
    │   └── active-skills.txt реестр, который читают все три линтера
    └── KNOWLEDGE/            lazy-loaded доменные паки
```

### Core

- `custom/CORE.md` — SSOT: read order, 8 core rules, языковая политика, контракты skill,
  knowledge и project context.
- `custom/RESOLVER.md` — таблица маршрутизации в один workflow skill, слой состояния `task-lab`,
  tie-breakers, шаблоны `SKILL CONTEXT` и `TRACE`.
- `custom/COMMON.md` — compatibility bridge на `CORE.md` и `RESOLVER.md`.
- `custom/_core/` — общие блоки: `skill-context.md`, `handoff-template.md`, `validation.md`,
  `destructive-actions-policy.md`, `instruction-style.md`, `active-skills.txt`.

### Хуки

| Хук | Событие | Что делает |
|---|---|---|
| `bash-guard.sh` | `PreToolUse` на `Bash` | Разбирает команду целиком, а не по префиксу: `deny` для катастрофического, `ask` для необратимого. Требует `jq` |
| `project-context.sh` | `SessionStart` | Инжектит `PROJECT.md` или `.claude/PROJECT.md` проекта, помечая тело как данные. Обрезает на 20000 байт |
| `skill-lint.sh` | `PostToolUse` на `Write`/`Edit` | Быстрая проверка одного изменённого instruction-файла. Exit 2 возвращает findings агенту |
| `skill-context-lint.sh` | `Stop` | Каждый зарегистрированный `SKILL.md` обязан требовать `SKILL CONTEXT` и финальный `TRACE` |

Все хуки безопасны вне шаблона: нет файла — `exit 0`.

Полная валидация вручную:

```bash
sh Claude2Home/skills/skill-maintenance/scripts/skill-lint.sh Claude2Home   # исходное дерево
sh ~/.claude/skills/skill-maintenance/scripts/skill-lint.sh                 # установленная система
```

### Skills

Живут в `Claude2Home/skills/`, ставятся в `~/.claude/skills/`. Skills атомарны: выбранный skill
не читает соседние.

| Skill | Modes | Назначение |
|---|---|---|
| `swift-build-optimization` | `benchmark/analyze/fix/verify` | Замер и оптимизация времени сборки Xcode/Swift/iOS/macOS, SPM overhead, аудит build settings |
| `analysis-plan` | `plan/refactor/architecture/scout/deps/review/research/spec` | Анализ, планы, review, research, repo scout, dependency report, спеки. Read-only, кроме явно запрошенного Markdown-артефакта |
| `implementation-from-plan` | — | Правки по утверждённому плану или прямой директиве + верификация |
| `debug-diagnose` | `build/ci/runtime/environment` | Диагностика build/CI/runtime/environment. Root cause и fix plan без скрытого перехода к правкам |
| `mac-local-ops` | — | Безопасные локальные shell/filesystem операции с destructive-action gate |
| `deploy-ops` | — | Deploy/release/publish/rollout с явным gate, rollback и верификацией |
| `skill-maintenance` | `authoring/audit/lint/registry/ai-context-init` | Обслуживание самой instruction/skill системы |

Сверх семи workflow-маршрутов:

- **`task-lab`** — слой состояния, а не владелец результата. Держит папку задачи на диске
  (`Context/`, `Knowledge/`, `Steps/`, `Results/`, `Notes/`, `Inbox/`), чтобы работа пережила
  потерю контекста. Активируется по TaskID или пути в папку задачи, routing-строку не занимает.
  Зарегистрирован в `active-skills.txt` и линтуется наравне с workflow-скиллами.
- **`graphify`** — построение графа знаний по произвольному входу. Версионируется шаблоном, но
  вне реестра и вне структурного линта; вызывается напрямую.

`swift-build-optimization` дополнительно несёт Python-скрипты (`benchmark_builds.py`,
`diagnose_compilation.py`, `summarize_build_timing.py`, `check_spm_pins.py`, генераторы отчётов)
и JSON-схему бенчмарка. `analysis-plan` несёт скрипты визуального компаньона (`server.cjs`,
`start-server.sh`, `stop-server.sh`, `frame-template.html`). `task-lab` несёт
`init_task.py`, `resolve_task.py`, `restore_task.py`, `audit_task.py`, `self_test.py`.

### Knowledge

Lazy-loaded доменные правила в `custom/KNOWLEDGE/`. Загружаются только по сигналу из
`KNOWLEDGE/_index.md` или по требованию выбранного skill; загруженные и пропущенные packs
показываются в `SKILL CONTEXT`.

| Pack | Содержимое |
|---|---|
| `swift/` | Конвенции, верификация, `swift/debugging/` + каталог паттернов `swift/patterns/` |
| `ios/` | Feature-first архитектура, CI/CD |
| `devops/` | CI pipelines, deploy checks, verification |
| `shell/` | zsh, brew, mise |
| `python/` | Правила и верификация |
| `zig/` | Правила, отладка, верификация |

#### Каталог Swift-паттернов

`KNOWLEDGE/swift/patterns/` — 39 файлов в шести категориях, каждый с Bad/Good Example. Читается
по одному файлу при обнаружении сигнала, превентивная загрузка всего каталога запрещена
(token economy).

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
~/.claude/CLAUDE.md  (или проектный CLAUDE.md / AGENTS.md)
  -> ~/.claude/custom/CORE.md
  -> ~/.claude/custom/RESOLVER.md
  -> ~/.claude/skills/task-lab/ когда активен слой состояния (state before subject)
  -> PROJECT.md проекта, если он есть (инжектится хуком на SessionStart)
  -> ~/.claude/skills/<selected-skill>/SKILL.md
  -> references/modes/scripts/assets, объявленные этим skill
  -> ~/.claude/custom/KNOWLEDGE/<domain> packs, названные резолвером или skill
```

Запрещено: выбранный skill → соседний skill, legacy prompt-слои, произвольные role-заметки.

### Ключевые границы

- Analysis/review/planning **не** подразумевает implementation.
- Deploy/release/publish/rollout **никогда** не идёт через `mac-local-ops`.
- Debug + «почини сейчас» → сначала `debug-diagnose`, передача в `implementation-from-plan`
  только после сформулированного root cause.
- Оптимизация времени сборки Xcode перехватывается `swift-build-optimization` раньше общих
  `analysis-plan` / `debug-diagnose`.
- Новый язык или стек не создаёт новый top-level skill — сначала добавляется `KNOWLEDGE/<domain>/`.
- `task-lab` не заменяет владельца результата, а оборачивает его.
- Деструктивные операции требуют явного confirmation gate из `_core/destructive-actions-policy.md`.
- Изменения под `~/.claude/` требуют явного намерения пользователя (core rule 8).

## Проектный контекст

Репозиторий может положить в корень `PROJECT.md` (или `.claude/PROJECT.md`) с проверенными
фактами: стек, команды, layout, CI, глоссарий, ограничения, запретные пути. Хук
`project-context.sh` инжектит его на старте сессии; агент объявляет путь в `SKILL CONTEXT`
как `PROJECT:`.

Файл добавляет факты и сужает scope, но не переопределяет core rules 5, 7 и 8. Держите его
короче 200 строк, глубокий домен — в `KNOWLEDGE/<domain>/`. Сгенерировать по шаблону:
`skill-maintenance` mode `ai-context-init`.

## Обязательные блоки ответа

Перед существенной работой рантайм печатает `SKILL CONTEXT` (skill, mode, task folder, причина,
project context, загруженные и пропущенные knowledge packs, references, правила, артефакт,
stop-граница), после — `TRACE` (что прочитано, какие паттерны применены, верификация, остаточный
риск). Шаблоны — в `custom/RESOLVER.md` и `custom/_core/skill-context.md`.
