#!/bin/sh
# PreToolUse(Bash) guard.
#
# Смысл: разрешения в settings.json сопоставляются по ПРЕФИКСУ команды, поэтому
# `cd x && rm -rf y` или `git -C repo reset --hard` мимо них проходят. Хук получает
# всю строку целиком и решает сам:
#   deny — катастрофическое, не делаем никогда;
#   ask  — необратимое, но легитимное: показываем промпт;
#   (молчание) — обычная работа, решают правила из settings.json.
set -u

input=$(cat)

if ! command -v jq >/dev/null 2>&1; then
  printf '%s\n' '{"systemMessage":"bash-guard: jq не найден, защита отключена"}'
  exit 0
fi

cmd=$(printf '%s' "$input" | jq -r '.tool_input.command // .tool_input.cmd // ""' | tr '\n\t' '  ')
[ -n "$cmd" ] || exit 0

emit() {
  jq -n --arg d "$1" --arg r "$2" \
    '{hookSpecificOutput:{hookEventName:"PreToolUse",permissionDecision:$d,permissionDecisionReason:$r}}'
  exit 0
}

# Начало командного слова: старт строки или разделитель (;, &&, ||, |, подстановка).
W='(^|[;&|(`]|[[:space:]])'

match()  { printf '%s' "$cmd" | grep -Eq  "$1"; }
matchi() { printf '%s' "$cmd" | grep -Eqi "$1"; }

# Исключение: `rm` строго внутри временного каталога сессии — рутина, не спрашиваем.
rm_only_tmp() {
  case "$cmd" in
    *'&&'*|*';'*|*'|'*|*'$('*|*'`'*|*'>'*) return 1 ;;
  esac
  # shellcheck disable=SC2086
  set -- $cmd
  [ "${1:-}" = "rm" ] || return 1
  shift
  hit=0
  for a in "$@"; do
    case "$a" in
      -*) continue ;;
      /private/tmp/claude-*|/tmp/claude-*) hit=$((hit + 1)) ;;
      *) return 1 ;;
    esac
  done
  [ "$hit" -gt 0 ]
}

# ---------------------------------------------------------------- HARD DENY --
match "${W}sudo([[:space:]]|\$)" \
  && emit deny "sudo запрещён: изменения с правами root необратимы и вне контроля проекта."

match "${W}rm[[:space:]]+(-[^[:space:]]+[[:space:]]+)*(/|~|\\\$HOME|\\\$\{HOME\})([[:space:]/]|\$)" \
  && emit deny "rm по корню/домашнему каталогу запрещён."

match "${W}rm[^;&|]*[[:space:]](\.git|\.claude)([[:space:]/]|\$)" \
  && emit deny "Удаление .git/.claude запрещено: теряется история и конфигурация."

match "${W}(mkfs|diskutil[[:space:]]+(erase|reformat|partitionDisk))" \
  && emit deny "Форматирование диска запрещено."

match "${W}dd[[:space:]][^;&|]*of=/dev/" \
  && emit deny "dd с записью в /dev/ запрещён."

match '>[[:space:]]*/dev/(disk|rdisk|sd[a-z])' \
  && emit deny "Запись в блочное устройство запрещена."

match ':\([[:space:]]*\)[[:space:]]*\{' \
  && emit deny "Похоже на fork-бомбу."

match "${W}(shutdown|reboot|halt)([[:space:]]|\$)" \
  && emit deny "Выключение/перезагрузка машины запрещены."

match "${W}(curl|wget)[^;&|]*\|[[:space:]]*(sudo[[:space:]]+)?(sh|bash|zsh)([[:space:]]|\$)" \
  && emit deny "curl|sh — исполнение скачанного кода без проверки запрещено."

match "${W}git([[:space:]]+-[^[:space:]]+[[:space:]]+[^[:space:]]+)*[[:space:]]+push[^;&|]*(--force([[:space:]]|=|\$)|[[:space:]]-f([[:space:]]|\$)|--delete|--mirror|[[:space:]]:refs/)" \
  && emit deny "force/delete push перезаписывает удалённую историю — запрещено."

match "${W}git[^;&|]*(filter-branch|filter-repo)" \
  && emit deny "Перезапись истории репозитория запрещена."

match "${W}shred([[:space:]]|\$)" \
  && emit deny "shred уничтожает данные без восстановления."

match "${W}chmod[[:space:]]+(-[^[:space:]]+[[:space:]]+)*777[[:space:]]+/([[:space:]]|\$)" \
  && emit deny "chmod 777 на корне запрещён."

