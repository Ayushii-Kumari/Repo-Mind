# Stage 1: Build React frontend 
FROM node:20-slim AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build
# Output is now in /app/frontend/dist

# Stage 2: Python backend 
FROM python:3.11-slim
WORKDIR /app

# Install uv
RUN pip install uv

# Copy Python project files
COPY pyproject.toml .
COPY . .

# Install Python deps (--system = no venv needed inside Docker)
RUN uv sync

# Copy built React files from stage 1
COPY --from=frontend-build /app/frontend/dist ./frontend/dist

# Expose Render port
EXPOSE 10000

# Start FastAPI
CMD ["uv", "run", "--system", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "10000"]