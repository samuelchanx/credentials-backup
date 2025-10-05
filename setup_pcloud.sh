#!/bin/bash

# rclone pCloud Configuration Helper
# This script helps you configure rclone to work with pCloud

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

print_status "pCloud rclone Configuration Helper"
echo

print_status "This script will help you configure rclone for pCloud storage."
print_status "You'll need your pCloud username and password."
echo

# Check if rclone is installed
if ! command -v rclone &> /dev/null; then
    print_error "rclone is not installed. Please install it first: brew install rclone"
    exit 1
fi

print_status "Starting rclone configuration..."
echo

# Run rclone config
print_status "Follow these steps in the rclone config:"
echo
echo "1. Choose 'n' for new remote"
echo "2. Name it 'pcloud' (or your preferred name)"
echo "3. Choose 'pcloud' from the storage type list"
echo "4. Enter your pCloud username (email)"
echo "5. Enter your pCloud password"
echo "6. Leave other options as default (press Enter)"
echo "7. Choose 'y' to save the configuration"
echo "8. Choose 'q' to quit"
echo

read -p "Press Enter to start rclone configuration..."

rclone config

print_success "rclone configuration completed!"
echo

# Test the configuration
print_status "Testing the configuration..."
if rclone lsd pcloud: &> /dev/null; then
    print_success "pCloud connection successful!"
    print_status "Your pCloud folders:"
    rclone lsd pcloud:
else
    print_error "pCloud connection failed. Please check your credentials."
    exit 1
fi

print_success "Setup complete! You can now use ./secure_backup.sh to backup your credentials."
