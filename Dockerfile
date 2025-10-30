# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# System deps for reportlab (PDF) and general build
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libjpeg62-turbo-dev \
    zlib1g-dev \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r /app/requirements.txt

# Copy project
COPY . /app

# Expose FastAPI port
EXPOSE 9000

# Default environment (override in docker run or compose)
# ENV OPENAI_API_KEY=...
# ENV DATABASE_URL=sqlite:///./glow_haven.db
# ENV API_BASE_URL=http://localhost:9000/api

# Run FastAPI on 0.0.0.0:9000
CMD ["uvicorn", "app.main:app", "--port", "9000"]
