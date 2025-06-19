#!/usr/bin/env python3
from setuptools import setup, find_packages
import os
import sys
import platform

# Read version from version.py
version_file = os.path.join(os.path.dirname(__file__), 'payloadprotector', 'version.py')
version_dict = {}
try:
    with open(version_file) as f:
        exec(f.read(), version_dict)
except FileNotFoundError:
    print("Error: version.py not found. Please ensure you have the complete source code.")
    sys.exit(1)

# Read README for long description
readme_file = os.path.join(os.path.dirname(__file__), 'README.md')
try:
    with open(readme_file, 'r', encoding='utf-8') as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = version_dict.get('__description__', "Hybrid encryption tool for Red Team operations")

# Platform-specific requirements
install_requires = [
    'pycryptodome>=3.18.0',
    'requests>=2.25.0',
    'packaging>=21.0',
]

# Add platform-specific dependencies
if platform.system() == "Windows":
    # Windows-specific dependencies
    install_requires.extend([
        'pywin32>=227;platform_system=="Windows"',
    ])
elif platform.system() == "Linux":
    # Linux-specific dependencies (if any)
    pass

# Development dependencies
extras_require = {
    'dev': [
        'pytest>=6.0',
        'black>=21.0',
        'flake8>=3.8',
        'mypy>=0.910',
        'pytest-cov>=2.12.0',
    ],
    'test': [
        'pytest>=6.0',
        'pytest-cov>=2.12.0',
    ],
    'build': [
        'wheel>=0.36.0',
        'twine>=3.4.0',
    ]
}

# Console scripts for cross-platform compatibility
console_scripts = [
    'payloadprotector=payloadprotector.cli:main',
    'pp-update=payloadprotector.updater:main',
]

# Add platform-specific aliases
if platform.system() == "Windows":
    console_scripts.extend([
        'pp.exe=payloadprotector.cli:main',
        'payloadprotector.exe=payloadprotector.cli:main',
    ])

setup(
    name="payloadprotector",
    version=version_dict['__version__'].lstrip('v'),  # Remove 'v' prefix for setuptools
    author=version_dict['__author__'],
    author_email="contact.berkalicakir@gmail.com",
    description=version_dict['__description__'],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=version_dict['REPO_URL'],

    # Package configuration
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,

    # Dependencies
    install_requires=install_requires,
    extras_require=extras_require,
    python_requires='>=3.6',

    # Entry points
    entry_points={
        'console_scripts': console_scripts,
    },

    # Package data
    package_data={
        'payloadprotector': [
            'version.py',
            '*.txt',
            '*.md',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Information Technology",
        "Topic :: Security",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords="security encryption payload redteam pentest",
    project_urls={
        "Bug Reports": f"{version_dict['REPO_URL']}/issues",
        "Source": version_dict['REPO_URL'],
        "Documentation": f"{version_dict['REPO_URL']}/wiki",
        "Fundings": "https://buymeacoffee.com/hellreys\n"
                   "https://github.com/sponsors/HellReys",

    },
)