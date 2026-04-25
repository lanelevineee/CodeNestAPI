#!/bin/bash

# Codensest Docker Development Runner
# This script starts the development environment using Docker Compose

set -e

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "🐳 Starting Codensest Docker Development Environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is not installed${NC}"
    exit 1
fi

# Determine which docker-compose command to use
if docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env file from .env.example...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}Please update .env with your configuration${NC}"
fi

# Build and start services
echo -e "${YELLOW}Building and starting services...${NC}"
$COMPOSE_CMD -f docker-compose.dev.yml up --build -d

# Wait for services to be ready
echo -e "${YELLOW}Waiting for services to be ready...${NC}"
sleep 10

# Show status
echo -e "${GREEN}✅ Development environment started!${NC}"
echo -e "${YELLOW}Access the application at: http://localhost:8000${NC}"
echo -e "${YELLOW}Database: localhost:5432${NC}"
echo -e "${YELLOW}Redis: localhost:6379${NC}"
echo ""
echo -e "${YELLOW}Useful commands:${NC}"
echo -e "  Stop: ./scripts/docker-dev.sh stop"
echo -e "  Logs: ./scripts/docker-dev.sh logs"
echo -e "  Restart: ./scripts/docker-dev.sh restart"
echo -e "  Shell: ./scripts/docker-dev.sh shell"
