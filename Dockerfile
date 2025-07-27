# Builder stage
# Use slim Python image for smaller footprint
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /install
COPY requirements.txt requirements.lock ./
RUN if [ -f requirements.lock ]; then \
        pip install --no-cache-dir --prefix=/install -r requirements.lock; \
    else \
        pip install --no-cache-dir --prefix=/install -r requirements.txt; \
    fi

# Final stage
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Create non-root user for security
RUN adduser --disabled-password --gecos "" appuser

COPY --from=builder /install /usr/local
COPY . /app

# Change ownership to the non-root user
RUN chown -R appuser:appuser /app

USER appuser

# Expose FastAPI default port
EXPOSE 8000

CMD ["uvicorn", "superNova_2177:app", "--host", "0.0.0.0", "--port", "8000"]
