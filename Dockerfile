# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards

# Builder stage
# Use slim Python image for smaller footprint
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /install
COPY requirements-streamlit.txt requirements-minimal.txt ./
# Install build tools and Python dependencies, including Streamlit
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libsnappy-dev \
        libsdl2-dev \
        libsdl2-image-dev \
        libsdl2-mixer-dev \
        libsdl2-ttf-dev \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir --prefix=/install -r requirements-streamlit.txt

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
EXPOSE 8888

# Launch Streamlit UI explicitly
CMD ["streamlit", "run", "ui.py", "--server.port=8888", "--server.address=0.0.0.0"]