# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards

# Builder stage
# Use slim Python image for smaller footprint
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /install
COPY requirements.txt ./
# Install build tools and Python dependencies
# SDL libraries are omitted unless requirements-optional.txt is used
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libsnappy-dev \
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

# Expose Streamlit port
EXPOSE 8501

# Launch Streamlit UI explicitly
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]