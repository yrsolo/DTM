# `access_api`

## Роль

`access_api` — это хозяин основного browser-facing read-side.

Он отвечает за:
- сборку главного task-list payload;
- masked/full access policy на backend boundary;
- browser-safe DTO shape;
- выдачу `/info`-related operational reads.

## Главные входы

- browser task-list read;
- operational info read;
- attachment read/view/download surface, которая нужна браузеру.

## Что модуль не должен делать

- хранить transport orchestration в роутере;
- тянуть внутренности `snapshot`, `attachments` или `rendering`;
- размывать ownership между несколькими handler-catalog слоями.

## Finish line

Если пользователь открыл интерфейс и получил стабильный payload карточек и вложений, это finish line `access_api`.
