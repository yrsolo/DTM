# `telegram_interaction`

## Роль

`telegram_interaction` владеет Telegram intake и reply-related flows:
- webhook intake;
- update parsing;
- command mapping;
- group query reply execution.

## Статус в системе

Это рабочий, но reserve-capability модуль.

Он должен оставаться:
- изолированным;
- low-maintenance;
- не влияющим на архитектурный центр системы сильнее, чем это нужно текущим сценариям.

## Что модуль не должен делать

- превращаться в главный product contour;
- тянуть ownership reminder или browser read-side на себя;
- исполнять тяжёлые действия inline в webhook path.
