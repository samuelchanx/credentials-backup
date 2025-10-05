#!/usr/bin/env python3
"""
Credentials Backup Script
Backs up credentials from git repositories and home directory
"""

import argparse
import fnmatch
import hashlib
import json
import logging
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set

from config import DEFAULT_BACKUP_DIR, DEFAULT_HOME_DIR, DEFAULT_REPOS_DIR


class CredentialsBackup:
    def __init__(self, backup_root: str = None, repos_folder: str = None):
        self.backup_root = Path(backup_root) if backup_root else Path(DEFAULT_BACKUP_DIR)
        self.repos_folder = Path(repos_folder) if repos_folder else Path(DEFAULT_REPOS_DIR) if DEFAULT_REPOS_DIR else None
        self.home_dir = Path(DEFAULT_HOME_DIR)
        
        # Secret file patterns to look for
        self.secret_patterns = [
            'secrets',
            'secret',
            'credentials',
            'credential',
            '.env',
            '.production.env',
            '.staging.env',
            '.development.env',
            '.local.env',
            'config.json',
            'settings.json',
            'app.json',
            'database.json',
            'db.json',
            'auth.json',
            'api.json',
            'keys.json',
            'tokens.json',
            '.secrets',
            '.credentials',
            'secrets.json',
            'credentials.json',
            'auth.conf',
            'config.conf',
            'settings.conf',
            '.aws',
            '.azure',
            '.gcp',
            'service-account.json',
            'firebase.json',
            'google-services.json',
            'GoogleService-Info.plist',
            'keystore.jks',
            'keystore.p12',
            'cert.pem',
            'key.pem',
            'private.key',
            'public.key',
            'id_rsa',
            'id_ed25519',
            'id_ecdsa',
            'known_hosts',
            'authorized_keys',
        ]
        
        # File extensions to consider
        self.secret_extensions = [
            '.env',
            '.key',
            '.pem',
            '.p12',
            '.jks',
            '.json',
            '.conf',
            '.config',
            '.ini',
            '.yaml',
            '.yml',
            '.toml',
            '.properties'
        ]
        
        # Setup logging
        self.setup_logging()
        
        # Create backup directory structure
        self.setup_backup_structure()
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_dir = self.backup_root / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = log_dir / f'backup_{timestamp}.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_backup_structure(self):
        """Create backup directory structure"""
        self.backup_root.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (self.backup_root / 'repos').mkdir(exist_ok=True)
        (self.backup_root / 'home').mkdir(exist_ok=True)
        (self.backup_root / 'ssh').mkdir(exist_ok=True)
        (self.backup_root / 'metadata').mkdir(exist_ok=True)
    
    def is_git_repo(self, path: Path) -> bool:
        """Check if a directory is a git repository"""
        return (path / '.git').exists()
    
    def find_secret_files(self, repo_path: Path) -> List[Path]:
        """Find all potential secret files in a repository"""
        secret_files = []
        
        # Common directories to skip
        skip_dirs = {
            '.git', 'node_modules', '__pycache__', '.pytest_cache', 
            '.coverage', 'coverage', '.nyc_output', 'dist', 'build',
            '.next', '.nuxt', 'target', '.cargo', '.gradle', '.m2',
            'venv', 'env', '.venv', '.env.local', '.env.test',
            '.env.example', '.env.sample', '.env.template',
            '.svn', '.hg', '.bzr', '.DS_Store', 'Thumbs.db',
            'vendor', 'bower_components', '.sass-cache', '.cache',
            'tmp', 'temp', 'logs', 'log', '.logs'
        }
        
        # Walk through all files in the repository
        for root, dirs, files in os.walk(repo_path):
            # Skip unwanted directories
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            
            root_path = Path(root)
            
            for file in files:
                file_path = root_path / file
                file_name = file.lower()
                
                # Skip files that are clearly not secrets
                if self.should_skip_file(file_path, file_name):
                    continue
                
                # Check if file matches secret patterns
                if any(pattern.lower() in file_name for pattern in self.secret_patterns):
                    secret_files.append(file_path)
                    continue
                
                # Check file extension
                if any(file_name.endswith(ext) for ext in self.secret_extensions):
                    # Additional check for files that might contain secrets
                    if self.might_contain_secrets(file_path):
                        secret_files.append(file_path)
        
        return secret_files
    
    def find_gitignored_files(self, repo_path: Path) -> List[Path]:
        """Find git-ignored files that might contain secrets"""
        secret_files = []
        
        try:
            # Get git-ignored files using git command
            result = subprocess.run(
                ['git', 'ls-files', '--others', '--ignored', '--exclude-standard'],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                self.logger.warning(f"Could not get git-ignored files for {repo_path}: {result.stderr}")
                return []
            
            ignored_files = result.stdout.strip().split('\n')
            
            for file_path_str in ignored_files:
                if not file_path_str.strip():
                    continue
                    
                file_path = repo_path / file_path_str
                
                if not file_path.exists() or not file_path.is_file():
                    continue
                
                # Skip files in common build/cache directories
                if self.should_skip_gitignored_file(file_path_str):
                    continue
                
                file_name = file_path.name.lower()
                
                # Check if file matches secret patterns
                if any(pattern.lower() in file_name for pattern in self.secret_patterns):
                    secret_files.append(file_path)
                    continue
                
                # Check file extension
                if any(file_name.endswith(ext) for ext in self.secret_extensions):
                    # Additional check for files that might contain secrets
                    if self.might_contain_secrets(file_path):
                        secret_files.append(file_path)
        
        except subprocess.TimeoutExpired:
            self.logger.warning(f"Timeout getting git-ignored files for {repo_path}")
        except Exception as e:
            self.logger.warning(f"Error getting git-ignored files for {repo_path}: {e}")
        
        return secret_files
    
    def should_skip_gitignored_file(self, file_path_str: str) -> bool:
        """Check if a git-ignored file should be skipped"""
        # Skip build dependency directories and their contents
        build_dirs = {
            'ios/pods', 'macos/pods', 'android/app/.cxx', 'android/app/build',
            'android/build', 'android/.gradle', 'android/gradle',
            'node_modules', '__pycache__', '.pytest_cache', '.coverage',
            'coverage', '.nyc_output', 'dist', 'build', '.next', '.nuxt',
            'target', '.cargo', '.gradle', '.m2', 'venv', 'env', '.venv',
            '.env.local', '.env.test', '.env.example', '.env.sample',
            '.env.template', '.svn', '.hg', '.bzr', '.DS_Store', 'Thumbs.db',
            'vendor', 'bower_components', '.sass-cache', '.cache',
            'tmp', 'temp', 'logs', 'log', '.logs'
        }
        
        # Check if file is in a build directory
        file_str = file_path_str.lower()
        for build_dir in build_dirs:
            # Check if the path contains the build directory
            if f'/{build_dir}/' in file_str or file_str.endswith(f'/{build_dir}') or file_str.startswith(f'{build_dir}/'):
                return True
        
        # Skip patterns based on file names
        skip_patterns = {
            'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml',
            'composer.lock', 'Pipfile.lock', 'poetry.lock',
            'Gemfile.lock', 'go.sum', 'Cargo.lock',
            '*.log', '*.tmp', '*.temp', '*.cache',
            '*.pyc', '*.pyo', '*.pyd', '*.so', '*.dylib', '*.dll',
            '*.exe', '*.bin', '*.o', '*.obj', '*.a', '*.lib',
            '*.zip', '*.tar', '*.gz', '*.rar', '*.7z',
            '*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp', '*.svg',
            '*.mp3', '*.mp4', '*.avi', '*.mov', '*.wmv',
            '*.pdf', '*.doc', '*.docx', '*.xls', '*.xlsx',
            '*.ppt', '*.pptx', '*.odt', '*.ods', '*.odp',
            '*.map', '*.min.js', '*.min.css', '*.bundle.js',
            '*.chunk.js', '*.vendor.js', '*.app.js',
            # Build artifacts
            '*.podspec.json', '*.abi.json', '*.xcassets',
            'prefab_config.json', 'Contents.json'
        }
        
        # Skip extensions
        skip_extensions = {
            '.log', '.tmp', '.temp', '.cache', '.pyc', '.pyo', '.pyd',
            '.so', '.dylib', '.dll', '.exe', '.bin', '.o', '.obj',
            '.a', '.lib', '.zip', '.tar', '.gz', '.rar', '.7z',
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg',
            '.mp3', '.mp4', '.avi', '.mov', '.wmv',
            '.pdf', '.doc', '.docx', '.xls', '.xlsx',
            '.ppt', '.pptx', '.odt', '.ods', '.odp',
            '.map', '.min.js', '.min.css', '.bundle.js',
            '.chunk.js', '.vendor.js', '.app.js',
            '.json', '.h', '.m', '.cc', '.cpp', '.c', '.swift'
        }
        
        file_name = file_path_str.split('/')[-1].lower()
        
        # Check file name patterns
        for pattern in skip_patterns:
            if fnmatch.fnmatch(file_name, pattern.lower()):
                return True
        
        # Check file extensions
        if any(file_name.endswith(ext) for ext in skip_extensions):
            return True
        
        return False
    
    def should_skip_file(self, file_path: Path, file_name: str) -> bool:
        """Check if a file should be skipped based on common patterns"""
        
        # Skip build dependency directories and their contents
        build_dirs = {
            'ios/pods', 'macos/pods', 'android/app/.cxx', 'android/app/build',
            'android/build', 'android/.gradle', 'android/gradle',
            'node_modules', '__pycache__', '.pytest_cache', '.coverage',
            'coverage', '.nyc_output', 'dist', 'build', '.next', '.nuxt',
            'target', '.cargo', '.gradle', '.m2', 'venv', 'env', '.venv',
            '.env.local', '.env.test', '.env.example', '.env.sample',
            '.env.template', '.svn', '.hg', '.bzr', '.DS_Store', 'Thumbs.db',
            'vendor', 'bower_components', '.sass-cache', '.cache',
            'tmp', 'temp', 'logs', 'log', '.logs'
        }
        
        # Check if file is in a build directory
        file_str = str(file_path).lower()
        for build_dir in build_dirs:
            if f'/{build_dir}/' in file_str or file_str.endswith(f'/{build_dir}'):
                return True
        
        # Skip patterns based on file names
        skip_patterns = {
            'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml',
            'composer.lock', 'Pipfile.lock', 'poetry.lock',
            'Gemfile.lock', 'go.sum', 'Cargo.lock',
            '*.log', '*.tmp', '*.temp', '*.cache',
            '*.pyc', '*.pyo', '*.pyd', '*.so', '*.dylib', '*.dll',
            '*.exe', '*.bin', '*.o', '*.obj', '*.a', '*.lib',
            '*.zip', '*.tar', '*.gz', '*.rar', '*.7z',
            '*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp', '*.svg',
            '*.mp3', '*.mp4', '*.avi', '*.mov', '*.wmv',
            '*.pdf', '*.doc', '*.docx', '*.xls', '*.xlsx',
            '*.ppt', '*.pptx', '*.odt', '*.ods', '*.odp',
            '*.map', '*.min.js', '*.min.css', '*.bundle.js',
            '*.chunk.js', '*.vendor.js', '*.app.js',
            # Build artifacts
            '*.podspec.json', '*.abi.json', '*.xcassets',
            'prefab_config.json', 'Contents.json'
        }
        
        # Skip extensions
        skip_extensions = {
            '.log', '.tmp', '.temp', '.cache', '.pyc', '.pyo', '.pyd',
            '.so', '.dylib', '.dll', '.exe', '.bin', '.o', '.obj',
            '.a', '.lib', '.zip', '.tar', '.gz', '.rar', '.7z',
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg',
            '.mp3', '.mp4', '.avi', '.mov', '.wmv',
            '.pdf', '.doc', '.docx', '.xls', '.xlsx',
            '.ppt', '.pptx', '.odt', '.ods', '.odp',
            '.map', '.min.js', '.min.css', '.bundle.js',
            '.chunk.js', '.vendor.js', '.app.js',
            '.json', '.h', '.m', '.cc', '.cpp', '.c', '.swift'
        }
        
        # Check file name patterns
        for pattern in skip_patterns:
            if fnmatch.fnmatch(file_name.lower(), pattern.lower()):
                return True
        
        # Check file extensions
        if file_path.suffix.lower() in skip_extensions:
            return True
        
        # Skip very large files (> 1MB)
        try:
            if file_path.stat().st_size > 1024 * 1024:  # 1MB
                return True
        except:
            pass
        
        return False
    
    def might_contain_secrets(self, file_path: Path) -> bool:
        """Check if a file might contain secrets based on content"""
        try:
            # Skip binary files
            if self.is_binary_file(file_path):
                return False
            
            # Read first few lines to check for common secret patterns
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(1024).lower()  # Read first 1KB
                
                secret_keywords = [
                    'password', 'passwd', 'pwd',
                    'secret', 'token', 'key',
                    'api_key', 'apikey',
                    'access_key', 'secret_key',
                    'private_key', 'public_key',
                    'certificate', 'cert',
                    'auth', 'authentication',
                    'credential', 'credentials',
                    'database_url', 'db_url',
                    'connection_string',
                    'jwt', 'bearer',
                    'oauth', 'client_id', 'client_secret'
                ]
                
                return any(keyword in content for keyword in secret_keywords)
        
        except Exception as e:
            self.logger.warning(f"Could not read file {file_path}: {e}")
            return False
    
    def is_binary_file(self, file_path: Path) -> bool:
        """Check if a file is binary"""
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                return b'\0' in chunk
        except:
            return True
    
    def backup_repo_files(self, repo_path: Path, secret_files: List[Path], repo_name: str = None):
        """Backup secret files from a repository"""
        if repo_name is None:
            repo_name = repo_path.name
        
        # Create backup directory maintaining folder structure
        repo_backup_dir = self.backup_root / 'repos' / repo_name
        repo_backup_dir.mkdir(parents=True, exist_ok=True)
        
        backed_up_files = []
        
        for secret_file in secret_files:
            try:
                # Calculate relative path from repo root
                rel_path = secret_file.relative_to(repo_path)
                backup_path = repo_backup_dir / rel_path
                
                # Create parent directories
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Copy file
                shutil.copy2(secret_file, backup_path)
                
                # Calculate file hash for verification
                file_hash = self.calculate_file_hash(secret_file)
                
                backed_up_files.append({
                    'original_path': str(secret_file),
                    'backup_path': str(backup_path),
                    'relative_path': str(rel_path),
                    'file_hash': file_hash,
                    'size': secret_file.stat().st_size,
                    'modified': datetime.fromtimestamp(secret_file.stat().st_mtime).isoformat()
                })
                
                self.logger.info(f"Backed up: {rel_path}")
                
            except Exception as e:
                self.logger.error(f"Failed to backup {secret_file}: {e}")
        
        # Save metadata
        metadata_file = repo_backup_dir / 'backup_metadata.json'
        metadata = {
            'repo_name': repo_name,
            'repo_path': str(repo_path),
            'backup_timestamp': datetime.now().isoformat(),
            'total_files': len(backed_up_files),
            'files': backed_up_files
        }
        
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def backup_home_credentials(self):
        """Backup credential files from home directory"""
        home_backup_dir = self.backup_root / 'home'
        
        # Common credential locations in home directory
        home_credential_paths = [
            '.aws/credentials',
            '.aws/config',
            '.azure/credentials',
            '.gcp/credentials',
            '.docker/config.json',
            '.npmrc',
            '.yarnrc',
            '.gitconfig',
            '.netrc',
            '.pgpass',
            '.my.cnf',
            '.boto',
            '.s3cfg',
            '.gcloud',
            '.kube/config',
            '.helm',
            '.terraform.d',
            '.vault-token',
            '.gnupg',
            '.ssh/config',
            '.ssh/known_hosts',
            '.ssh/authorized_keys'
        ]
        
        # Browser cookies and data - REMOVED (not needed)
        # browser_paths = [
        #     # Chrome
        #     'Library/Application Support/Google/Chrome/Default/Cookies',
        #     'Library/Application Support/Google/Chrome/Default/Login Data',
        #     'Library/Application Support/Google/Chrome/Default/Web Data',
        #     'Library/Application Support/Google/Chrome/Default/Preferences',
        #     # Firefox
        #     'Library/Application Support/Firefox/Profiles',
        #     # Safari
        #     'Library/Cookies/Cookies.binarycookies',
        #     'Library/Safari/LocalStorage',
        #     # Edge
        #     'Library/Application Support/Microsoft Edge/Default/Cookies',
        #     'Library/Application Support/Microsoft Edge/Default/Login Data',
        #     'Library/Application Support/Microsoft Edge/Default/Web Data',
        #     # Brave
        #     'Library/Application Support/BraveSoftware/Brave-Browser/Default/Cookies',
        #     'Library/Application Support/BraveSoftware/Brave-Browser/Default/Login Data',
        #     'Library/Application Support/BraveSoftware/BraveSoftware/Brave-Browser/Default/Web Data'
        # ]
        
        # Add browser paths to credential paths - REMOVED
        # home_credential_paths.extend(browser_paths)
        
        backed_up_files = []
        
        for cred_path in home_credential_paths:
            source_path = self.home_dir / cred_path
            
            if source_path.exists():
                try:
                    if source_path.is_file():
                        backup_path = home_backup_dir / cred_path
                        backup_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(source_path, backup_path)
                        
                        file_hash = self.calculate_file_hash(source_path)
                        backed_up_files.append({
                            'original_path': str(source_path),
                            'backup_path': str(backup_path),
                            'file_hash': file_hash,
                            'size': source_path.stat().st_size,
                            'modified': datetime.fromtimestamp(source_path.stat().st_mtime).isoformat()
                        })
                        
                        self.logger.info(f"Backed up home credential: {cred_path}")
                    
                    elif source_path.is_dir():
                        # Skip directories to avoid backing up large folders accidentally
                        self.logger.warning(f"Skipping directory (not backing up): {cred_path}")
                        continue
                
                except Exception as e:
                    self.logger.error(f"Failed to backup {source_path}: {e}")
        
        # Save home backup metadata
        metadata_file = home_backup_dir / 'backup_metadata.json'
        metadata = {
            'backup_timestamp': datetime.now().isoformat(),
            'home_directory': str(self.home_dir),
            'total_files': len(backed_up_files),
            'files': backed_up_files
        }
        
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def backup_ssh_keys(self):
        """Backup SSH keys and configuration"""
        ssh_dir = self.home_dir / '.ssh'
        ssh_backup_dir = self.backup_root / 'ssh'
        
        if not ssh_dir.exists():
            self.logger.warning("SSH directory not found")
            return
        
        backed_up_files = []
        
        try:
            # Copy entire .ssh directory
            shutil.copytree(ssh_dir, ssh_backup_dir / '.ssh', dirs_exist_ok=True)
            
            # List all files for metadata
            for file_path in ssh_dir.rglob('*'):
                if file_path.is_file():
                    file_hash = self.calculate_file_hash(file_path)
                    backed_up_files.append({
                        'original_path': str(file_path),
                        'file_hash': file_hash,
                        'size': file_path.stat().st_size,
                        'modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                    })
            
            self.logger.info(f"Backed up SSH directory with {len(backed_up_files)} files")
            
        except Exception as e:
            self.logger.error(f"Failed to backup SSH directory: {e}")
        
        # Save SSH backup metadata
        metadata_file = ssh_backup_dir / 'backup_metadata.json'
        metadata = {
            'backup_timestamp': datetime.now().isoformat(),
            'ssh_directory': str(ssh_dir),
            'total_files': len(backed_up_files),
            'files': backed_up_files
        }
        
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of a file"""
        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            self.logger.warning(f"Could not calculate hash for {file_path}: {e}")
            return ""
    
    def find_all_git_repos(self, root_path: Path) -> List[Path]:
        """Recursively find all git repositories"""
        git_repos = []
        
        try:
            for item in root_path.rglob('.git'):
                if item.is_dir():
                    # Get the parent directory (the actual repo root)
                    repo_path = item.parent
                    # Skip the backup directory itself to avoid infinite loops
                    if 'backups' not in str(repo_path) and 'credentials-backup' not in str(repo_path):
                        git_repos.append(repo_path)
        except Exception as e:
            self.logger.error(f"Error scanning for git repositories: {e}")
        
        return git_repos
    
    def scan_repositories(self):
        """Scan and backup all repositories recursively"""
        if not self.repos_folder or not self.repos_folder.exists():
            self.logger.warning("Repositories folder not specified or doesn't exist")
            return
        
        # Find all git repositories recursively
        self.logger.info(f"Scanning for git repositories in: {self.repos_folder}")
        git_repos = self.find_all_git_repos(self.repos_folder)
        
        repos_found = len(git_repos)
        repos_backed_up = 0
        
        self.logger.info(f"Found {repos_found} git repositories")
        
        # Process each repository
        for repo_path in git_repos:
            # Calculate relative path to maintain folder structure
            try:
                rel_path = repo_path.relative_to(self.repos_folder)
                self.logger.info(f"Scanning repository: {rel_path} ({repo_path})")
                
                secret_files = self.find_gitignored_files(repo_path)
                
                if secret_files:
                    self.logger.info(f"Found {len(secret_files)} git-ignored secret files in {rel_path}")
                    self.backup_repo_files(repo_path, secret_files, str(rel_path))
                    repos_backed_up += 1
                else:
                    self.logger.info(f"No git-ignored secret files found in {rel_path}")
                
            except Exception as e:
                self.logger.error(f"Failed to process repository {repo_path}: {e}")
        
        self.logger.info(f"Repository scan complete: {repos_backed_up}/{repos_found} repositories backed up")
    
    def create_backup_summary(self):
        """Create a summary of the backup"""
        summary = {
            'backup_timestamp': datetime.now().isoformat(),
            'backup_root': str(self.backup_root),
            'repos_folder': str(self.repos_folder) if self.repos_folder else None,
            'home_directory': str(self.home_dir),
            'total_size': self.calculate_backup_size()
        }
        
        summary_file = self.backup_root / 'metadata' / 'backup_summary.json'
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        self.logger.info(f"Backup summary saved to {summary_file}")
    
    def calculate_backup_size(self) -> int:
        """Calculate total size of backup"""
        total_size = 0
        for file_path in self.backup_root.rglob('*'):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        return total_size
    
    def run_backup(self):
        """Run the complete backup process"""
        self.logger.info("Starting credentials backup...")
        
        # Backup repositories
        if self.repos_folder:
            self.scan_repositories()
        
        # Backup home credentials
        self.backup_home_credentials()
        
        # Backup SSH keys
        self.backup_ssh_keys()
        
        # Create summary
        self.create_backup_summary()
        
        self.logger.info("Credentials backup completed!")


def main():
    parser = argparse.ArgumentParser(description='Backup credentials from repositories and home directory')
    parser.add_argument('--backup-dir', default=DEFAULT_BACKUP_DIR, help=f'Directory to store backups (default: {DEFAULT_BACKUP_DIR})')
    parser.add_argument('--repos-dir', default=DEFAULT_REPOS_DIR, help=f'Directory containing git repositories to scan (default: {DEFAULT_REPOS_DIR})')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Create backup instance
    backup = CredentialsBackup(
        backup_root=args.backup_dir,
        repos_folder=args.repos_dir
    )
    
    # Set logging level
    if args.verbose:
        backup.logger.setLevel(logging.DEBUG)
    
    # Run backup
    backup.run_backup()


if __name__ == '__main__':
    main()
