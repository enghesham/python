# Task Manager

A small task manager built with clean architecture principles and the Python standard library.

## Structure

- `app/domain`: business entities and repository contracts
- `app/application`: use cases and application-specific errors
- `app/infrastructure/database`: SQLite connection and schema bootstrap
- `app/infrastructure/persistence`: persistence adapters
- `app/presentation`: CLI entry point
- `app/bootstrap.py`: dependency wiring that can be reused in FastAPI

## Usage

```bash
python main.py init-db
python main.py add "Write tests" --description "Cover the critical flow"
python main.py list
python main.py complete <task-id>
python main.py delete <task-id>
python main.py migrate-json
```

## Run tests

```bash
python -m unittest discover -s tests
```
