#!/usr/bin/env python3
"""
Payload Protector Update System
Handles version checking and automatic updates from GitHub releases.
"""

import requests
import json
import os
import sys
import subprocess
import tempfile
import zipfile
import shutil
from packaging import version
import argparse


class PayloadProtectorUpdater:
    def __init__(self):
        self.current_version = "v1.1.0"  # This should match your setup.py version
        self.repo_owner = "HellReys"
        self.repo_name = "Offensive-Payload-Protector"
        self.api_url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/releases/latest"
        self.download_url = None
        self.latest_version = None

    def get_latest_version(self):
        """Fetch the latest version from GitHub releases."""
        try:
            print("[*] Checking for updates...")
            response = requests.get(self.api_url, timeout=10)
            response.raise_for_status()

            release_data = response.json()
            self.latest_version = release_data['tag_name'].lstrip('v')
            self.download_url = release_data['zipball_url']

            return self.latest_version
        except requests.exceptions.RequestException as e:
            print(f"[!] Failed to check for updates: {e}")
            return None
        except KeyError as e:
            print(f"[!] Invalid response format: {e}")
            return None

    def is_update_available(self):
        """Check if an update is available."""
        latest = self.get_latest_version()
        if not latest:
            return False

        try:
            return version.parse(latest) > version.parse(self.current_version)
        except Exception as e:
            print(f"[!] Version comparison failed: {e}")
            return False

    def download_update(self, temp_dir):
        """Download the latest version."""
        try:
            print(f"[*] Downloading version {self.latest_version}...")
            response = requests.get(self.download_url, stream=True, timeout=30)
            response.raise_for_status()

            zip_path = os.path.join(temp_dir, "update.zip")
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            return zip_path
        except requests.exceptions.RequestException as e:
            print(f"[!] Download failed: {e}")
            return None

    def extract_update(self, zip_path, temp_dir):
        """Extract the downloaded update."""
        try:
            print("[*] Extracting update...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)

            # Find the extracted folder (GitHub creates folder with commit hash)
            extracted_folders = [d for d in os.listdir(temp_dir)
                                 if os.path.isdir(os.path.join(temp_dir, d))]

            if not extracted_folders:
                raise Exception("No extracted folder found")

            return os.path.join(temp_dir, extracted_folders[0])
        except Exception as e:
            print(f"[!] Extraction failed: {e}")
            return None

    def backup_current_installation(self):
        """Create a backup of the current installation."""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            backup_dir = f"{current_dir}_backup_{self.current_version}"

            if os.path.exists(backup_dir):
                shutil.rmtree(backup_dir)

            shutil.copytree(current_dir, backup_dir,
                            ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '.git'))

            print(f"[+] Backup created: {backup_dir}")
            return backup_dir
        except Exception as e:
            print(f"[!] Backup failed: {e}")
            return None

    def install_update(self, extracted_path):
        """Install the extracted update."""
        try:
            print("[*] Installing update...")
            current_dir = os.path.dirname(os.path.abspath(__file__))

            # Copy new files (excluding .git and other unwanted files)
            for item in os.listdir(extracted_path):
                if item in ['.git', '.idea', '__pycache__', '.gitignore']:
                    continue

                src_path = os.path.join(extracted_path, item)
                dst_path = os.path.join(current_dir, item)

                if os.path.isdir(src_path):
                    if os.path.exists(dst_path):
                        shutil.rmtree(dst_path)
                    shutil.copytree(src_path, dst_path)
                else:
                    shutil.copy2(src_path, dst_path)

            # Reinstall the package
            subprocess.check_call([sys.executable, 'setup.py', 'install', '--force'],
                                  cwd=current_dir)

            print(f"[+] Successfully updated to version {self.latest_version}")
            return True
        except Exception as e:
            print(f"[!] Installation failed: {e}")
            return False

    def rollback_update(self, backup_dir):
        """Rollback to the previous version."""
        try:
            print("[*] Rolling back update...")
            current_dir = os.path.dirname(os.path.abspath(__file__))

            # Remove current installation
            temp_name = f"{current_dir}_failed"
            os.rename(current_dir, temp_name)

            # Restore backup
            os.rename(backup_dir, current_dir)

            # Remove failed installation
            shutil.rmtree(temp_name)

            print("[+] Rollback completed")
            return True
        except Exception as e:
            print(f"[!] Rollback failed: {e}")
            return False

    def update(self, force=False):
        """Perform the complete update process."""
        if not force and not self.is_update_available():
            print(f"[+] You're already running the latest version ({self.current_version})")
            return True

        if not self.latest_version:
            self.get_latest_version()

        print(f"[*] Update available: {self.current_version} -> {self.latest_version}")

        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Download update
            zip_path = self.download_update(temp_dir)
            if not zip_path:
                return False

            # Extract update
            extracted_path = self.extract_update(zip_path, temp_dir)
            if not extracted_path:
                return False

            # Create backup
            backup_dir = self.backup_current_installation()
            if not backup_dir:
                print("[!] Cannot create backup, aborting update")
                return False

            # Install update
            if self.install_update(extracted_path):
                print("[+] Update completed successfully!")
                print(f"[*] Backup available at: {backup_dir}")
                return True
            else:
                # Rollback on failure
                self.rollback_update(backup_dir)
                return False

    def check_only(self):
        """Only check for updates without installing."""
        if self.is_update_available():
            print(f"[+] Update available: {self.current_version} -> {self.latest_version}")
            print("[*] Run 'payloadprotector --update' to install the latest version")
            return True
        else:
            print(f"[+] You're running the latest version ({self.current_version})")
            return False


def main():
    parser = argparse.ArgumentParser(description="Payload Protector Updater")
    parser.add_argument("--check", action="store_true",
                        help="Check for updates without installing")
    parser.add_argument("--force", action="store_true",
                        help="Force update even if no new version is available")
    args = parser.parse_args()

    updater = PayloadProtectorUpdater()

    if args.check:
        updater.check_only()
    else:
        updater.update(force=args.force)


if __name__ == "__main__":
    main()