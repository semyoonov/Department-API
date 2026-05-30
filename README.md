# Тестовое задание Junior Python developer. 
*API организационной структуры*

## Запуск

```bash
docker-compose up -d --build
```

## Архитектура

```
test_task/
├── app/
│   ├── api/
│   │   ├── methods.py      # Эндпоинты API
│   │   └── schemas.py      # Pydantic-схемы (входные данные)
│   ├── database/
│   │   └── database.py     # Подключение к БД
│   ├── models.py           # ORM-модели (Department, Employee)
│   └── main.py             # Точка входа FastAPI
├── tests/
│   └── test.py             # Тесты API
├── alembic/                # Миграции
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```
API: `http://localhost:8000`
Документация: `http://localhost:8000/docs`


## Технологии

- Python 3.12
- FastAPI
- SQLAlchemy (ORM)
- PostgreSQL 15
- Alembic (миграции)
- Docker, docker-compose

## Методы API

| Метод | Описание |
|---|---|
| `POST /departments/` | Создать подразделение |
| `GET /departments/{id}` | Получить подразделение с деревом |
| `PATCH /departments/{id}` | Обновить подразделение |
| `DELETE /departments/{id}` | Удалить подразделение |
| `POST /departments/{id}/employees/` | Создать сотрудника |

## Тесты

```bash
docker-compose exec api pytest tests/test.py -v
```