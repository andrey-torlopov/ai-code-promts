# Codex2Home

Переносимый шаблон глобальных инструкций, skills и knowledge packs для Codex.
Он заменяет копирование `Templates/Main` в каждый проект: Codex автоматически
загружает глобальный `AGENTS.md` из `CODEX_HOME` и добавляет проектные инструкции
поверх глобальных.

## Установка

```sh
./init_codex.sh
./init_codex.sh --dry-run
./init_codex.sh --target /path/to/codex-home
./init_codex.sh --target /path/to/codex-home --user-skills-dir /path/to/user-skills
```

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
- [CODEX_HOME и расположение состояния](https://developers.openai.com/codex/config-advanced).

## Карта payload

| В шаблоне | После установки | Стратегия |
|---|---|---|
| `AGENTS.md` | `<target>/AGENTS.md` | заменить с backup |
| `custom/` | `<target>/custom/` | заменить целиком с backup |
| `skills/<name>/` | `<target>/skills/<name>/` | заменить только поставляемый skill |
| link каждого skill | `<user-skills-dir>/<name>` | заменить только одноимённый путь с backup |

Установщик не изменяет `config.toml`, `auth.json`, историю, сессии, плагины,
логи, кэши и skills, которых нет в этом шаблоне.

Backup заменяемых путей создаётся в
`<target>/backups/codex2home-<timestamp>-<pid>/`. Флаг `--no-backup` отключает
backup явно.

## Структура

```text
<CODEX_HOME>/
├── AGENTS.md                 глобальный auto-loaded anchor
├── custom/
│   ├── CORE.md               SSOT глобальных правил
│   ├── RESOLVER.md           signal -> ровно один workflow skill
│   ├── COMMON.md             compatibility bridge
│   ├── _core/                validation, handoff, skill context, safety
│   └── KNOWLEDGE/            lazy-loaded доменные packs
└── skills/                   7 поставляемых workflow skills
```

## Порядок загрузки

```text
$CODEX_HOME/AGENTS.md
  -> $CODEX_HOME/custom/CORE.md
  -> $CODEX_HOME/custom/RESOLVER.md
  -> один выбранный skill
  -> только названные references/scripts/assets
  -> только релевантные custom/KNOWLEDGE packs
  -> более близкие project AGENTS.md overrides
```

`AGENTS.override.md` имеет приоритет над `AGENTS.md` на соответствующем уровне.
Не помещайте глобальный `AGENTS.override.md` рядом с установленным `AGENTS.md`,
если хотите, чтобы Codex загрузил этот шаблон: в глобальном scope Codex использует
только первый непустой файл.

## Проверка

```sh
bash -n init_codex.sh
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
