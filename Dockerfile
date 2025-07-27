FROM python:3.12-slim AS builder
WORKDIR /install

# copy dependency files first to leverage Docker layer caching
COPY pyproject.toml requirements.txt ./
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

FROM python:3.12-slim
WORKDIR /app

# copy installed python packages from the builder stage
COPY --from=builder /install /usr/local

# copy application source code
COPY . .

# run the application as a non-root user
RUN useradd -m appuser
USER appuser

CMD ["uvicorn", "superNova_2177:app", "--host", "0.0.0.0", "--port", "8000"]
