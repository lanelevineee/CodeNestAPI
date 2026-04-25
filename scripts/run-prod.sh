#!/bin/bash

# Codensest Production Server Runner
# This script starts the production server with Gunicorn

set -e

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "🚀 Starting Codensest Production Server..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Load environment variables
if [ -f ".env" ]; then
    echo -e "${YELLOW}Loading environment variables from .env${NC}"
    export $(cat .env | grep -v '^#' | xargs)
fi

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo -e "${RED}Error: Python is not installed${NC}"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo -e "${YELLOW}Installing production dependencies...${NC}"
pip install -r requirements.txt gunicorn -q

# Run migrations
echo -e "${YELLOW}Running database migrations...${NC}"
python manage.py migrate --noinput

# Collect static files
echo -e "${YELLOW}Collecting static files...${NC}"
python manage.py collectstatic --noinput

# Create necessary directories
mkdir -p logs staticfiles media uploads

# Start Gunicorn
echo -e "${GREEN}✅ Starting Gunicorn production server on http://0.0.0.0:8000${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
exec gunicorn codensest.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --threads 2 \
    --worker-class gthread \
    --timeout 120 \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log \
    --capture-output \
    --enable-stdio-inheritance
