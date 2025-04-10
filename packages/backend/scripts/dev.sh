#!/bin/bash

# Stop any existing containers
docker-compose -f docker-compose.dev.yml down

# Build and start development containers
docker-compose -f docker-compose.dev.yml up --build

# To stop, use Ctrl+C
