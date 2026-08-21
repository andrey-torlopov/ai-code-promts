<p align="center">
  <img src="Docs/banner.png" alt="Templates Logo" width="600"/>
</p>

# Templates

Два переносимых Home-шаблона одной instruction-системы:

- [`Claude2Home/`](Claude2Home/) устанавливается в домашний каталог Claude Code;
- [`Codex2Home/`](Codex2Home/) устанавливается в `CODEX_HOME` и публикует skills в нативный
  discovery-каталог Codex.

Оба шаблона используют один архитектурный контракт: глобальный anchor → `CORE.md` →
`RESOLVER.md` → ровно один workflow skill → только объявленные им references и knowledge packs.
`task-lab` может дополнительно обернуть работу durable state-слоем, но не заменяет владельца
результата.

Установка Home-шаблона — единственный поддерживаемый способ развернуть систему. Legacy-маршрут с
копированием `Main/` и `_ai/layers/` в каждый проект больше не является частью текущей топологии.
Проекту не нужна локальная копия глобальных инструкций; при необходимости он добавляет только
собственные `PROJECT.md`, `AGENTS.md` или runtime-specific overrides.

## Быстрый старт

Запускайте команды из корня этого репозитория:

```sh
./Claude2Home/init_claude.sh --dry-run
./Claude2Home/init_claude.sh

./Codex2Home/init_codex.sh --dry-run
./Codex2Home/init_codex.sh
```

`--dry-run` ничего не изменяет. Оба установщика создают backup заменяемых путей, если явно не
передан `--no-backup`, и запускают validator после реальной установки.

Подробные параметры:

- [установка Claude2Home](Claude2Home/README.md);
- [установка Codex2Home](Codex2Home/README.md).

## Сравнение рантаймов

| Контракт | Claude2Home | Codex2Home |
|---|---|---|
| Каталог источника | `Claude2Home/` | `Codex2Home/` |
| Цель по умолчанию | `${CLAUDE_CONFIG_DIR:-$HOME/.claude}` | `${CODEX_HOME:-$HOME/.codex}` |
| Глобальный anchor | `CLAUDE.md` | `AGENTS.md` |
| Конфигурация hooks | `settings.json`, заменяется целиком | `hooks.json`, управляемый `project-context` entry сливается с существующими entries |
| Hook scripts | четыре скрипта в `hooks/` | `hooks/project-context.sh` |
| Project override | `.claude/PROJECT.md`, затем `PROJECT.md` | `.codex/PROJECT.md`, затем `PROJECT.md` |
| Каноничные skills | `<target>/skills/<name>` | `<target>/skills/<name>` |
| Native discovery | напрямую из `~/.claude/skills/` | symlink в `${CODEX_USER_SKILLS_DIR:-$HOME/.agents/skills}` |
| Backup | `<target>/backups/home-template-<timestamp>/` | `<target>/backups/codex2home-<timestamp>-<pid>/` |
| Дополнительная зависимость | `jq` для разбора Bash-команд в `bash-guard` | Python 3 для безопасного merge `hooks.json` |

Claude installer переносит `CLAUDE.md`, `settings.json`, поставляемые hooks, `custom/` и каждый
поставляемый skill. Он подставляет реальный `$HOME` вместо `{{HOME}}` в машинно-зависимых deny
paths.

Codex installer не изменяет `config.toml`, `auth.json`, историю, сессии, плагины, кэши и
посторонние hooks. После первой установки или изменения определения hook откройте `/hooks` в Codex
и подтвердите `project-context`: доверие привязано к hash определения.

## Общая структура

Обе папки поставляют одинаковые логические слои, адаптированные к путям и lifecycle-механизмам
своего рантайма:

```text
<runtime-home>/
├── <anchor>                  CLAUDE.md или AGENTS.md
├── <hook configuration>      settings.json или hooks.json
├── hooks/                    runtime-specific lifecycle handlers
├── custom/
│   ├── CORE.md               SSOT глобальных правил
│   ├── RESOLVER.md           request signal -> один workflow skill
│   ├── COMMON.md             compatibility bridge
│   ├── _core/                validation, skill context, handoff, safety
│   └── KNOWLEDGE/            lazy-loaded доменные packs
└── skills/
    ├── <seven workflow skills>
    ├── task-lab/             durable state layer
    └── graphify/             direct-invocation skill
```

`custom/` при установке заменяется целиком с предварительным backup. Поставляемые skills
заменяются поимённо; посторонние skills остаются нетронутыми.

## Порядок загрузки

Для существенной задачи применяется следующий контракт:

```text
runtime anchor
  -> custom/CORE.md
  -> custom/RESOLVER.md
  -> task-lab/SKILL.md, только если активирован durable state layer
  -> PROJECT.md или runtime-specific PROJECT.md, если файл существует
  -> один deliverable-owning workflow SKILL.md
  -> только названные references, modes, scripts и assets
  -> только релевантные custom/KNOWLEDGE packs
```

Запрещены скрытые переходы `selected skill -> sibling skill`, legacy prompt layers и
произвольные role-файлы. Project context добавляет проверенные факты и сужает scope, но не может
отменить destructive-action, deploy и global-config gates из `CORE.md`.

## Skills

Обе папки содержат одинаковый набор workflow skills:

