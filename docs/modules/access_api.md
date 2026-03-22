# `access_api`

## Роль

`access_api` — это хозяин первичного browser read-model.

Он отвечает за:
- сборку главного task-list payload как канонического browser read-model;
- masked/full access policy на backend boundary;
- browser-safe DTO shape;
- выдачу `/info`-related operational reads.

## Главные входы

- primary browser read-model;
- operational info read;
- attachment read/view/download surface, которая нужна браузеру.

## Что модуль не должен делать

- хранить transport orchestration в роутере;
- тянуть внутренности `snapshot`, `attachments` или `rendering`;
- размывать ownership между несколькими handler-catalog слоями.

## Finish line

Если пользователь открыл интерфейс и получил стабильный browser read-model карточек и вложений, это finish line `access_api`.
