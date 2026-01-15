# Dockerfile
FROM python:3.11-slim

# 1. Environment Configuration
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.7.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false

# Add Poetry to PATH
ENV PATH="$POETRY_HOME/bin:$PATH"

# 2. System Dependencies (Curl for Poetry, LibPQ for Postgres)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 3. Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# 4. Setup Workdir
WORKDIR /app

# 5. Install Dependencies (Cached Layer)
# We copy ONLY the definition files first. Docker caches this layer.
# If you change code but not dependencies, this step is skipped (faster builds).
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --only main

# 6. Copy Application Code
COPY . .

# 7. Security: Create non-root user
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# 8. Run
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "main:app"]