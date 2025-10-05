#!/bin/bash

# Environment Setup Script for Credentials Backup
# This script helps you create your .env file from the template

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_status "Credentials Backup Environment Setup"
echo

# Check if .env already exists
if [ -f .env ]; then
    print_warning ".env file already exists!"
    echo -n "Do you want to overwrite it? (y/N): "
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        print_status "Setup cancelled."
        exit 0
    fi
fi

print_status "Creating .env file from template..."

# Copy template to .env
cp .env.example .env

print_success ".env file created!"

echo
print_status "Please edit the .env file to customize your settings:"
echo
print_status "Key settings to configure:"
echo "  - BACKUP_DIR: Where to store backups (default: ./backups)"
echo "  - REPOS_DIR: Directory containing your git repositories"
echo "  - RCLONE_REMOTE: Your rclone remote name (e.g., PCloud)"
echo "  - BACKUP_PASSWORD: Optional default password for 7zip encryption"
echo

print_status "You can edit the file with:"
echo "  nano .env"
echo "  vim .env"
echo "  code .env"
echo

print_status "After editing, you can run:"
echo "  python3 credentials_backup.py  # Uses .env defaults"
echo "  ./secure_backup.sh            # Uses .env defaults"
echo "  ./secure_backup.sh mypassword  # Override password"
echo

print_success "Setup complete! Remember to configure rclone if you haven't already:"
print_status "  ./setup_pcloud.sh"
