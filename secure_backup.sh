#!/bin/bash

# Secure Backup Script for Credentials
# This script compresses the backups folder with 7zip password protection
# and uploads it to pCloud using rclone

set -e  # Exit on any error

# Load environment variables from .env file if it exists
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Configuration (can be overridden by environment variables)
BACKUP_DIR="${BACKUP_DIR:-./backups}"
ARCHIVE_NAME="credentials_backup_$(date +%Y%m%d_%H%M%S).7z"
TEMP_DIR="./temp_backup"
RCLONE_REMOTE="${RCLONE_REMOTE:-PCloud}"  # Change this to your pCloud remote name
RCLONE_PATH="${RCLONE_PATH:-credentials-backup/}"  # Path in pCloud

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Function to get password securely
get_password() {
    # Check if password is provided as command line argument
    if [ -n "$1" ]; then
        echo "$1"
        return
    fi
    
    # Check if password is set in environment variable
    if [ -n "$BACKUP_PASSWORD" ]; then
        echo "$BACKUP_PASSWORD"
        return
    fi
    
    # Prompt for password
    echo -n "Enter password for 7zip archive: "
    read -s password
    echo
    echo -n "Confirm password: "
    read -s password_confirm
    echo
    
    if [ "$password" != "$password_confirm" ]; then
        print_error "Passwords do not match!"
        exit 1
    fi
    echo "$password"
}

# Check if required tools are installed
check_dependencies() {
    print_status "Checking dependencies..."
    
    if ! command -v 7z &> /dev/null; then
        print_error "7z is not installed. Please install p7zip: brew install p7zip"
        exit 1
    fi
    
    if ! command -v rclone &> /dev/null; then
        print_error "rclone is not installed. Please install rclone: brew install rclone"
        exit 1
    fi
    
    print_success "All dependencies are installed"
}

# Check if backup directory exists
check_backup_dir() {
    if [ ! -d "$BACKUP_DIR" ]; then
        print_error "Backup directory '$BACKUP_DIR' does not exist!"
        print_status "Please run the credentials backup script first: python3 credentials_backup.py"
        exit 1
    fi
    
    print_success "Backup directory found"
}

# Create 7zip archive with password protection
create_encrypted_archive() {
    print_status "Creating encrypted 7zip archive..."
    
    # Get password (pass command line argument if provided)
    password=$(get_password "$1")
    
    # Create archive with password protection
    # -p: password protection
    # -mhe: encrypt headers (filenames are also encrypted)
    # -mx9: maximum compression
    if 7z a -p"$password" -mhe -mx9 "$ARCHIVE_NAME" "$BACKUP_DIR"/*; then
        print_success "Encrypted archive created: $ARCHIVE_NAME"
        
        # Show archive info
        archive_size=$(du -h "$ARCHIVE_NAME" | cut -f1)
        print_status "Archive size: $archive_size"
    else
        print_error "Failed to create encrypted archive"
        exit 1
    fi
}

# Check rclone configuration
check_rclone_config() {
    print_status "Checking rclone configuration..."
    
    if ! rclone listremotes | grep -q "$RCLONE_REMOTE"; then
        print_warning "pCloud remote '$RCLONE_REMOTE' not found in rclone configuration"
        print_status "Available remotes:"
        rclone listremotes
        print_status ""
        print_status "To configure pCloud, run: rclone config"
        print_status "Choose 'n' for new remote, name it '$RCLONE_REMOTE', and select 'pcloud' as storage type"
        exit 1
    fi
    
    print_success "rclone remote '$RCLONE_REMOTE' is configured"
}

# Upload to pCloud
upload_to_pcloud() {
    print_status "Uploading to pCloud..."
    
    if rclone copy "$ARCHIVE_NAME" "$RCLONE_REMOTE:$RCLONE_PATH" --progress; then
        print_success "Successfully uploaded to pCloud: $RCLONE_REMOTE:$RCLONE_PATH$ARCHIVE_NAME"
    else
        print_error "Failed to upload to pCloud"
        exit 1
    fi
}

# Cleanup
cleanup() {
    print_status "Cleaning up..."
    
    if [ -f "$ARCHIVE_NAME" ]; then
        rm "$ARCHIVE_NAME"
        print_success "Local archive removed"
    fi
    
    if [ -d "$TEMP_DIR" ]; then
        rm -rf "$TEMP_DIR"
        print_success "Temporary directory removed"
    fi
}

# Main execution
main() {
    print_status "Starting secure backup process..."
    print_status "Backup directory: $BACKUP_DIR"
    print_status "Archive name: $ARCHIVE_NAME"
    print_status "pCloud remote: $RCLONE_REMOTE"
    print_status "pCloud path: $RCLONE_PATH"
    echo
    
    # Run all steps
    check_dependencies
    check_backup_dir
    check_rclone_config
    create_encrypted_archive "$1"  # Pass password argument if provided
    upload_to_pcloud
    cleanup
    
    print_success "Secure backup completed successfully!"
    print_status "Your credentials are now safely stored in pCloud with password protection"
}

# Handle script interruption
trap cleanup EXIT

# Run main function
main "$@"
