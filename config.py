"""
Configuration file for credentials backup
"""

import os
from pathlib import Path


# Load environment variables from .env file if it exists
def load_env_file():
    """Load environment variables from .env file"""
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

# Load environment variables
load_env_file()

# Default backup directory (can be overridden by environment variable)
DEFAULT_BACKUP_DIR = os.getenv('BACKUP_DIR', './backups')

# Default repositories directory (can be overridden by environment variable)
DEFAULT_REPOS_DIR = os.getenv('REPOS_DIR', './repos')

# Default home directory (can be overridden by environment variable)
DEFAULT_HOME_DIR = os.getenv('HOME_DIR', str(Path.home()))

# Additional secret file patterns to look for
ADDITIONAL_SECRET_PATTERNS = [
    'docker-compose.yml',
    'docker-compose.yaml',
    'docker-compose.override.yml',
    'k8s.yaml',
    'kubernetes.yaml',
    'helm-values.yaml',
    'terraform.tfvars',
    'variables.tf',
    'main.tf',
    'outputs.tf',
    'ansible.cfg',
    'playbook.yml',
    'inventory.ini',
    'vagrantfile',
    'vagrantfile.rb'
]

# File patterns to exclude (even if they match secret patterns)
EXCLUDE_PATTERNS = [
    'node_modules',
    '.git',
    '.svn',
    '.hg',
    '__pycache__',
    '.pytest_cache',
    '.coverage',
    'coverage',
    '.nyc_output',
    'dist',
    'build',
    '.next',
    '.nuxt',
    'target',
    '.cargo',
    '.gradle',
    '.m2',
    'venv',
    'env',
    '.venv',
    '.env.local',
    '.env.test',
    '.env.example',
    '.env.sample',
    '.env.template'
]

# Maximum file size to backup (in bytes) - 10MB default
MAX_FILE_SIZE = 10 * 1024 * 1024

# Backup retention settings
RETENTION_DAYS = 30  # Keep backups for 30 days
