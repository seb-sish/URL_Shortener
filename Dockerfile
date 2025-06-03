# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Устанавливаем переменные окружения
ENV PATH="/app/.venv/bin:$PATH"

# Install the project into `/app`
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Копируем файлы зависимостей
COPY pyproject.toml uv.lock ./

# Синхронизируем зависимости
RUN uv sync --frozen --no-cache

# Копируем остальной код приложения
COPY . .

# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
CMD ["sh", "-c", "alembic upgrade head"]
    

# Reset the entrypoint, don't invoke `uv`
# ENTRYPOINT []

# Run the FastAPI application by default
# Uses `fastapi dev` to enable hot-reloading when the `watch` sync occurs
# Uses `--host 0.0.0.0` to allow access from outside the container
# CMD ["uv", "run", "fastapi", "dev", "--host", "0.0.0.0"]