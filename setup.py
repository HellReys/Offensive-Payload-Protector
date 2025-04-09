from setuptools import setup, find_packages

setup(
    name="payloadprotector",
    version="1.0.0",
    author="Your Name",
    description="Offensive Payload Encryption Toolkit",
    packages=find_packages(),
    install_requires=[
        'pycryptodome>=3.18.0',
        'argparse>=1.4.0'
    ],
    entry_points={
        'console_scripts': [
            'payloadprotector=payloadprotector.cli:main',
        ],
    },
    python_requires='>=3.6',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)