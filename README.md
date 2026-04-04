# Contacts REST API

FastAPI + SQLAlchemy + PostgreSQL: CRUD для контактів, пошук (query), дні народження на найближчі 7 днів.

## Запуск

1. Створіть базу в PostgreSQL.
2. Скопіюйте `.env.example` у `.env` і задайте `DATABASE_URL`.
3. Встановіть залежності та запустіть сервер:

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Документація OpenAPI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Ендпоінти

- `POST /contacts` — створити контакт
- `GET /contacts` — список (опційно: `first_name`, `last_name`, `email`, `skip`, `limit`)
- `GET /contacts/{id}` — один контакт
- `PATCH /contacts/{id}` — оновити
- `DELETE /contacts/{id}` — видалити
- `GET /contacts/birthdays/upcoming` — дні народження у найближчі 7 днів
