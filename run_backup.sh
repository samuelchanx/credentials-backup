#!/bin/bash

# Credentials Backup Runner Script
# This script provides easy commands to run the backup

BACKUP_DIR="/Users/sc/Documents/workdev/credentials-backup/backups"
REPOS_DIR="/Users/sc/Documents/workdev/credentials-backup/repos"  # Customize this path

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Credentials Backup Script${NC}"
echo "=========================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python3 is not installed or not in PATH${NC}"
    exit 1
fi

# Check if backup directory exists
if [ ! -d "$BACKUP_DIR" ]; then
    echo -e "${YELLOW}Creating backup directory: $BACKUP_DIR${NC}"
    mkdir -p "$BACKUP_DIR"
fi

# Check if repos directory exists
if [ ! -d "$REPOS_DIR" ]; then
    echo -e "${YELLOW}Warning: Repositories directory not found: $REPOS_DIR${NC}"
    echo -e "${YELLOW}Please create this directory and add your git repositories${NC}"
    echo -e "${YELLOW}Or specify a different path using --repos-dir argument${NC}"
fi

echo -e "${GREEN}Starting backup process...${NC}"
echo "Backup directory: $BACKUP_DIR"
echo "Repositories directory: $REPOS_DIR"
echo ""

# Run the backup script
python3 credentials_backup.py \
    --backup-dir "$BACKUP_DIR" \
    --repos-dir "$REPOS_DIR" \
    --verbose

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Backup completed successfully!${NC}"
    echo -e "${BLUE}Backup location: $BACKUP_DIR${NC}"
else
    echo -e "${RED}Backup failed! Check the logs for details.${NC}"
    exit 1
fi
