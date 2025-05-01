FROM node:20.11-slim as frontend-build

WORKDIR /app

# Copy package.json files
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY packages/frontend/package.json ./packages/frontend/

# Install pnpm
RUN npm install -g pnpm

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy frontend code
COPY packages/frontend/ ./packages/frontend/

# Build frontend
WORKDIR /app/packages/frontend
RUN pnpm build

FROM python:3.10.13-slim as backend-build

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FASTAPI_ENV=production \
    PYTHONPATH=/app/backend

# Install dependencies including curl for healthcheck
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY packages/backend/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend project
COPY packages/backend/ /app/backend/
WORKDIR /app/backend

# Install the project
RUN pip install -e .

# Create a symlink for the side_quest_py module to ensure imports work correctly
RUN mkdir -p /app/backend/side_quest_py && \
    ln -sf /app/backend/src/side_quest_py/* /app/backend/side_quest_py/

# Copy built frontend from the first stage
COPY --from=frontend-build /app/packages/frontend/dist /app/backend/src/side_quest_py/static

# Create entrypoint script
RUN echo '#!/bin/bash\nset -e\n\necho "Starting application in production mode..."\n\n# Set working directory\ncd /app/backend\n\n# Start the application with Gunicorn\nexec gunicorn -c gunicorn.conf.py src.main:app\n' > /app/entrypoint.sh \
    && chmod +x /app/entrypoint.sh

# Create non-root user and set proper permissions
RUN groupadd -r appuser && useradd -r -g appuser -d /app appuser \
    && chown -R appuser:appuser /app

# Use the non-root user
USER appuser

# Set working directory for the application
WORKDIR /app/backend

# Use the entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1
