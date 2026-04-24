#!/bin/bash

# Database Backup Script
# Creates backups of the database and media files

set -e

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "💾 Database Backup"
echo "=================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

BACKUP_DIR="backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Backup SQLite
if [ -f "db.sqlite3" ]; then
    echo -e "${YELLOW}Backing up SQLite database...${NC}"
    cp db.sqlite3 "$BACKUP_DIR/db_$TIMESTAMP.sqlite3"
    echo -e "${GREEN}✓ Database backed up to $BACKUP_DIR/db_$TIMESTAMP.sqlite3${NC}"
fi

# Backup media files
if [ -d "media" ]; then
    echo -e "${YELLOW}Backing up media files...${NC}"
    tar -czf "$BACKUP_DIR/media_$TIMESTAMP.tar.gz" media/
    echo -e "${GREEN}✓ Media backed up to $BACKUP_DIR/media_$TIMESTAMP.tar.gz${NC}"
fi

# Backup uploads
if [ -d "uploads" ]; then
    echo -e "${YELLOW}Backing up uploads...${NC}"
    tar -czf "$BACKUP_DIR/uploads_$TIMESTAMP.tar.gz" uploads/
    echo -e "${GREEN}✓ Uploads backed up to $BACKUP_DIR/uploads_$TIMESTAMP.tar.gz${NC}"
fi

# Backup PostgreSQL (if running in Docker)
if command -v docker &> /dev/null && docker ps | grep -q codensest_db; then
    echo -e "${YELLOW}Backing up PostgreSQL database...${NC}"
    docker exec codensest_db pg_dump -U ${POSTGRES_USER:-codensest} ${POSTGRES_DB:-codensest} > "$BACKUP_DIR/postgres_$TIMESTAMP.sql"
    echo -e "${GREEN}✓ PostgreSQL backed up to $BACKUP_DIR/postgres_$TIMESTAMP.sql${NC}"
fi

# Cleanup old backups (keep last 7 days)
echo -e "${YELLOW}Cleaning up old backups...${NC}"
find $BACKUP_DIR -name "*.sqlite3" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete

echo ""
echo -e "${GREEN}Backup complete!${NC}"
echo ""
echo "Backup location: $BACKUP_DIR"
ls -lh $BACKUP_DIR/*$TIMESTAMP* 2>/dev/null | awk '{print "  " $9 " (" $5 ")"}'
