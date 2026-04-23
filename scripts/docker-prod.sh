#!/bin/bash

# Codensest Docker Production Runner
# This script starts the production environment using Docker Compose

set -e

echo "🐳 Starting Codensest Docker Production Environment..."

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

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${RED}Error: .env file not found${NC}"
    echo -e "${YELLOW}Please create .env file from .env.example and configure it${NC}"
    exit 1
fi

# Generate secret key if not set
if [ -z "$SECRET_KEY" ] || [ "$SECRET_KEY" = "your-super-secret-key-change-this-in-production-use-openssl-rand-hex-32" ]; then
    echo -e "${YELLOW}Generating secure SECRET_KEY...${NC}"
    export SECRET_KEY=$(openssl rand -hex 32)
fi

# Create SSL directory and generate self-signed cert for development
if [ ! -f "ssl/cert.pem" ] || [ ! -f "ssl/key.pem" ]; then
    echo -e "${YELLOW}Generating self-signed SSL certificate...${NC}"
    mkdir -p ssl
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout ssl/key.pem \
        -out ssl/cert.pem \
        -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost" 2>/dev/null
fi

# Build and start services
echo -e "${YELLOW}Building and starting production services...${NC}"
$COMPOSE_CMD up --build -d

# Wait for services to be ready
echo -e "${YELLOW}Waiting for services to be ready...${NC}"
sleep 15

# Show status
echo -e "${GREEN}✅ Production environment started!${NC}"
echo -e "${YELLOW}Access the application at: https://localhost${NC}"
echo -e "${YELLOW}HTTP redirects to HTTPS automatically${NC}"
echo ""
echo -e "${YELLOW}Useful commands:${NC}"
echo -e "  Stop: ./scripts/docker-prod.sh stop"
echo -e "  Logs: ./scripts/docker-prod.sh logs"
echo -e "  Restart: ./scripts/docker-prod.sh restart"
echo -e "  Status: ./scripts/docker-prod.sh status"
