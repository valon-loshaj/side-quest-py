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

# Set working directory for the application
WORKDIR /app/backend/src

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app"]

EXPOSE 5000
