FROM python:3.12-slim as base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Test stage: run tests before production build
FROM base as test

COPY . .

RUN cd promo && python -m pytest ../tests/ -v

# Production stage: only built if tests pass
FROM base as production

RUN useradd --create-home appuser

COPY . .
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

WORKDIR /app/promo

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "promo.asgi:application", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120"]
