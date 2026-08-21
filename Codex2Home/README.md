# Codex2Home

Переносимый шаблон глобальных инструкций, lifecycle hooks, skills и knowledge packs для Codex.
Установка через `init_codex.sh` — единственный поддерживаемый способ развернуть эту систему;
старый project-level маршрут (`Templates/Main` + `init_ai.sh`) архивирован и использоваться не
должен. Codex автоматически загружает глобальный `AGENTS.md` из `CODEX_HOME` и добавляет
проектные инструкции поверх глобальных.

## Установка

```sh
./init_codex.sh
./init_codex.sh --dry-run
./init_codex.sh --target /path/to/codex-home
./init_codex.sh --target /path/to/codex-home --user-skills-dir /path/to/user-skills
```

Для безопасного слияния существующего `hooks.json` установщику требуется Python 3.

Целевой каталог выбирается в следующем порядке:

1. `--target DIR`;
2. переменная `CODEX_HOME`;
3. `$HOME/.codex`.

Каталог compatibility-links для нативного discovery skills выбирается так:

1. `--user-skills-dir DIR`;
2. переменная `CODEX_USER_SKILLS_DIR`;
3. `$HOME/.agents/skills`.

Для стандартного Codex оставляйте `$HOME/.agents/skills`: произвольное значение
`--user-skills-dir` предназначено для изолированных тестов или рантайма, который
явно сканирует этот каталог. Эта переменная принадлежит установщику; Codex не
обязан читать `CODEX_USER_SKILLS_DIR`.

При установке в нестандартный каталог запускайте Codex с тем же `CODEX_HOME`:

```sh
export CODEX_HOME=/path/to/codex-home
codex
```

После первой установки или изменения hook откройте `/hooks` в Codex и подтвердите
точное определение `project-context`. Codex привязывает доверие к hash определения,
поэтому изменённый hook не выполняется до повторного review.

## PROJECT.md на старте сессии

`SessionStart` hook ищет контекст в корне Git-репозитория в таком порядке:

1. `.codex/PROJECT.md` — явный Codex-specific override;
2. `PROJECT.md` — общий проектный контекст.

Найденный файл добавляется как developer context при `startup`, `resume`, `clear` и
`compact`. Размер автоматически ограничивается первыми 20 000 байтами. Если файла
нет, hook завершается без вывода и не меняет глобальный runtime.

## Почему используются symlink для skills

`CODEX_HOME` управляет `AGENTS.md`, конфигурацией и локальным состоянием Codex.
Актуальный документированный пользовательский scope для нативных skills —
`$HOME/.agents/skills`. Локально проверенный `codex-cli 0.148.0-alpha.15` также
обнаруживает `<CODEX_HOME>/skills` напрямую; links сохраняют совместимость с
документированным scope и другими актуальными клиентами.
Поэтому каноничная копия каждого поставляемого skill хранится в
`<target>/skills/<name>`, а установщик создаёт управляемый symlink:

```text
$HOME/.agents/skills/<name> -> <target>/skills/<name>
```

Codex поддерживает symlink-каталоги skills. Для изолированного копирования без
изменения discovery-каталога используйте `--no-skill-links`.

Контракт проверен по официальной документации OpenAI:

- [глобальные и проектные AGENTS.md](https://developers.openai.com/codex/guides/agents-md);
- [создание и discovery skills](https://developers.openai.com/codex/skills);
- [lifecycle hooks и trust review](https://learn.chatgpt.com/codex/hooks);
- [CODEX_HOME и расположение состояния](https://developers.openai.com/codex/config-advanced).

## Карта payload

| В шаблоне | После установки | Стратегия |
|---|---|---|
| `AGENTS.md` | `<target>/AGENTS.md` | заменить с backup |
| `hooks.json` | `<target>/hooks.json` | заменить только управляемый `project-context` entry, остальные сохранить |
| `hooks/project-context.sh` | `<target>/hooks/project-context.sh` | заменить с backup |
| `custom/` | `<target>/custom/` | заменить целиком с backup |
| `skills/<name>/` | `<target>/skills/<name>/` | заменить только поставляемый skill |
| link каждого skill | `<user-skills-dir>/<name>` | заменить только одноимённый путь с backup |

Установщик не изменяет `config.toml`, `auth.json`, историю, сессии, плагины,
логи, кэши, посторонние hook handlers и skills, которых нет в этом шаблоне.
Каталог `scripts/` используется только самим установщиком и в `<target>` не копируется.

Backup заменяемых путей создаётся в
`<target>/backups/codex2home-<timestamp>-<pid>/`. Флаг `--no-backup` отключает
backup явно.

## Структура

```text
<CODEX_HOME>/
├── AGENTS.md                 глобальный auto-loaded anchor
├── hooks.json                SessionStart lifecycle configuration
├── hooks/
│   └── project-context.sh    безопасная загрузка PROJECT.md
├── custom/
│   ├── CORE.md               SSOT глобальных правил
│   ├── RESOLVER.md           signal -> ровно один workflow skill
│   ├── COMMON.md             compatibility bridge
│   ├── _core/                validation, handoff, skill context, safety
│   └── KNOWLEDGE/            lazy-loaded доменные packs
└── skills/                   7 workflow skills + task-lab (state layer) + graphify
```

## Порядок загрузки

```text
$CODEX_HOME/AGENTS.md
  -> $CODEX_HOME/custom/CORE.md
  -> $CODEX_HOME/custom/RESOLVER.md
  -> поставляемый task-lab, если запрос содержит TaskID или task-folder
  -> PROJECT.md или .codex/PROJECT.md через SessionStart
  -> один выбранный skill
  -> только названные references/scripts/assets
  -> только релевантные custom/KNOWLEDGE packs
  -> более близкие project AGENTS.md overrides
```

`task-lab` поставляется и версионируется вместе с системой, но остаётся state layer, а не восьмым
workflow skill. При наличии TaskID или пути task-folder `RESOLVER.md` сначала восстанавливает
durable task state, после чего обычный workflow skill остаётся единственным владельцем
deliverable. При неполной установке без `task-lab` routing деградирует безопасно: работает без
state layer и объявляет `TASK: none`.

`graphify` тоже поставляется вместе с шаблоном, но не входит в workflow-реестр: он вызывается
напрямую по `/graphify` или для запросов к уже построенному `graphify-out/`.

`AGENTS.override.md` имеет приоритет над `AGENTS.md` на соответствующем уровне.
Не помещайте глобальный `AGENTS.override.md` рядом с установленным `AGENTS.md`,
если хотите, чтобы Codex загрузил этот шаблон: в глобальном scope Codex использует
только первый непустой файл.

## Проверка

```sh
bash -n init_codex.sh
sh -n hooks/project-context.sh
python3 -m json.tool hooks.json >/dev/null
python3 scripts/merge_hooks.py --check hooks.json /path/to/existing/hooks.json
CODEX_HOME="$PWD" sh skills/skill-maintenance/scripts/skill-lint.sh "$PWD"
```

После изменения source tree повторно запустите `init_codex.sh`. Редактирование
установленной копии напрямую приводит к расхождению с шаблоном и будет
перезаписано следующей установкой.

## Добавление skill

1. Создайте `skills/<name>/SKILL.md` с корректным YAML frontmatter.
2. Добавьте имя в `custom/_core/active-skills.txt`.
3. Добавьте маршрут в `custom/RESOLVER.md`.
4. Запустите validator.
5. Повторно выполните `init_codex.sh`; новый symlink будет создан автоматически.
