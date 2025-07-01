#!/usr/bin/env python3
"""
Improved Payload Protector Update System
Cross-platform version checking and automatic updates from GitHub releases.
Fixed Linux compatibility issues.
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
import sysconfig


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
        self.is_macos = self.system == "Darwin"

        # Detect installation environment
        self.installation_info = self._detect_installation_environment()
        self.use_user_install = self.installation_info['use_user_install']
        self.installation_path = self.installation_info['installation_path']

    def _detect_installation_environment(self):
        """Comprehensive detection of installation environment."""
        info = {
            'installation_path': None,
            'use_user_install': True,  # Default to safer user install
            'is_virtual_env': False,
            'is_conda': False,
            'is_system_install': False,
            'python_executable': sys.executable,
            'site_packages': None
        }

        # Detect virtual environment
        info['is_virtual_env'] = (
                hasattr(sys, 'real_prefix') or
                (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
        )

        # Detect conda environment
        info['is_conda'] = (
                'CONDA_DEFAULT_ENV' in os.environ or
                'conda' in sys.executable.lower() or
                os.path.exists(os.path.join(sys.prefix, 'conda-meta'))
        )

        # Get site-packages directory
        try:
            import payloadprotector
            pkg_location = os.path.dirname(payloadprotector.__file__)
            info['site_packages'] = os.path.dirname(pkg_location)
            info['installation_path'] = pkg_location
        except ImportError:
            # Fallback methods
            if info['is_virtual_env'] or info['is_conda']:
                info['site_packages'] = sysconfig.get_path('purelib')
            else:
                # Try to determine if it's a user install
                user_site = site.getusersitepackages()
                system_site = sysconfig.get_path('purelib')

                # Check which one is more likely
                if os.path.exists(user_site) and user_site in sys.path:
                    info['site_packages'] = user_site
                    info['use_user_install'] = True
                else:
                    info['site_packages'] = system_site
                    info['use_user_install'] = not self._has_write_permissions(system_site)

        # Determine installation strategy
        if info['is_virtual_env'] or info['is_conda']:
            # In virtual environment, don't use --user flag
            info['use_user_install'] = False
        elif self.is_windows:
            # On Windows, check write permissions to determine strategy
            try:
                system_site = sysconfig.get_path('purelib')
                info['use_user_install'] = not self._has_write_permissions(system_site)
            except:
                info['use_user_install'] = True
        else:
            # On Unix-like systems
            if os.getuid() == 0:  # Running as root
                info['use_user_install'] = False
                info['is_system_install'] = True
            else:
                # Check if we're in a location that suggests user install
                user_site = site.getusersitepackages()
                if info['site_packages'] and user_site in info['site_packages']:
                    info['use_user_install'] = True
                else:
                    # Test write permissions
                    system_site = sysconfig.get_path('purelib')
                    info['use_user_install'] = not self._has_write_permissions(system_site)

        return info

    def _has_write_permissions(self, path):
        """Check if we have write permissions to a directory."""
        if not path or not os.path.exists(path):
            return False

        try:
            test_file = os.path.join(path, f'write_test_{os.getpid()}.tmp')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            return True
        except (PermissionError, OSError, IOError):
            return False

    def _get_python_executable(self):
        """Get the correct Python executable for the current platform."""
        # First, use the current interpreter (most reliable)
        current_python = sys.executable
        if current_python and os.path.exists(current_python):
            return current_python

        # Try different common Python executable names based on platform
        if self.is_windows:
            python_names = ['py', 'python', 'python3', 'python.exe']
        else:
            python_names = ['python3', 'python']

        for name in python_names:
            try:
                result = subprocess.run([name, '--version'],
                                        capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    # Verify it's the same Python version
                    if 'Python 3' in result.stdout or 'Python 2' in result.stdout:
                        return name
            except (subprocess.SubprocessError, FileNotFoundError, subprocess.TimeoutExpired):
                continue

        # Final fallback
        return current_python if current_python else 'python3'

    def _get_pip_executable(self):
        """Get the correct pip executable with enhanced detection."""
        python_exe = self._get_python_executable()

        # Method 1: Try python -m pip (most reliable)
        try:
            result = subprocess.run([python_exe, '-m', 'pip', '--version'],
                                    capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return [python_exe, '-m', 'pip']
        except:
            pass

        # Method 2: Try standalone pip executables
        pip_candidates = ['pip3', 'pip'] if not self.is_windows else ['pip', 'pip3']

        for pip_name in pip_candidates:
            try:
                result = subprocess.run([pip_name, '--version'],
                                        capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    # Verify it's for the right Python version
                    python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
                    if python_version in result.stdout or sys.executable in result.stdout:
                        return [pip_name]
            except:
                continue

        # Method 3: Try with full path
        python_dir = os.path.dirname(python_exe)
        for pip_name in ['pip3', 'pip']:
            pip_path = os.path.join(python_dir, pip_name)
            if self.is_windows:
                pip_path += '.exe'

            if os.path.exists(pip_path):
                try:
                    result = subprocess.run([pip_path, '--version'],
                                            capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        return [pip_path]
                except:
                    continue

        # Final fallback
        return [python_exe, '-m', 'pip']

    def _prepare_installation_command(self, source_path):
        """Prepare the installation command based on the environment."""
        pip_cmd = self._get_pip_executable()

        # Base installation command
        install_cmd = pip_cmd + [
            'install', source_path,
            '--force-reinstall',
            '--no-deps',
            '--upgrade'
        ]

        # Add user flag if needed (but not in virtual environments)
        if self.use_user_install and not (
                self.installation_info['is_virtual_env'] or self.installation_info['is_conda']):
            install_cmd.append('--user')
            print("[*] Installing to user directory")

        # Platform-specific adjustments
        if self.is_linux:
            # On Linux, sometimes we need to upgrade pip itself first
            try:
                upgrade_pip_cmd = pip_cmd + ['install', '--upgrade', 'pip']
                if self.use_user_install and not (
                        self.installation_info['is_virtual_env'] or self.installation_info['is_conda']):
                    upgrade_pip_cmd.append('--user')

                subprocess.run(upgrade_pip_cmd, capture_output=True, timeout=30)
            except:
                pass  # Continue even if pip upgrade fails

        return install_cmd

    def get_latest_version(self):
        """Fetch the latest version from GitHub releases."""
        try:
            print("[*] Checking for updates...")
            headers = {
                'User-Agent': 'PayloadProtector-Updater/1.1 (Cross-Platform)',
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
        """Download the latest version with improved error handling."""
        try:
            print(f"[*] Downloading version v{self.latest_version}...")
            print(f"[*] Download URL: {self.download_url}")

            headers = {
                'User-Agent': 'PayloadProtector-Updater/1.1 (Cross-Platform)',
                'Accept': 'application/zip'
            }

            # Use session for better connection handling
            session = requests.Session()
            session.headers.update(headers)

            response = session.get(self.download_url, stream=True, timeout=60)
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

            # Verify download
            if os.path.getsize(zip_path) == 0:
                raise Exception("Downloaded file is empty")

            return zip_path

        except requests.exceptions.RequestException as e:
            print(f"\n[!] Download failed: {e}")
            return None
        except Exception as e:
            print(f"\n[!] Unexpected error during download: {e}")
            return None

    def extract_update(self, zip_path, temp_dir):
        """Extract the downloaded update with better error handling."""
        try:
            print("[*] Extracting update...")

            # Verify zip file is valid
            if not zipfile.is_zipfile(zip_path):
                raise Exception("Downloaded file is not a valid ZIP archive")

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Check for malicious paths
                for member in zip_ref.namelist():
                    if os.path.isabs(member) or ".." in member:
                        raise Exception(f"Potentially unsafe path in archive: {member}")

                zip_ref.extractall(temp_dir)

            # Find the extracted folder (GitHub creates folder with commit hash)
            extracted_folders = [d for d in os.listdir(temp_dir)
                                 if os.path.isdir(os.path.join(temp_dir, d)) and d != '__MACOSX']

            if not extracted_folders:
                raise Exception("No extracted folder found")

            extracted_path = os.path.join(temp_dir, extracted_folders[0])

            # Verify required files exist
            required_files = ['setup.py', 'payloadprotector']
            for req_file in required_files:
                if not os.path.exists(os.path.join(extracted_path, req_file)):
                    raise Exception(f"Required file/directory missing: {req_file}")

            print(f"[+] Extracted to: {extracted_path}")
            return extracted_path

        except Exception as e:
            print(f"[!] Extraction failed: {e}")
            return None

    def install_update(self, extracted_path):
        """Install the extracted update with enhanced Linux support."""
        try:
            print("[*] Installing update...")
            print(f"[*] Installation environment: {self.installation_info}")

            # Prepare installation command
            install_cmd = self._prepare_installation_command(extracted_path)
            print(f"[*] Using command: {' '.join(install_cmd)}")

            # Run the installation
            env = os.environ.copy()

            # Set environment variables for better compatibility
            if self.is_linux:
                env['PYTHONUSERBASE'] = os.path.expanduser('~/.local')
                if self.use_user_install:
                    env['PIP_USER'] = '1'

            result = subprocess.run(
                install_cmd,
                capture_output=True,
                text=True,
                timeout=120,
                env=env,
                cwd=extracted_path
            )

            if result.returncode != 0:
                print(f"[!] Installation failed with return code: {result.returncode}")
                print(f"[!] stdout: {result.stdout}")
                print(f"[!] stderr: {result.stderr}")

                # Try alternative installation method
                return self._try_alternative_install(extracted_path)

            print(f"[+] Installation completed successfully")
            print(f"[*] stdout: {result.stdout}")

            # Install dependencies
            self._install_dependencies(extracted_path)

            return True

        except subprocess.TimeoutExpired:
            print("[!] Installation timed out")
            return False
        except Exception as e:
            print(f"[!] Installation failed: {e}")
            return self._try_alternative_install(extracted_path)

    def _try_alternative_install(self, extracted_path):
        """Try alternative installation method using setup.py directly."""
        try:
            print("[*] Trying alternative installation method...")

            python_exe = self._get_python_executable()
            original_cwd = os.getcwd()

            try:
                os.chdir(extracted_path)

                # Prepare setup.py command
                setup_cmd = [python_exe, 'setup.py', 'install']

                if self.use_user_install and not (
                        self.installation_info['is_virtual_env'] or self.installation_info['is_conda']):
                    setup_cmd.append('--user')

                setup_cmd.append('--force')

                print(f"[*] Running: {' '.join(setup_cmd)}")

                env = os.environ.copy()
                if self.is_linux and self.use_user_install:
                    env['PYTHONUSERBASE'] = os.path.expanduser('~/.local')

                result = subprocess.run(
                    setup_cmd,
                    capture_output=True,
                    text=True,
                    timeout=120,
                    env=env
                )

                if result.returncode != 0:
                    print(f"[!] Alternative installation also failed: {result.stderr}")
                    return False

                print("[+] Alternative installation successful")
                return True

            finally:
                os.chdir(original_cwd)

        except Exception as e:
            print(f"[!] Alternative installation failed: {e}")
            return False

    def _install_dependencies(self, extracted_path):
        """Install dependencies with better Linux support."""
        try:
            requirements_path = os.path.join(extracted_path, 'requirements.txt')
            if not os.path.exists(requirements_path):
                print("[*] No requirements.txt found, skipping dependency installation")
                return

            print("[*] Installing dependencies...")

            pip_cmd = self._get_pip_executable()
            deps_cmd = pip_cmd + ['install', '-r', requirements_path]

            if self.use_user_install and not (
                    self.installation_info['is_virtual_env'] or self.installation_info['is_conda']):
                deps_cmd.append('--user')

            env = os.environ.copy()
            if self.is_linux and self.use_user_install:
                env['PYTHONUSERBASE'] = os.path.expanduser('~/.local')

            result = subprocess.run(deps_cmd, capture_output=True, text=True, timeout=120, env=env)

            if result.returncode == 0:
                print("[+] Dependencies installed successfully")
            else:
                print(f"[!] Some dependencies may not have been installed: {result.stderr}")

        except Exception as e:
            print(f"[*] Warning: Could not install dependencies: {e}")

    def _verify_installation(self):
        """Verify that the installation was successful with better error reporting."""
        try:
            python_exe = self._get_python_executable()

            # Test package import
            test_cmd = [python_exe, '-c', 'import payloadprotector; print("Import OK")']
            result = subprocess.run(test_cmd, capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                print("[+] Package import verification: OK")
            else:
                print(f"[!] Package import failed: {result.stderr}")

                # Try to provide more information
                path_cmd = [python_exe, '-c', 'import sys; print("\\n".join(sys.path))']
                path_result = subprocess.run(path_cmd, capture_output=True, text=True, timeout=5)
                if path_result.returncode == 0:
                    print(f"[*] Python path: {path_result.stdout}")

                return False

            # Test CLI tool
            cli_test_cmd = [python_exe, '-c', 'from payloadprotector.cli import main; print("CLI OK")']
            result = subprocess.run(cli_test_cmd, capture_output=True, text=True, timeout=10)

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
            # Clear import cache
            if hasattr(sys, 'path_importer_cache'):
                sys.path_importer_cache.clear()

            # Refresh sys.path for user installations
            if self.use_user_install:
                user_site = site.getusersitepackages()
                if user_site and os.path.exists(user_site) and user_site not in sys.path:
                    sys.path.insert(0, user_site)

            # Refresh pkg_resources working set
            try:
                pkg_resources._initialize_master_working_set()
            except:
                pass

            # Clear module cache for payloadprotector
            modules_to_clear = [name for name in sys.modules.keys() if name.startswith('payloadprotector')]
            for module_name in modules_to_clear:
                del sys.modules[module_name]

        except Exception as e:
            print(f"[*] Environment refresh warning: {e}")

    def update(self, force=False):
        """Perform the complete update process with enhanced Linux support."""
        print(f"[*] Payload Protector Cross-Platform Updater")
        print(f"[*] Current version: {self.current_version}")
        print(f"[*] Platform: {self.system}")
        print(f"[*] Python: {sys.version}")
        print(f"[*] Installation info: {self.installation_info}")

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

            # Install update
            if self.install_update(extracted_path):
                print("[+] Update installation completed!")
                print(f"[*] Updated from {self.current_version} to v{self.latest_version}")

                # Refresh environment
                self._refresh_environment()

                # Verify installation
                if self._verify_installation():
                    print("[+] Installation verified successfully")

                    # Linux-specific post-installation steps
                    if self.is_linux:
                        self._linux_post_install()

                    print("[*] Please restart your terminal or run the following:")
                    if self.is_linux:
                        print("    hash -r  # Refresh command cache")
                        print("    source ~/.bashrc  # Reload shell configuration")
                    else:
                        print("    Restart your command prompt/terminal")

                    return True
                else:
                    print("[!] Installation verification failed")
                    return False
            else:
                print("[!] Update failed")
                return False

    def _linux_post_install(self):
        """Linux-specific post-installation steps."""
        try:
            # Ensure ~/.local/bin is in PATH for user installations
            if self.use_user_install:
                local_bin = os.path.expanduser('~/.local/bin')

                if os.path.exists(local_bin):
                    # Check if it's in PATH
                    current_path = os.environ.get('PATH', '')
                    if local_bin not in current_path:
                        print(f"[*] Note: {local_bin} should be in your PATH")
                        print(f"[*] Add this to your ~/.bashrc or ~/.profile:")
                        print(f'    export PATH="$HOME/.local/bin:$PATH"')

                # Check if the payloadprotector command is available
                pp_script = os.path.join(local_bin, 'payloadprotector')
                if os.path.exists(pp_script):
                    # Make sure it's executable
                    st = os.stat(pp_script)
                    if not st.st_mode & stat.S_IEXEC:
                        os.chmod(pp_script, st.st_mode | stat.S_IEXEC)
                        print(f"[*] Made {pp_script} executable")

        except Exception as e:
            print(f"[*] Post-install setup warning: {e}")

    def check_only(self):
        """Only check for updates without installing."""
        print(f"[*] Payload Protector Update Checker")
        print(f"[*] Current version: {self.current_version}")
        print(f"[*] Platform: {self.system}")
        print(f"[*] Installation environment: {self.installation_info}")

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
        description="Payload Protector Cross-Platform Updater v1.1",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  pp-update --check    # Check for updates
  pp-update            # Install latest update
  pp-update --force    # Force reinstall latest version

Supported platforms: Windows, Linux, macOS
Supported environments: System install, User install, Virtual environments, Conda

The updater will automatically:
- Detect your Python environment (system/user/virtual/conda)
- Use appropriate installation method
- Handle permissions correctly across platforms
- Verify installation success
- Provide platform-specific instructions
        """
    )
    parser.add_argument("--check", action="store_true",
                        help="Check for updates without installing")
    parser.add_argument("--force", action="store_true",
                        help="Force update even if no new version is available")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Enable verbose output")
    parser.add_argument("--user", action="store_true",
                        help="Force user installation (--user flag)")
    parser.add_argument("--system", action="store_true",
                        help="Force system-wide installation")

    args = parser.parse_args()

    # Enable verbose logging if requested
    if args.verbose:
        import logging
        logging.basicConfig(level=logging.DEBUG)

    updater = PayloadProtectorUpdater()

    # Override installation mode if flags are provided
    if args.user and args.system:
        print("[!] Cannot specify both --user and --system flags")
        sys.exit(1)
    elif args.user:
        updater.use_user_install = True
        print("[*] Forcing user installation mode")
    elif args.system:
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