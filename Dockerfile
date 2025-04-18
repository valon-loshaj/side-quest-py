FROM node:20-slim as frontend-build

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

FROM python:3.10-slim

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production

# Install dependencies including curl for healthcheck
RUN apt-get update && apt-get install -y curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY packages/backend/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend project
COPY packages/backend/ /app/backend/
WORKDIR /app/backend

# Install the project
RUN pip install -e .

# Copy built frontend from the first stage
COPY --from=frontend-build /app/packages/frontend/dist /app/backend/src/side_quest_py/static

# Copy entrypoint script
COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

# Set working directory for the application
WORKDIR /app

# Use the entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]

EXPOSE 5000
