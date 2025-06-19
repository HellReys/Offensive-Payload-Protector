#!/usr/bin/env python3
"""
Version information for Payload Protector
This file is automatically updated by the build system.
"""

__version__ = "1.1.0"
__build__ = "stable"
__release_date__ = "2025-06-19"
__author__ = "HellReys"
__description__ = "Hybrid encryption tool for Red Team operations"

# GitHub repository information
REPO_OWNER = "HellReys"
REPO_NAME = "Offensive-Payload-Protector"
REPO_URL = f"https://github.com/{REPO_OWNER}/{REPO_NAME}"

# Update URLs
API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/latest"
DOWNLOAD_URL = f"{REPO_URL}/archive/refs/heads/main.zip"

def get_version_info():
    """Return formatted version information."""
    return f"""
Payload Protector v{__version__} ({__build__})
Released: {__release_date__}
Author: {__author__}
Repository: {REPO_URL}
    """.strip()

def get_version():
    """Return version string."""
    return __version__

def get_build():
    """Return build type."""
    return __build__

def is_stable():
    """Check if this is a stable release."""
    return __build__ == "stable"