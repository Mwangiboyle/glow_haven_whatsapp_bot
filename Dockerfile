
# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# System dependencies (for PDF generation, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libjpeg62-turbo-dev \
    zlib1g-dev \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency file
COPY requirements.txt .

# Install dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy application code
COPY . .

# Copy environment variables file
COPY .env /app/.env

# Expose FastAPI port
EXPOSE 9000

# Load .env automatically (using python-dotenv)
# and run the app
CMD ["bash", "-c", "source /app/.env && uvicorn app.main:app --host 0.0.0.0 --port 9000"]

