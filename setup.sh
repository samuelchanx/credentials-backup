#!/bin/bash

# Setup script for Credentials Backup

echo "Setting up Credentials Backup Script..."
echo "======================================"

# Create necessary directories
echo "Creating directories..."
mkdir -p backups
mkdir -p repos
mkdir -p logs

# Make scripts executable
echo "Making scripts executable..."
chmod +x credentials_backup.py
chmod +x restore_helper.py
chmod +x run_backup.sh
chmod +x setup.sh

# Check Python installation
echo "Checking Python installation..."
if command -v python3 &> /dev/null; then
    echo "✓ Python3 is installed"
    python3 --version
else
    echo "✗ Python3 is not installed. Please install Python 3.6+ first."
    exit 1
fi

# Test script syntax
echo "Testing script syntax..."
python3 -m py_compile credentials_backup.py
if [ $? -eq 0 ]; then
    echo "✓ Main backup script syntax is valid"
else
    echo "✗ Main backup script has syntax errors"
    exit 1
fi

python3 -m py_compile restore_helper.py
if [ $? -eq 0 ]; then
    echo "✓ Restore helper script syntax is valid"
else
    echo "✗ Restore helper script has syntax errors"
    exit 1
fi

echo ""
echo "Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Copy your git repositories to the 'repos' directory"
echo "2. Customize the paths in 'run_backup.sh' if needed"
echo "3. Run './run_backup.sh' to start your first backup"
echo ""
echo "For more information, see README.md"