# ---------------------------------------------------------------------- ASK --
if ! rm_only_tmp; then
  match "${W}(rm|rmdir|unlink)([[:space:]]|\$)" \
    && emit ask "Удаление файлов — необратимо. Проверьте пути."
fi

match "${W}find[^;&|]*(-delete|-exec[[:space:]]+rm)" \
  && emit ask "find с удалением — необратимо."

match "${W}xargs[^;&|]*[[:space:]]rm([[:space:]]|\$)" \
  && emit ask "xargs rm — массовое удаление."

match "${W}git[^;&|]*reset[^;&|]*(--hard|--merge|--keep)" \
  && emit ask "git reset --hard уничтожает незакоммиченные изменения."

match "${W}git[^;&|]*(clean([[:space:]]|\$)|checkout[[:space:]]+--|checkout[[:space:]]+\.([[:space:]]|\$)|restore([[:space:]]|\$))" \
  && emit ask "Откат рабочего дерева уничтожает незакоммиченные изменения."

match "${W}git[^;&|]*(commit[^;&|]*--amend|rebase([[:space:]]|\$)|branch[[:space:]]+-D|branch[[:space:]]+-d|tag[[:space:]]+-d|update-ref[[:space:]]+-d)" \
  && emit ask "Операция переписывает или удаляет git-историю."

match "${W}git[^;&|]*stash[[:space:]]+(drop|clear|pop)" \
  && emit ask "Удаление stash — восстановить нельзя."

match "${W}git[^;&|]*(reflog[[:space:]]+expire|gc[^;&|]*--prune|worktree[[:space:]]+remove|submodule[[:space:]]+deinit|remote[[:space:]]+(rm|remove|set-url))" \
  && emit ask "Операция необратимо меняет состояние репозитория."

match "${W}git([[:space:]]+-[^[:space:]]+[[:space:]]+[^[:space:]]+)*[[:space:]]+push([[:space:]]|\$)" \
  && emit ask "push публикует изменения наружу."

match '>[[:space:]]*/(etc|usr|bin|sbin|System|Library|private/etc)/' \
  && emit ask "Запись в системный каталог."

match "${W}(chown|chmod)[[:space:]]+-R" \
  && emit ask "Рекурсивная смена прав/владельца."

match "${W}launchctl[[:space:]]+(unload|remove|bootout)" \
  && emit ask "Выгрузка системного сервиса."

match "${W}defaults[[:space:]]+(delete|write)" \
  && emit ask "Изменение системных настроек macOS."

match "${W}(brew[[:space:]]+(uninstall|remove|cleanup)|(npm|pnpm|yarn)[[:space:]]+uninstall[^;&|]*-g|(pip|pip3)[[:space:]]+uninstall|gem[[:space:]]+uninstall)" \
  && emit ask "Удаление установленного пакета."

match "${W}((npm|pnpm|yarn)[[:space:]]+publish|pod[[:space:]]+trunk[[:space:]]+push|xcrun[[:space:]]+(altool|notarytool)|fastlane[[:space:]]+(deliver|pilot|release|beta|deploy))" \
  && emit ask "Публикация артефакта наружу — отменить нельзя."

match "${W}gh[[:space:]]+(release|repo[[:space:]]+delete|pr[[:space:]]+(merge|close)|issue[[:space:]]+close)" \
  && emit ask "Действие меняет состояние на GitHub."

match "${W}xcrun[[:space:]]+simctl[[:space:]]+(erase|delete)" \
  && emit ask "Стирание/удаление симулятора."

match "${W}(docker[[:space:]]+(rm|rmi|system[[:space:]]+prune|volume[[:space:]]+rm)|kubectl[[:space:]]+delete|terraform[[:space:]]+(apply|destroy))" \
  && emit ask "Удаление инфраструктурного ресурса."

match "${W}aws[^;&|]*(s3[[:space:]]+rm|--delete)" \
  && emit ask "Удаление объектов в облаке."

match "${W}truncate[[:space:]]+-s" \
  && emit ask "Обрезание файла."

matchi '(drop|truncate)[[:space:]]+table' \
  && emit ask "SQL DROP/TRUNCATE TABLE."

match "${W}(curl|wget)[^;&|]*(-X[[:space:]]*(DELETE|PUT)|--request[[:space:]]*DELETE)" \
  && emit ask "Деструктивный HTTP-запрос."

exit 0
