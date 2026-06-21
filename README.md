# Booking Service

Backend-сервис для записи на встречи: REST API, Celery-воркер, PostgreSQL и Redis.

## Запуск

1. Скопируйте переменные окружения:

```bash
cp .env.example .env
```

2. Поднимите стек:

```bash
docker compose up --build
```

После старта доступны:

- API: http://localhost:8000
- PostgreSQL: localhost:5433
- Redis: localhost:6380

Миграции применяются отдельным одноразовым контейнером `migrate` перед стартом `app` и `celery`.

## Тесты

Тесты используют SQLite in-memory и Celery eager mode, Docker для запуска не нужен:

```bash
poetry install
make test
```

## API

| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/bookings` | Создать бронь (`name`, `datetime`, `service_type`), вернуть `id` |
| GET | `/bookings/{id}` | Получить бронь по id |
| GET | `/bookings` | Список броней (`status`, `offset`, `limit`) |
| DELETE | `/bookings/{id}` | Отменить бронь (только `pending`) |

Пример создания брони:

```bash
curl -X POST http://localhost:8000/bookings \
  -H 'Content-Type: application/json' \
  -d '{"name":"Alice","datetime":"2030-06-21T10:00:00","service_type":"consultation"}'
```

## Архитектурные решения (дизайн кода)

1. Знание о пагинации осталось в контроллере, так как это сугубо клиентская история, нам в репозитории достаточно ждать, что попросят срез
2. Репозиторий отвечает за генерацию инкремента, мутируя сущность. Осознанный компромисс между сложностью и надёжностью (явностью)
3. Осознано практически не прибегал к явным оркестраторам бизнес процессов (Application Services или Use Cases) из за простоты проекта
4. Осознано один docker-compose для работы и тестов (решил избыточным делать два в рамках тех. задания)
5. Осознано на уровне сервисов, использую настоящий репо (делать Fake посчитал избыточным в этой ситуации)
6. Осознано не тестировал функционал Retry
7. Осознано не делаю в репозитории update или delete_by так как это крайние меры, когда не хватает производительности. В остальных ситуациях лучше получить данные с помощью богатой модели проверить инварианты и только потом просить что-то удалять/обновлять
8. 

## Стек и поведение сервиса

- FastAPI + Pydantic для REST API, Celery + Redis для фонового подтверждения брони
- `domain` / `adapters`: сущности, порты, application service, use case `CreateBookingUseCase`, HTTP, persistence, Celery, stub-клиент
- `get_by` поверх `find_by` для выборки ровно одной записи: 0 — `BookingNotFound`, больше одного — `FindBookingMoreThanOne`
- Идемпотентность воркера: повторная обработка не-`pending` брони завершается без изменений
- Stub-клиент с ~15% сбоем, retry с экспоненциальным backoff, после исчерпания попыток — статус `failed`
- JSON-логирование, rate limiting на `POST /bookings` (10 req/min с IP), `Makefile` (`dev`, `test`, `lint`)
- `POST /bookings`: новая бронь — `201` + `{"id": ...}`, дубликат — `200` + `{"id": ...}` без повторной постановки задачи в очередь
