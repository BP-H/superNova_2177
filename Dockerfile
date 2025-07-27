# Builder stage
FROM python:3.12-slim AS builder
WORKDIR /install
COPY requirements.txt ./
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Final stage
FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /install /usr/local
COPY . /app
CMD ["uvicorn", "superNova_2177:app", "--host", "0.0.0.0", "--port", "8000"]
