# Wallet API

Асинхронный сервис для управления кошельками с балансом. Поддерживает пополнение, снятие средств и проверку баланса.

---

## Быстрый старт

Запустить PostgreSQL через Docker:  
```
docker run --name wallet_postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres
docker exec -it wallet_postgres psql -U postgres -c "CREATE DATABASE wallet_db"
```
Запустить приложение:  
```
docker-compose up --build
```
API будет доступно по адресу: http://localhost:8000/docs

---

## Тестовый кошелёк

Для тестирования нужно создать кошелек вручную. пример: 
```
docker exec -it wallet_postgres psql -U postgres -d wallet_db -c "INSERT INTO wallets (id, balance) VALUES ('123e4567-e89b-12d3-a456-426614174000', 100);"
```
UUID кошелька будет: 123e4567-e89b-12d3-a456-426614174000

---

## API Эндпоинты

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| GET | /api/v1/wallets/{wallet_uuid} | Получить баланс кошелька |
| POST | /api/v1/wallets/{wallet_uuid}/operation | пополнить или снять средсттва |

### Пример запроса на пополнение
```
{
  "operation_type": "DEPOSIT",
  "amount": 50
}
```
### Пример запроса на снятие
```
{
  "operation_type": "WITHDRAW",
  "amount": 30
}
```
---

## Запуск тестов

Тесты необходимо запускать по одному, чтобы избежать конфликтов:
```
poetry run pytest tests/test_wallet.py::test_get_wallet -v
poetry run pytest tests/test_wallet.py::test_wallet_deposit -v
poetry run pytest tests/test_wallet.py::test_wallet_withdraw -v
poetry run pytest tests/test_wallet.py::test_wallet_withdraw_insufficient_funds -v
poetry run pytest tests/test_wallet.py::test_wallet_invalid_operation -v
poetry run pytest tests/test_wallet.py::test_wallet_transaction -v
```
Результаты тестов:
```
tests/test_wallet.py::test_get_wallet PASSED
tests/test_wallet.py::test_wallet_deposit PASSED
tests/test_wallet.py::test_wallet_withdraw PASSED
tests/test_wallet.py::test_wallet_withdraw_insufficient_funds PASSED
tests/test_wallet.py::test_wallet_invalid_operation PASSED
tests/test_wallet.py::test_wallet_transaction PASSED
```
При запуске всех тестов сразу появляется ошибка - не знаю как исправить, поэтмоу запускал по одному
```
FAILED tests/test_wallet.py::test_wallet_transaction - sqlalchemy.exc.InterfaceError: (sqlalchemy.dialects.postgresql.asyncpg.InterfaceError) <class 'asyncpg.exceptions._base.InterfaceError'>: cannot perform operation: another operation is in progress [SQL: INSERT INTO wallets (id, balance) VALUES ($1::UUID, $2::NUMERIC(10, 2))]
```

---

## Структура проекта
```
wallet_api/
├── app/
│   ├── api/
│   │   └── routes/
│   │       └── wallets.py          # Эндпоинты для работы с кошельками
│   ├── core/
│   │   └── config.py               # Настройки из .env
│   ├── db/
│   │   └── database.py             # Подключение к PostgreSQL
│   ├── models/
│   │   └── wallet.py               # Модель Wallet (UUID, balance)
│   ├── schemas/
│   │   └── wallet.py               # Pydantic схемы (WalletResponse, OperationRequest)
│   └── main.py                     # Точка входа FastAPI
├── alembic/                        # Миграции Alembic
├── tests/
│   └── test_wallet.py              # Тесты эндпоинтов
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── poetry.lock
└── README.md
```
---

## Технологии
- Python 3.12
- FastAPI 
- PostgreSQL + SQLAlchemy async
- Alembic
- Docker / Docker Compose
- Pytest
