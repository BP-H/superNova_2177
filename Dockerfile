# Builder stage
# Use slim Python image for smaller footprint
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /install
COPY requirements.txt ./
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libsnappy-dev \
        libsdl2-dev \
        libsdl2-image-dev \
        libsdl2-mixer-dev \
        libsdl2-ttf-dev \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir --prefix=/install -r requirements.txt

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
