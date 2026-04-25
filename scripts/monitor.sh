#!/bin/bash

# Codensest Server Monitoring Script
# This script provides server status, logs, and management capabilities

set -e

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "📊 Codensest Server Monitor"
echo "=========================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to show help
show_help() {
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  status     - Show server status (default)"
    echo "  logs       - Show recent logs"
    echo "  health     - Check application health"
    echo "  db         - Database status and stats"
    echo "  redis      - Redis status"
    echo "  docker     - Docker containers status"
    echo "  processes  - Running Python processes"
    echo "  disk       - Disk usage"
    echo "  memory     - Memory usage"
    echo "  all        - Show all information"
    echo "  help       - Show this help message"
    echo ""
}

# Function to check application health
check_health() {
    echo -e "${BLUE}Application Health:${NC}"
    if curl -s -f http://localhost:8000/health/ > /dev/null 2>&1; then
        echo -e "  ${GREEN}✓ Application is healthy${NC}"
        curl -s http://localhost:8000/health/ | python -m json.tool 2>/dev/null || echo "  Response received"
    else
        echo -e "  ${RED}✗ Application is not responding${NC}"
    fi
    echo ""
}

# Function to show server status
show_status() {
    echo -e "${BLUE}Server Status:${NC}"
    
    # Check if server is running
    if pgrep -f "gunicorn|runserver|manage.py" > /dev/null; then
        echo -e "  ${GREEN}✓ Django server is running${NC}"
        pgrep -af "gunicorn|runserver|manage.py" | head -5 | sed 's/^/    /'
    else
        echo -e "  ${YELLOW}⚠ Django server is not running${NC}"
    fi
    
    # Check ports
    echo ""
    echo -e "${BLUE}Listening Ports:${NC}"
    if command -v netstat &> /dev/null; then
        netstat -tlnp 2>/dev/null | grep -E ":(8000|5432|6379|80|443)" | sed 's/^/  /' || echo "  No relevant ports found"
    elif command -v ss &> /dev/null; then
        ss -tlnp 2>/dev/null | grep -E ":(8000|5432|6379|80|443)" | sed 's/^/  /' || echo "  No relevant ports found"
    else
        echo "  Network tools not available"
    fi
    echo ""
}

# Function to show logs
show_logs() {
    echo -e "${BLUE}Recent Logs:${NC}"
    if [ -d "logs" ] && [ "$(ls -A logs 2>/dev/null)" ]; then
        echo "  Last 20 lines from error.log:"
        tail -20 logs/error.log 2>/dev/null | sed 's/^/  /' || echo "  No error.log found"
        echo ""
        echo "  Last 20 lines from access.log:"
        tail -20 logs/access.log 2>/dev/null | sed 's/^/  /' || echo "  No access.log found"
    else
        echo "  No logs directory found"
    fi
    echo ""
}

# Function to check database status
check_db() {
    echo -e "${BLUE}Database Status:${NC}"
    if command -v psql &> /dev/null && [ -n "$DATABASE_URL" ]; then
        psql "$DATABASE_URL" -c "SELECT version();" 2>/dev/null | head -5 | sed 's/^/  /' || echo "  Cannot connect to database"
    elif [ -f "db.sqlite3" ]; then
        echo "  Using SQLite database"
        ls -lh db.sqlite3 | awk '{print "  Size: " $5}' 
    else
        echo "  Database status unknown"
    fi
    echo ""
}

# Function to check Redis status
check_redis() {
    echo -e "${BLUE}Redis Status:${NC}"
    if command -v redis-cli &> /dev/null; then
        redis-cli ping 2>/dev/null | grep -q "PONG" && echo -e "  ${GREEN}✓ Redis is running${NC}" || echo -e "  ${RED}✗ Redis is not responding${NC}"
    else
        echo "  Redis CLI not installed"
    fi
    echo ""
}

# Function to show Docker status
show_docker() {
    echo -e "${BLUE}Docker Containers:${NC}"
    if command -v docker &> /dev/null; then
        docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null | grep -i codensest || echo "  No Codensest containers running"
        echo ""
        echo "Container Resource Usage:"
        docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" 2>/dev/null | grep -i codensest || echo "  No stats available"
    else
        echo "  Docker not installed"
    fi
    echo ""
}

# Function to show processes
show_processes() {
    echo -e "${BLUE}Python Processes:${NC}"
    ps aux | grep -E "[p]ython.*manage|[g]unicorn" | head -10 | awk '{print "  " $2 " " $11 " " $12}' || echo "  No Python processes found"
    echo ""
}

# Function to show disk usage
show_disk() {
    echo -e "${BLUE}Disk Usage:${NC}"
    df -h / 2>/dev/null | tail -1 | awk '{print "  Root: " $3 " used of " $2 " (" $5 " full)"}' 
    if [ -d "media" ]; then
        du -sh media 2>/dev/null | awk '{print "  Media: " $1}'
    fi
    if [ -d "staticfiles" ]; then
        du -sh staticfiles 2>/dev/null | awk '{print "  Static: " $1}'
    fi
    echo ""
}

# Function to show memory usage
show_memory() {
    echo -e "${BLUE}Memory Usage:${NC}"
    if command -v free &> /dev/null; then
        free -h | grep Mem | awk '{print "  Total: " $2 ", Used: " $3 ", Free: " $4}'
    fi
    echo ""
}

# Main logic
case "${1:-status}" in
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    health)
        check_health
        ;;
    db)
        check_db
        ;;
    redis)
        check_redis
        ;;
    docker)
        show_docker
        ;;
    processes)
        show_processes
        ;;
    disk)
        show_disk
        ;;
    memory)
        show_memory
        ;;
    all)
        show_status
        check_health
        show_processes
        check_db
        check_redis
        show_docker
        show_disk
        show_memory
        show_logs
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        show_help
        exit 1
        ;;
esac
