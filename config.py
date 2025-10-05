"""
Configuration file for credentials backup
"""

# Default backup directory
DEFAULT_BACKUP_DIR = "/Users/sc/Documents/workdev/credentials-backup/backups"

# Default repositories directory (customize this path)
DEFAULT_REPOS_DIR = "/Users/sc/Documents/workdev/credentials-backup/repos"

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
