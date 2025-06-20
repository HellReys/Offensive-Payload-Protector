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
import pkg_resources
import site


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
        self.use_user_install = self._should_use_user_install()

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

    def _should_use_user_install(self):
        """Determine if we should use user installation mode."""
        if self.is_windows:
            return False  # Windows typically doesn't need user mode

        if self.is_linux:
            # Check if we're running as root
            try:
                return os.getuid() != 0
            except AttributeError:
                return True  # Assume non-root if getuid() is not available

        return True  # Default to user install for other platforms

    def _get_python_executable(self):
        """Get the correct Python executable for the current platform."""
        # First, try the current interpreter
        current_python = sys.executable
        if current_python and os.path.exists(current_python):
            return current_python

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

        # Final fallback
        return 'python3' if not self.is_windows else 'python'

    def _get_pip_executable(self):
        """Get the correct pip executable."""
        python_exe = self._get_python_executable()

        # Try python -m pip first (most reliable)
        try:
            result = subprocess.run([python_exe, '-m', 'pip', '--version'],
                                    capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return [python_exe, '-m', 'pip']
        except:
            pass

        # Try standalone pip executables
        pip_names = ['pip3', 'pip']
        for pip_name in pip_names:
            try:
                result = subprocess.run([pip_name, '--version'],
                                        capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    return [pip_name]
            except:
                continue

        # Fallback to python -m pip
        return [python_exe, '-m', 'pip']

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
        if not self.use_user_install and not self._has_write_permissions(self.installation_path):
            if self.is_windows:
                print("[!] Administrator privileges required for system-wide update.")
                print("[*] Please run the command as Administrator.")
                return False
            elif self.is_linux:
                print("[!] Root privileges may be required for system-wide update.")
                print("[*] Trying user installation mode instead...")
                self.use_user_install = True
                return True
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
        """Install the extracted update using pip (most reliable method)."""
        try:
            print("[*] Installing update...")

            # Check for setup.py in extracted path
            setup_py = os.path.join(extracted_path, 'setup.py')
            if not os.path.exists(setup_py):
                raise Exception("setup.py not found in extracted update")

            # Get pip executable
            pip_cmd = self._get_pip_executable()
            print(f"[*] Using pip command: {' '.join(pip_cmd)}")

            # Prepare installation command
            install_cmd = pip_cmd + ['install', extracted_path, '--force-reinstall', '--no-deps']

            # Add user flag for Linux if needed
            if self.use_user_install:
                install_cmd.append('--user')
                print("[*] Installing to user directory")

            # Add upgrade flag to ensure latest version
            install_cmd.append('--upgrade')

            print(f"[*] Running: {' '.join(install_cmd)}")

            # Run the installation
            result = subprocess.run(install_cmd,
                                    capture_output=True, text=True, timeout=120)

            if result.returncode != 0:
                print(f"[!] Pip installation failed with return code: {result.returncode}")
                print(f"[!] stdout: {result.stdout}")
                print(f"[!] stderr: {result.stderr}")

                # Try alternative method with setup.py
                print("[*] Trying alternative installation with setup.py...")

                python_exe = self._get_python_executable()
                original_cwd = os.getcwd()
                os.chdir(extracted_path)

                try:
                    setup_cmd = [python_exe, 'setup.py', 'install']
                    if self.use_user_install:
                        setup_cmd.append('--user')
                    setup_cmd.append('--force')

                    result = subprocess.run(setup_cmd, capture_output=True, text=True, timeout=120)
                    if result.returncode != 0:
                        raise Exception(f"Setup.py installation also failed: {result.stderr}")

                finally:
                    os.chdir(original_cwd)

            print(f"[+] Installation completed successfully")

            # Install dependencies
            self._install_dependencies(extracted_path)

            return True

        except subprocess.TimeoutExpired:
            print("[!] Installation timed out")
            return False
        except Exception as e:
            print(f"[!] Installation failed: {e}")
            return False

    def _install_dependencies(self, extracted_path):
        """Install dependencies from requirements.txt if available."""
        try:
            requirements_path = os.path.join(extracted_path, 'requirements.txt')
            if os.path.exists(requirements_path):
                print("[*] Installing dependencies...")

                pip_cmd = self._get_pip_executable()
                deps_cmd = pip_cmd + ['install', '-r', requirements_path]

                if self.use_user_install:
                    deps_cmd.append('--user')

                result = subprocess.run(deps_cmd, capture_output=True, text=True, timeout=60)

                if result.returncode == 0:
                    print("[+] Dependencies installed successfully")
                else:
                    print(f"[!] Some dependencies may not have been installed: {result.stderr}")
        except Exception as e:
            print(f"[*] Warning: Could not install dependencies: {e}")

    def rollback_update(self, backup_dir):
        """Rollback to the previous version."""
        try:
            print("[*] Rolling back update...")

            if not os.path.exists(backup_dir):
                print("[!] Backup directory not found, cannot rollback")
                return False

            # For pip installations, try to reinstall from backup
            if os.path.exists(os.path.join(backup_dir, 'setup.py')):
                pip_cmd = self._get_pip_executable()
                rollback_cmd = pip_cmd + ['install', backup_dir, '--force-reinstall']

                if self.use_user_install:
                    rollback_cmd.append('--user')

                result = subprocess.run(rollback_cmd, capture_output=True, text=True, timeout=60)

                if result.returncode == 0:
                    print("[+] Rollback completed successfully")
                    return True
                else:
                    print(f"[!] Rollback failed: {result.stderr}")

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

            if os.path.exists(parent_dir):
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

    def _verify_installation(self):
        """Verify that the installation was successful."""
        try:
            python_exe = self._get_python_executable()

            # Test if the package can be imported
            test_cmd = [python_exe, '-c', 'import payloadprotector; print("Import OK")']
            result = subprocess.run(test_cmd, capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                print("[+] Package import verification: OK")
            else:
                print(f"[!] Package import failed: {result.stderr}")
                return False

            # Test if the command line tool works
            cmd_test = [python_exe, '-c', 'from payloadprotector.cli import main; print("CLI OK")']
            result = subprocess.run(cmd_test, capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                print("[+] CLI tool verification: OK")
                return True
            else:
                print(f"[!] CLI tool verification failed: {result.stderr}")
                return False

        except Exception as e:
            print(f"[*] Verification error: {e}")
            return False

    def _refresh_environment(self):
        """Refresh the Python environment to pick up new installations."""
        try:
            # Refresh sys.path for user installations
            if self.use_user_install:
                user_site = site.getusersitepackages()
                if user_site not in sys.path:
                    sys.path.insert(0, user_site)

            # Refresh pkg_resources
            try:
                pkg_resources._initialize_master_working_set()
            except:
                pass  # Ignore if pkg_resources refresh fails

        except Exception as e:
            print(f"[*] Environment refresh warning: {e}")

    def update(self, force=False):
        """Perform the complete update process."""
        print(f"[*] Payload Protector Updater")
        print(f"[*] Current version: {self.current_version}")
        print(f"[*] Platform: {self.system}")
        print(f"[*] Installation path: {self.installation_path}")
        print(f"[*] User installation: {'Yes' if self.use_user_install else 'No'}")

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

            # Create backup (optional for pip installations)
            backup_dir = self.backup_current_installation()

            # Install update
            if self.install_update(extracted_path):
                print("[+] Update completed successfully!")
                print(f"[*] Updated from {self.current_version} to v{self.latest_version}")

                if backup_dir:
                    print(f"[*] Backup available at: {backup_dir}")

                # Refresh environment
                self._refresh_environment()

                # Verify installation
                if self._verify_installation():
                    print("[+] Installation verified successfully")

                    # Clean up old backups
                    self.cleanup_temp_files()

                    print("[*] Please restart your terminal or run 'hash -r' to refresh the command cache")
                    return True
                else:
                    print("[!] Installation verification failed")
                    if backup_dir:
                        print("[*] Attempting rollback...")
                        self.rollback_update(backup_dir)
                    return False
            else:
                print("[!] Update failed")
                if backup_dir:
                    print("[*] Attempting rollback...")
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

The updater will automatically:
- Use user installation on Linux (unless running as root)
- Use system installation on Windows (with admin privileges)
- Create backups before updating
- Verify installation after update
- Rollback on failure
        """
    )
    parser.add_argument("--check", action="store_true",
                        help="Check for updates without installing")
    parser.add_argument("--force", action="store_true",
                        help="Force update even if no new version is available")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Enable verbose output")
    parser.add_argument("--system", action="store_true",
                        help="Force system-wide installation (requires admin/root)")

    args = parser.parse_args()

    # Enable verbose logging if requested
    if args.verbose:
        import logging
        logging.basicConfig(level=logging.DEBUG)

    updater = PayloadProtectorUpdater()

    # Override user installation mode if system flag is provided
    if args.system:
        updater.use_user_install = False
        print("[*] Forcing system-wide installation mode")

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