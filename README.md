#  Davit Capstone

An API with FASTAPI

## Setup
Install main dependencies

```shell
poetry install
```

Create `.env` file in `src` and write the `SQLite` database path in it as follows:
```
DB_URL={URL}
```

## Running API

### For running project with uvicorn

```shell
uvicorn src.app.main:app --host 0.0.0.0 --port 8000 
```

### Debug mode with reloading

```shell
uvicorn src.app.main:app --host 0.0.0.0 --port 8000 --reload
```



## Testing

Install testing dependencies

```bash
poetry install --with dev
```

For automatic test detection (-v for verbose -s for printing inside functions)

```shell
pytest -v -s 
```