# Шаг XX — {{STEP_TITLE}}

**Статус:** выполняется
**Дата:** {{DATE}}

## Запрос пользователя

{{USER_REQUEST}}

## Вопрос шага

{{QUESTION_WHOSE_ANSWER_CLOSES_THE_STEP}}

## Границы

**В шаге:** {{IN_SCOPE}}.

**Вне шага:** {{OUT_OF_SCOPE}}.

## Входы

{{DURABLE_INPUTS_WITHOUT_INBOX_LINKS}}

## Действия

1. {{EXECUTABLE_ACTION}}

## Критерий завершения

{{OBSERVABLE_DONE_CONDITION}}

## Карта вердиктов

Объявляется до выполнения, иначе критерий подгоняется под результат.

| Исход | Вывод | Действие после результата |
|---|---|---|
| {{OUTCOME}} | {{CONCLUSION}} | {{FOLLOW_UP}} |

## Записывает в

- `Steps/Step-XX-result.md`;
- {{OTHER_DURABLE_FILES_OR_NONE}}.
