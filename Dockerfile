FROM python:3.11-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy project files
COPY pyproject.toml .
COPY . .

# Install dependencies
RUN uv sync --no-dev

# Expose ports
EXPOSE 8000 8501

# Run both services
CMD ["uv", "run", "app.py"]
