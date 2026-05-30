# SecondPlate API — Python 3.11 (pinned for stable scientific-stack wheels).
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# curl is used by the container healthcheck.
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Normalise line endings so the entrypoint runs on any host, then make it executable.
RUN sed -i 's/\r$//' entrypoint.sh && chmod +x entrypoint.sh

# Pre-train the surplus model at build time (against a throwaway SQLite seed) so
# runtime cold starts serve immediately instead of retraining under a throttled
# free-tier CPU. The baked artifact lives in app/ml/artifacts/.
RUN DATABASE_URL="sqlite:///./_build.db" sh -c \
    "alembic upgrade head && python -m app.seed.seed && python -m app.ml.train" \
    && rm -f _build.db

EXPOSE 8000

CMD ["./entrypoint.sh"]
