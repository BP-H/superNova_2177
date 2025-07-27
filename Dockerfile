# Builder stage used for installing dependencies
FROM python:3.12-slim AS builder
ENV PYTHONDONTWRITEBYTECODE=1
WORKDIR /install
COPY requirements.lock ./
RUN pip install --no-cache-dir --prefix=/install -r requirements.lock

# Final stage
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1
RUN groupadd -r app && useradd -r -g app app
WORKDIR /app
COPY --from=builder /install /usr/local
COPY . /app
USER app
CMD ["uvicorn", "superNova_2177:app", "--host", "0.0.0.0", "--port", "8000"]
