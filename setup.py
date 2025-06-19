from setuptools import setup, find_packages
import os

# Read version from version.py
version_file = os.path.join(os.path.dirname(__file__), 'payloadprotector', 'version.py')
version_dict = {}
with open(version_file) as f:
    exec(f.read(), version_dict)

# Read README for long description
readme_file = os.path.join(os.path.dirname(__file__), 'README.md')
try:
    with open(readme_file, 'r', encoding='utf-8') as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = "Hybrid encryption tool for Red Team operations"

setup(
    name="payloadprotector",
    version=version_dict['__version__'],
    author=version_dict['__author__'],
    author_email="contact@hellreys.com",
    description=version_dict['__description__'],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=version_dict['REPO_URL'],
    packages=find_packages(),
    install_requires=[
        'pycryptodome>=3.18.0',
        'argparse>=1.4.0',
        'requests>=2.25.0',
        'packaging>=21.0',
    ],
    extras_require={
        'dev': [
            'pytest>=6.0',
            'black>=21.0',
            'flake8>=3.8',
        ]
    },
    entry_points={
        'console_scripts': [
            'payloadprotector=payloadprotector.cli:main',
            'pp-update=payloadprotector.updater:main',
        ],
    },
    python_requires='>=3.6',
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
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords="security encryption payload redteam pentest",
    project_urls={
        "Bug Reports": f"{version_dict['REPO_URL']}/issues",
        "Source": version_dict['REPO_URL'],
        "Documentation": f"{version_dict['REPO_URL']}/wiki",
        "Funding": "https://buymeacoffee.com/hellreys",
    },
)