| Skill | Modes | Назначение |
|---|---|---|
| `swift-build-optimization` | `benchmark/analyze/fix/verify` | Замер и оптимизация Xcode/Swift build time, SPM overhead и build settings |
| `analysis-plan` | `plan/refactor/architecture/scout/deps/review/research/spec` | Анализ, планы, review, research, repository scout и спецификации |
| `implementation-from-plan` | — | Реализация утверждённого плана или прямой concrete-edit директивы с верификацией |
| `debug-diagnose` | `build/ci/runtime/environment` | Root cause и fix plan без автоматического изменения кода |
| `mac-local-ops` | — | Безопасные локальные shell/filesystem операции |
| `deploy-ops` | — | Deploy/release/publish/rollout с confirmation, rollback и verification gates |
| `skill-maintenance` | `authoring/audit/lint/registry/ai-context-init` | Создание, аудит и обслуживание instruction-системы |

Специальные skills:

- `task-lab` — поставляемый и зарегистрированный state layer. Он хранит `Context/`, `Knowledge/`,
  `Steps/`, `Results/`, `Notes/` и `Inbox/`, активируется по TaskID или task-folder и не занимает
  routing-строку. Его scripts включают init, resolve, restore, audit и self-test.
- `graphify` — поставляемый direct-invocation skill для графа знаний. Он вызывается по
  `/graphify` или при работе с существующим `graphify-out/`, но не входит в workflow-реестр и
  структурный lint.

## Knowledge packs

`custom/KNOWLEDGE/` в обоих шаблонах содержит домены:

| Pack | Содержимое |
|---|---|
| `swift/` | Конвенции, verification, debugging и каталог code-review patterns |
| `ios/` | Feature-first архитектура и CI/CD |
| `devops/` | CI pipelines, deploy checks и verification |
| `shell/` | zsh, Homebrew и mise |
| `python/` | Базовые правила и verification |
| `zig/` | Правила, debugging и verification |

Swift-каталог содержит 39 rule-файлов:

```text
common(10) + performance(10) + networking(7) + platform(6) + best-practices(3) + security(3) = 39
```

Паки загружаются только по detection signal или требованию выбранного skill. Загруженные и
намеренно пропущенные паки объявляются в `SKILL CONTEXT`.

## Lifecycle hooks

### Claude2Home

| Hook | Событие | Назначение |
|---|---|---|
| `project-context.sh` | `SessionStart` | Загружает `.claude/PROJECT.md` или `PROJECT.md`, максимум 20 000 байт |
| `bash-guard.sh` | `PreToolUse` для Bash | `deny` для катастрофических и `ask` для необратимых команд; без `jq` безопасно деградирует в `ask` |
| `skill-lint.sh` | `PostToolUse` для Write/Edit | Проверяет изменённые instruction-файлы |
| `skill-context-lint.sh` | `Stop` | Проверяет `SKILL CONTEXT` и финальный `TRACE` у зарегистрированных skills |

### Codex2Home

`SessionStart` hook загружает `.codex/PROJECT.md` или `PROJECT.md` из корня Git-репозитория при
`startup`, `resume`, `clear` и `compact`. Содержимое ограничивается первыми 20 000 байтами и
добавляется как developer context. Остальные entries существующего `hooks.json` сохраняются.

## Project context

`PROJECT.md` хранит только проверенные проектные факты и правила: стек, команды, layout, CI,
глоссарий, ограничения и запретные пути. Runtime-specific файл имеет приоритет над общим:

- Claude Code: `.claude/PROJECT.md` → `PROJECT.md`;
- Codex: `.codex/PROJECT.md` → `PROJECT.md`.

Глубокие доменные инструкции должны жить в `KNOWLEDGE/<domain>/`, а не раздувать `PROJECT.md`.
Рекомендуемый предел самого project context — 200 строк; hook всё равно обрезает инъекцию после
20 000 байт.

## Проверка

Из корня репозитория:

```sh
sh Claude2Home/skills/skill-maintenance/scripts/skill-lint.sh Claude2Home
CODEX_HOME="$PWD/Codex2Home" sh Codex2Home/skills/skill-maintenance/scripts/skill-lint.sh Codex2Home

python3 Claude2Home/skills/task-lab/scripts/self_test.py
python3 Codex2Home/skills/task-lab/scripts/self_test.py

bash -n Claude2Home/init_claude.sh
bash -n Codex2Home/init_codex.sh
python3 -m json.tool Claude2Home/settings.json >/dev/null
python3 -m json.tool Codex2Home/hooks.json >/dev/null
python3 Codex2Home/scripts/merge_hooks.py --check Codex2Home/hooks.json Codex2Home/hooks.json
git diff --check
```

После изменения исходного дерева повторно запустите соответствующий installer. Не редактируйте
установленную копию как каноничный источник: следующая установка перезапишет поставляемые файлы.

## Обновление системы

При изменении общего контракта синхронизируйте обе runtime-копии, но не копируйте механизмы
буквально:

- пути `~/.claude/...` и `$CODEX_HOME/...` должны оставаться runtime-specific;
- Claude permissions/hooks живут в `settings.json`, Codex lifecycle entries — в `hooks.json`;
- Claude обнаруживает user skills напрямую, Codex installer дополнительно управляет symlink-links;
- workflow skill добавляется в `active-skills.txt` и `RESOLVER.md` обеих систем;
- direct-invocation skill может оставаться вне workflow-реестра, если это явно отражено в
  resolver и validation docs.
