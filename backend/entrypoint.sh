#!/bin/sh
# Boot sequence: wait for the database, migrate, seed (only if empty), train the
# model, then serve. Idempotent — safe to run on every container start.
set -e

echo "==> Waiting for the database to accept connections..."
python - <<'PY'
import os, sys, time
from sqlalchemy import create_engine, text

url = os.environ.get("DATABASE_URL", "")
for attempt in range(40):
    try:
        with create_engine(url).connect() as conn:
            conn.execute(text("SELECT 1"))
        print("    database is ready")
        break
    except Exception as exc:  # noqa: BLE001
        print(f"    waiting ({attempt + 1})... {exc.__class__.__name__}")
        time.sleep(2)
else:
    sys.exit("Database never became reachable")
PY

echo "==> Applying migrations..."
alembic upgrade head

echo "==> Seeding synthetic data (if empty)..."
python -m app.seed.seed --if-empty

echo "==> Training the surplus model..."
python -m app.ml.train

echo "==> Starting API on :8000"
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
