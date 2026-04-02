# Task Manager

A small task manager built with clean architecture principles, SQLAlchemy, SQLite, and PostgreSQL.

## Structure

- `app/domain`: business entities and repository contracts
- `app/application`: use cases and application-specific errors
- `app/infrastructure/database`: SQLAlchemy engine, session management, and backend-specific adapters
- `app/infrastructure/persistence`: persistence adapters
- `app/presentation`: CLI entry point
- `app/bootstrap.py`: dependency wiring that can be reused in FastAPI

## Usage

```bash
python main.py --backend sqlite init-db
python main.py --backend sqlite add "Write tests" --description "Cover the critical flow"
python main.py --backend sqlite list
python main.py --backend sqlite complete <task-id>
python main.py --backend sqlite delete <task-id>
python main.py --backend sqlite migrate-json

python main.py --backend postgresql --postgres-dsn "postgresql+psycopg://user:pass@localhost:5432/task_manager" init-db
python main.py --backend postgresql --postgres-dsn "postgresql+psycopg://user:pass@localhost:5432/task_manager" list
```

## Run tests

```bash
python -m unittest discover -s tests
```
