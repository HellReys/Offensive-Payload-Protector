#!/usr/bin/env python3
"""
Payload Protector Update System
Cross-platform version checking and automatic updates from GitHub releases.
Supports both Windows and Linux systems.
"""

import requests
import json
import os
import sys
import subprocess
import tempfile
import zipfile
import shutil
import platform
import stat
from packaging import version
import argparse
from pathlib import Path


class PayloadProtectorUpdater:
    def __init__(self):
        self.current_version = "v1.1.0"  # This should match your setup.py version
        self.repo_owner = "HellReys"
        self.repo_name = "Offensive-Payload-Protector"
        self.api_url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/releases/latest"
        self.download_url = None
        self.latest_version = None
        self.system = platform.system()

        # Platform-specific configurations
        self.is_windows = self.system == "Windows"
        self.is_linux = self.system == "Linux"

        # Detect installation paths
        self.installation_path = self._detect_installation_path()

    def _detect_installation_path(self):
        """Detect the current installation path cross-platform."""
        try:
            # Try to find the package installation directory
            import payloadprotector
            package_path = os.path.dirname(payloadprotector.__file__)
            return os.path.dirname(package_path)
        except ImportError:
            # Fallback to current script directory
            return os.path.dirname(os.path.abspath(__file__))

    def _get_python_executable(self):
        """Get the correct Python executable for the current platform."""
        # Try different common Python executable names
        python_names = ['python3', 'python', 'py'] if not self.is_windows else ['py', 'python', 'python3']

        for name in python_names:
            try:
                result = subprocess.run([name, '--version'],
                                        capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    return name
            except (subprocess.SubprocessError, FileNotFoundError, subprocess.TimeoutExpired):
                continue

        # Fallback to sys.executable
        return sys.executable

    def _has_write_permissions(self, path):
        """Check if we have write permissions to the installation directory."""
        try:
            test_file = os.path.join(path, 'write_test.tmp')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            return True
        except (PermissionError, OSError):
            return False

    def _request_elevated_permissions(self):
        """Request elevated permissions if needed."""
        if not self._has_write_permissions(self.installation_path):
            if self.is_windows:
                print("[!] Administrator privileges required for update.")
                print("[*] Please run the command as Administrator.")
                return False
            elif self.is_linux:
                print("[!] Root privileges may be required for update.")
                print("[*] You may need to run with 'sudo' if the update fails.")
                return True  # Let's try without sudo first
        return True

    def get_latest_version(self):
        """Fetch the latest version from GitHub releases."""
        try:
            print("[*] Checking for updates...")
            headers = {
                'User-Agent': 'PayloadProtector-Updater/1.0',
                'Accept': 'application/vnd.github.v3+json'
            }

            response = requests.get(self.api_url, headers=headers, timeout=15)
            response.raise_for_status()

            release_data = response.json()
            self.latest_version = release_data['tag_name'].lstrip('v')
            self.download_url = release_data['zipball_url']

            print(f"[+] Latest version found: v{self.latest_version}")
            return self.latest_version
        except requests.exceptions.RequestException as e:
            print(f"[!] Failed to check for updates: {e}")
            print("[*] Please check your internet connection and try again.")
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
            current_clean = self.current_version.lstrip('v')
            return version.parse(latest) > version.parse(current_clean)
        except Exception as e:
            print(f"[!] Version comparison failed: {e}")
            return False

    def download_update(self, temp_dir):
        """Download the latest version."""
        try:
            print(f"[*] Downloading version v{self.latest_version}...")
            print(f"[*] Download URL: {self.download_url}")

            headers = {
                'User-Agent': 'PayloadProtector-Updater/1.0',
                'Accept': 'application/zip'
            }

            response = requests.get(self.download_url, stream=True, headers=headers, timeout=60)
            response.raise_for_status()

            zip_path = os.path.join(temp_dir, "update.zip")
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0

            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            print(f"\r[*] Downloaded: {percent:.1f}%", end='', flush=True)

            print(f"\n[+] Download completed: {zip_path}")
            return zip_path
        except requests.exceptions.RequestException as e:
            print(f"\n[!] Download failed: {e}")
            return None
        except Exception as e:
            print(f"\n[!] Unexpected error during download: {e}")
            return None

    def extract_update(self, zip_path, temp_dir):
        """Extract the downloaded update."""
        try:
            print("[*] Extracting update...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)

            # Find the extracted folder (GitHub creates folder with commit hash)
            extracted_folders = [d for d in os.listdir(temp_dir)
                                 if os.path.isdir(os.path.join(temp_dir, d)) and d != '__MACOSX']

            if not extracted_folders:
                raise Exception("No extracted folder found")

            extracted_path = os.path.join(temp_dir, extracted_folders[0])
            print(f"[+] Extracted to: {extracted_path}")
            return extracted_path
        except Exception as e:
            print(f"[!] Extraction failed: {e}")
            return None

    def backup_current_installation(self):
        """Create a backup of the current installation."""
        try:
            backup_dir = f"{self.installation_path}_backup_{self.current_version.lstrip('v')}"

            print(f"[*] Creating backup at: {backup_dir}")

            if os.path.exists(backup_dir):
                print("[*] Removing old backup...")
                shutil.rmtree(backup_dir)

            # Create backup with proper exclusions
            ignore_patterns = shutil.ignore_patterns(
                '__pycache__', '*.pyc', '*.pyo', '.git', '.idea',
                '*.egg-info', 'build', 'dist', '.pytest_cache',
                '*.log', 'decryptor.py', '*.bin'
            )

            shutil.copytree(self.installation_path, backup_dir, ignore=ignore_patterns)

            print(f"[+] Backup created successfully")
            return backup_dir
        except Exception as e:
            print(f"[!] Backup failed: {e}")
            return None

    def install_update(self, extracted_path):
        """Install the extracted update using cross-platform methods."""
        try:
            print("[*] Installing update...")

            # Check for setup.py in extracted path
            setup_py = os.path.join(extracted_path, 'setup.py')
            if not os.path.exists(setup_py):
                raise Exception("setup.py not found in extracted update")

            # Get Python executable
            python_exe = self._get_python_executable()
            print(f"[*] Using Python executable: {python_exe}")

            # Change to extracted directory for installation
            original_cwd = os.getcwd()
            os.chdir(extracted_path)

            try:
                # Install/upgrade the package
                install_cmd = [python_exe, 'setup.py', 'install', '--force']

                # Add user flag for Linux if not running as root
                if self.is_linux and os.getuid() != 0:
                    install_cmd.append('--user')
                    print("[*] Installing to user directory (no root privileges)")

                print(f"[*] Running: {' '.join(install_cmd)}")
                result = subprocess.run(install_cmd,
                                        capture_output=True, text=True, timeout=120)

                if result.returncode != 0:
                    print(f"[!] Installation failed with return code: {result.returncode}")
                    print(f"[!] stdout: {result.stdout}")
                    print(f"[!] stderr: {result.stderr}")

                    # Try alternative installation method
                    if self.is_linux:
                        print("[*] Trying alternative installation with pip...")
                        pip_cmd = [python_exe, '-m', 'pip', 'install', '.', '--force-reinstall']
                        if os.getuid() != 0:
                            pip_cmd.append('--user')

                        result = subprocess.run(pip_cmd, capture_output=True, text=True, timeout=120)
                        if result.returncode != 0:
                            raise Exception(f"Alternative installation also failed: {result.stderr}")

                print(f"[+] Installation completed successfully")
                return True

            finally:
                os.chdir(original_cwd)

        except subprocess.TimeoutExpired:
            print("[!] Installation timed out")
            return False
        except Exception as e:
            print(f"[!] Installation failed: {e}")
            return False

    def rollback_update(self, backup_dir):
        """Rollback to the previous version."""
        try:
            print("[*] Rolling back update...")

            if not os.path.exists(backup_dir):
                print("[!] Backup directory not found, cannot rollback")
                return False

            # Remove current installation
            temp_name = f"{self.installation_path}_failed_{os.getpid()}"
            if os.path.exists(self.installation_path):
                os.rename(self.installation_path, temp_name)

            # Restore backup
            shutil.copytree(backup_dir, self.installation_path)

            # Remove failed installation
            if os.path.exists(temp_name):
                shutil.rmtree(temp_name)

            print("[+] Rollback completed successfully")
            return True
        except Exception as e:
            print(f"[!] Rollback failed: {e}")
            return False

    def cleanup_temp_files(self):
        """Clean up temporary files and old backups."""
        try:
            # Clean up old backups (keep only the last 3)
            backup_pattern = f"{os.path.basename(self.installation_path)}_backup_"
            parent_dir = os.path.dirname(self.installation_path)

            backups = [d for d in os.listdir(parent_dir)
                       if d.startswith(backup_pattern) and os.path.isdir(os.path.join(parent_dir, d))]

            if len(backups) > 3:
                backups.sort()  # Sort by name (which includes version)
                for old_backup in backups[:-3]:  # Keep only the last 3
                    old_backup_path = os.path.join(parent_dir, old_backup)
                    shutil.rmtree(old_backup_path)
                    print(f"[*] Cleaned up old backup: {old_backup}")

        except Exception as e:
            print(f"[*] Cleanup warning: {e}")

    def update(self, force=False):
        """Perform the complete update process."""
        print(f"[*] Payload Protector Updater")
        print(f"[*] Current version: {self.current_version}")
        print(f"[*] Platform: {self.system}")
        print(f"[*] Installation path: {self.installation_path}")

        # Check permissions
        if not self._request_elevated_permissions():
            return False

        if not force and not self.is_update_available():
            print(f"[+] You're already running the latest version ({self.current_version})")
            return True

        if not self.latest_version:
            self.get_latest_version()

        print(f"[*] Update available: {self.current_version} -> v{self.latest_version}")

        # Create temporary directory
        with tempfile.TemporaryDirectory(prefix='payloadprotector_update_') as temp_dir:
            print(f"[*] Using temporary directory: {temp_dir}")

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
                print("[!] Cannot create backup, aborting update for safety")
                return False

            # Install update
            if self.install_update(extracted_path):
                print("[+] Update completed successfully!")
                print(f"[*] Updated from {self.current_version} to v{self.latest_version}")
                print(f"[*] Backup available at: {backup_dir}")

                # Clean up old backups
                self.cleanup_temp_files()

                # Verify installation
                try:
                    python_exe = self._get_python_executable()
                    result = subprocess.run([python_exe, '-c', 'import payloadprotector; print("OK")'],
                                            capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        print("[+] Installation verified successfully")
                    else:
                        print("[!] Installation verification failed, but update completed")
                except Exception:
                    print("[*] Could not verify installation, but update completed")

                return True
            else:
                print("[!] Update failed, attempting rollback...")
                if self.rollback_update(backup_dir):
                    print("[+] Rollback completed, system restored to previous state")
                else:
                    print("[!] Rollback failed! Manual intervention may be required")
                    print(f"[*] Backup location: {backup_dir}")
                return False

    def check_only(self):
        """Only check for updates without installing."""
        print(f"[*] Payload Protector Update Checker")
        print(f"[*] Current version: {self.current_version}")
        print(f"[*] Platform: {self.system}")

        if self.is_update_available():
            print(f"[+] Update available: {self.current_version} -> v{self.latest_version}")
            print("[*] Run 'payloadprotector --update' to install the latest version")
            print("[*] Or run 'pp-update' for standalone update")
            return True
        else:
            print(f"[+] You're running the latest version ({self.current_version})")
            return False


def main():
    parser = argparse.ArgumentParser(
        description="Payload Protector Cross-Platform Updater",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  pp-update --check    # Check for updates
  pp-update            # Install latest update
  pp-update --force    # Force reinstall latest version

Supported platforms: Windows, Linux
        """
    )
    parser.add_argument("--check", action="store_true",
                        help="Check for updates without installing")
    parser.add_argument("--force", action="store_true",
                        help="Force update even if no new version is available")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Enable verbose output")

    args = parser.parse_args()

    # Enable verbose logging if requested
    if args.verbose:
        import logging
        logging.basicConfig(level=logging.DEBUG)

    updater = PayloadProtectorUpdater()

    try:
        if args.check:
            success = updater.check_only()
        else:
            success = updater.update(force=args.force)

        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n[!] Update cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"[!] Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()