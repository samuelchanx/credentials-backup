#!/usr/bin/env python3
"""
Restore Helper Script
Helps restore credentials from backup
"""

import argparse
import json
import shutil
from pathlib import Path


class CredentialsRestore:
    def __init__(self, backup_dir: str):
        self.backup_dir = Path(backup_dir)
    
    def list_backups(self):
        """List available backups"""
        print("Available backups:")
        print("================")
        
        # List repository backups
        repos_dir = self.backup_dir / 'repos'
        if repos_dir.exists():
            print("\nRepository Backups:")
            for repo_dir in repos_dir.iterdir():
                if repo_dir.is_dir():
                    metadata_file = repo_dir / 'backup_metadata.json'
                    if metadata_file.exists():
                        with open(metadata_file, 'r') as f:
                            metadata = json.load(f)
                        print(f"  - {repo_dir.name}: {metadata['total_files']} files")
        
        # List home backups
        home_dir = self.backup_dir / 'home'
        if home_dir.exists():
            print("\nHome Directory Backups:")
            metadata_file = home_dir / 'backup_metadata.json'
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                print(f"  - Home credentials: {metadata['total_files']} files")
        
        # List SSH backups
        ssh_dir = self.backup_dir / 'ssh'
        if ssh_dir.exists():
            print("\nSSH Backups:")
            metadata_file = ssh_dir / 'backup_metadata.json'
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                print(f"  - SSH keys: {metadata['total_files']} files")
    
    def restore_repo(self, repo_name: str, target_dir: str):
        """Restore a specific repository backup"""
        repo_backup_dir = self.backup_dir / 'repos' / repo_name
        
        if not repo_backup_dir.exists():
            print(f"Repository backup '{repo_name}' not found")
            return False
        
        target_path = Path(target_dir)
        target_path.mkdir(parents=True, exist_ok=True)
        
        # Copy all files except metadata
        for file_path in repo_backup_dir.rglob('*'):
            if file_path.is_file() and file_path.name != 'backup_metadata.json':
                rel_path = file_path.relative_to(repo_backup_dir)
                target_file = target_path / rel_path
                target_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file_path, target_file)
                print(f"Restored: {rel_path}")
        
        print(f"Repository '{repo_name}' restored to {target_dir}")
        return True
    
    def restore_home_credentials(self, target_home: str):
        """Restore home directory credentials"""
        home_backup_dir = self.backup_dir / 'home'
        
        if not home_backup_dir.exists():
            print("Home credentials backup not found")
            return False
        
        target_home_path = Path(target_home)
        
        # Copy all files except metadata
        for file_path in home_backup_dir.rglob('*'):
            if file_path.is_file() and file_path.name != 'backup_metadata.json':
                rel_path = file_path.relative_to(home_backup_dir)
                target_file = target_home_path / rel_path
                target_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file_path, target_file)
                print(f"Restored: {rel_path}")
        
        print(f"Home credentials restored to {target_home}")
        return True
    
    def restore_ssh_keys(self, target_home: str):
        """Restore SSH keys"""
        ssh_backup_dir = self.backup_dir / 'ssh' / '.ssh'
        
        if not ssh_backup_dir.exists():
            print("SSH keys backup not found")
            return False
        
        target_ssh_dir = Path(target_home) / '.ssh'
        
        # Copy entire .ssh directory
        shutil.copytree(ssh_backup_dir, target_ssh_dir, dirs_exist_ok=True)
        
        print(f"SSH keys restored to {target_ssh_dir}")
        return True

def main():
    parser = argparse.ArgumentParser(description='Restore credentials from backup')
    parser.add_argument('--backup-dir', required=True, help='Backup directory')
    parser.add_argument('--list', action='store_true', help='List available backups')
    parser.add_argument('--restore-repo', help='Restore specific repository')
    parser.add_argument('--restore-target', help='Target directory for restoration')
    parser.add_argument('--restore-home', action='store_true', help='Restore home credentials')
    parser.add_argument('--restore-ssh', action='store_true', help='Restore SSH keys')
    
    args = parser.parse_args()
    
    restore = CredentialsRestore(args.backup_dir)
    
    if args.list:
        restore.list_backups()
    elif args.restore_repo and args.restore_target:
        restore.restore_repo(args.restore_repo, args.restore_target)
    elif args.restore_home and args.restore_target:
        restore.restore_home_credentials(args.restore_target)
    elif args.restore_ssh and args.restore_target:
        restore.restore_ssh_keys(args.restore_target)
    else:
        print("Use --help for usage information")

if __name__ == '__main__':
    main()
