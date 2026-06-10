# Contributing

## Local Setup

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
python -m app.ml.train
flask --app run init-db
python run.py
```

## Checks

```bash
black .
isort .
pytest -v
```

Use small branches with descriptive names, keep secrets out of commits, and open pull requests with a summary of behavior changes and tests run.

Report bugs with reproduction steps, expected behavior, actual behavior, and relevant logs without private journal text.

