# Credentials Backup Script

A comprehensive Python script to backup credentials from git repositories and home directory.

## Features

- **Git Repository Scanning**: Automatically scans git repositories for secret files
- **Home Directory Backup**: Backs up SSH keys, AWS credentials, and other home directory secrets
- **Structured Backup**: Maintains folder structure for easy reference
- **Multiple File Patterns**: Detects various secret file names and patterns
- **Metadata Tracking**: Creates detailed metadata for each backup
- **File Integrity**: Calculates SHA256 hashes for verification
- **Restore Helper**: Includes a script to restore credentials from backup

## Secret File Detection

The script looks for files matching these patterns:

### File Names
- `secrets`, `secret`, `credentials`, `credential`
- `.env`, `.production.env`, `.staging.env`, `.development.env`
- `config.json`, `settings.json`, `auth.json`, `keys.json`
- `.aws`, `.azure`, `.gcp`, `service-account.json`
- SSH keys: `id_rsa`, `id_ed25519`, `id_ecdsa`
- And many more...

### File Extensions
- `.env`, `.key`, `.pem`, `.p12`, `.jks`
- `.json`, `.conf`, `.config`, `.ini`
- `.yaml`, `.yml`, `.toml`, `.properties`

### Content-Based Detection
Files are also analyzed for common secret keywords like:
- `password`, `token`, `api_key`, `secret_key`
- `private_key`, `certificate`, `auth`
- `database_url`, `connection_string`

## Installation

1. Clone or download this repository
2. Ensure Python 3.6+ is installed
3. Make the scripts executable:
   ```bash
   chmod +x run_backup.sh
   chmod +x credentials_backup.py
   chmod +x restore_helper.py
   ```

## Usage

### Basic Usage

1. **Set up your repositories directory**:
   ```bash
   mkdir -p /path/to/your/git/repos
   # Copy your git repositories into this directory
   ```

2. **Run the backup**:
   ```bash
   ./run_backup.sh
   ```

### Advanced Usage

#### Command Line Options

```bash
python3 credentials_backup.py --help
```

**Required:**
- `--backup-dir`: Directory to store backups

**Optional:**
- `--repos-dir`: Directory containing git repositories to scan
- `--verbose`: Enable verbose logging

#### Examples

```bash
# Basic backup
python3 credentials_backup.py --backup-dir ./backups

# Backup with custom repos directory
python3 credentials_backup.py \
    --backup-dir ./backups \
    --repos-dir /path/to/git/repos \
    --verbose

# Backup only home directory (no repos)
python3 credentials_backup.py --backup-dir ./backups
```

### Restoring Credentials

Use the restore helper script:

```bash
# List available backups
python3 restore_helper.py --backup-dir ./backups --list

# Restore a specific repository
python3 restore_helper.py \
    --backup-dir ./backups \
    --restore-repo my-project \
    --restore-target /path/to/restore/location

# Restore home credentials
python3 restore_helper.py \
    --backup-dir ./backups \
    --restore-home \
    --restore-target /home/user

# Restore SSH keys
python3 restore_helper.py \
    --backup-dir ./backups \
    --restore-ssh \
    --restore-target /home/user
```

## Backup Structure

The backup creates the following structure:

```
backups/
├── repos/                    # Repository backups
│   ├── project1/
│   │   ├── .env
│   │   ├── config/
│   │   │   └── secrets.json
│   │   └── backup_metadata.json
│   └── project2/
│       ├── credentials/
│       └── backup_metadata.json
├── home/                     # Home directory credentials
│   ├── .aws/
│   ├── .ssh/
│   └── backup_metadata.json
├── ssh/                      # SSH keys backup
│   ├── .ssh/
│   └── backup_metadata.json
├── metadata/                 # Backup summaries
│   └── backup_summary.json
└── logs/                     # Backup logs
    └── backup_YYYYMMDD_HHMMSS.log
```

## Configuration

Edit `config.py` to customize:

- Default backup and repository directories
- Additional secret file patterns
- File patterns to exclude
- Maximum file size limits
- Backup retention settings

## Security Considerations

⚠️ **Important Security Notes:**

1. **Backup Location**: Store backups in a secure location with proper access controls
2. **Encryption**: Consider encrypting the backup directory for additional security
3. **Access Control**: Limit access to backup files and scripts
4. **Cleanup**: Regularly clean up old backups to prevent accumulation
5. **Network Security**: If storing backups remotely, use encrypted connections

## Logging

The script creates detailed logs in the `logs/` directory:

- Timestamped log files for each backup run
- Detailed information about files found and backed up
- Error messages for failed operations
- File integrity verification results

## Troubleshooting

### Common Issues

1. **Permission Denied**: Ensure you have read access to repositories and write access to backup directory
2. **Large Files**: The script skips binary files and very large files by default
3. **Git Repository Detection**: Only directories with `.git` folders are considered repositories
4. **SSH Directory**: SSH backup requires access to `~/.ssh` directory

### Debug Mode

Run with verbose logging to see detailed information:

```bash
python3 credentials_backup.py --backup-dir ./backups --repos-dir ./repos --verbose
```

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is open source. Use responsibly and ensure you have proper authorization to backup credentials.
