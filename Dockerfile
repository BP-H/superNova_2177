FROM python:3.12-slim

WORKDIR /app

# Install dependencies first
COPY requirements.txt pyproject.toml ./
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir .

# Copy project files
COPY . .

EXPOSE 8000

CMD ["uvicorn", "superNova_2177:app", "--host", "0.0.0.0", "--port", "8000"]
