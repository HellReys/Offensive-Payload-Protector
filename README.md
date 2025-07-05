# Payload Protector

> ⚠️ **Disclaimer:** This project is for **educational purposes only**. The author is not responsible for any misuse or damage caused by this tool.

**Advanced hybrid encryption tool for Red Team operations and penetration testing.**

[![Version](https://img.shields.io/badge/version-1.1.0-blue.svg)](https://github.com/HellReys/Offensive-Payload-Protector/releases)
[![Python](https://img.shields.io/badge/python-3.6+-green.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-red.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)](https://github.com/HellReys/Offensive-Payload-Protector)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/HellReys/Offensive-Payload-Protector)

## 🚀 Features

### 🔐 Military-Grade Encryption
- **AES-256-CBC encryption** with cryptographically secure random keys
- **SHA-256 fallback** for password-based encryption
- **Auto-generated IVs** for each encryption operation
- **Secure key generation** using `secrets.token_bytes(32)`

### 🛡️ Advanced Obfuscation
- **XOR obfuscation layer** with ephemeral keys
- **Dynamic key generation** - unique keys per session
- **Anti-static analysis** protection
- **Multi-layer security** approach

### 💻 Cross-Platform Payload Execution
- **Windows PE execution** via VirtualProtect + CFUNCTYPE
- **Linux ELF execution** via mmap + PROT_EXEC
- **macOS support** for universal compatibility
- **In-memory execution** - no disk artifacts
- **Anti-sandbox techniques** built-in

### 🔄 Automatic Update System
- **GitHub releases integration** for seamless updates
- **One-click update mechanism** with backup/rollback
- **Version management** and compatibility checking
- **Cross-platform update support**

## 📦 Installation

### Requirements
- Python 3.6+ (Python 3.8+ recommended)
- pip package manager
- Internet connection for updates

### Quick Install

#### Linux/macOS
```bash
git clone https://github.com/HellReys/Offensive-Payload-Protector.git
cd Offensive-Payload-Protector
python3 setup.py install
```

#### Windows
```bash
git clone https://github.com/HellReys/Offensive-Payload-Protector.git
cd Offensive-Payload-Protector
pip install -r requirements.txt
python setup.py install
```

### Alternative Installation Methods

#### User Installation (Recommended)
```bash
python setup.py install --user
```

#### Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows
python setup.py install
```

#### Development Installation
```bash
pip install -e .
```

## 🔧 Usage

### Basic Encryption
```bash
# Auto-generate everything (recommended for maximum security)
payloadprotector --input payload.bin --output encrypted.bin

# With custom password
payloadprotector --input payload.bin --output encrypted.bin --key "MySecretPassword"

# Full custom encryption
payloadprotector --input payload.bin --output encrypted.bin --key "MySecretPassword" --xor_key "1a2b3c4d5e6f7890"
```

### Execution
```bash
# Execute the encrypted payload
python decryptor.py

# Linux (if executable)
./decryptor.py
```

### Update Operations
```bash
# Check for updates
payloadprotector --check-update

# Install latest update
payloadprotector --update

# Force update
payloadprotector --force-update

# Show version information
payloadprotector --version
```

## 📋 Command Reference

### Core Commands
| Command | Description | Example |
|---------|-------------|---------|
| `--input` | Input payload file | `--input payload.bin` |
| `--output` | Output encrypted file | `--output encrypted.bin` |
| `--key` | AES key (hex/password/auto) | `--key "MyPassword"` |
| `--xor_key` | Custom XOR key (32-byte hex) | `--xor_key "1a2b3c..."` |

### Update Commands
| Command | Description | Example |
|---------|-------------|---------|
| `--check-update` | Check for updates | `payloadprotector --check-update` |
| `--update` | Install latest version | `payloadprotector --update` |
| `--force-update` | Force reinstall | `payloadprotector --force-update` |
| `--version` | Show version info | `payloadprotector --version` |

### Utility Commands
| Command | Description | Example |
|---------|-------------|---------|
| `--quiet` | Suppress banner | `payloadprotector --quiet --input ...` |
| `--help` | Show help | `payloadprotector --help` |

### Standalone Update Tool
```bash
pp-update --check      # Check for updates
pp-update              # Install updates
pp-update --force      # Force update
pp-update --verbose    # Verbose output
```

## 🔬 Technical Specifications

### Encryption Details
| Component | Technology | Security Level |
|-----------|------------|----------------|
| **Symmetric Encryption** | AES-256-CBC | Military-grade |
| **Key Generation** | `secrets.token_bytes(32)` | Cryptographically secure |
| **Initialization Vector** | Auto-generated per operation | Unique per encryption |
| **Key Derivation** | SHA-256 (fallback) | Industry standard |
| **Obfuscation** | XOR with ephemeral keys | Anti-static analysis |

### Platform Support
| Platform | Execution Method | Status |
|----------|------------------|--------|
| **Windows** | VirtualProtect + CFUNCTYPE | ✅ Fully supported |
| **Linux** | mmap + PROT_EXEC | ✅ Fully supported |
| **macOS** | mmap + PROT_EXEC | ✅ Fully supported |

### Security Features
- 🔒 **Memory-only execution** - No disk artifacts
- 🛡️ **Anti-sandbox delays** - Evasion techniques
- 🔑 **Dynamic key generation** - Unique per session
- 🚫 **Anti-static analysis** - XOR obfuscation
- 🔄 **Secure updates** - HTTPS-only downloads

## 🛠️ Advanced Usage

### Custom Encryption Scenarios
```bash
# High-security payload with custom keys
payloadprotector --input sensitive.bin --output encrypted.bin \
  --key "$(openssl rand -hex 32)" --xor_key "$(openssl rand -hex 32)"

# Batch processing
for payload in *.bin; do
  payloadprotector --input "$payload" --output "encrypted_${payload}"
done
```

### Environment-Specific Installation
```bash
# Virtual environment
python -m venv payloadprotector-env
source payloadprotector-env/bin/activate
pip install -r requirements.txt
python setup.py install

# Conda environment
conda create -n payloadprotector python=3.9
conda activate payloadprotector
python setup.py install
```

## 🔍 Troubleshooting

### Common Issues and Solutions

#### "Access Denied" or "Permission Denied"
```bash
# Solution: Disable AV temporarily or run as administrator
sudo payloadprotector --input payload.bin --output encrypted.bin
```

#### "Module not found" after installation
```bash
# Solution: Refresh your PATH or use full path
hash -r  # Linux/macOS
# or restart terminal

# Alternative: Use full path
python -m payloadprotector.cli --input payload.bin --output encrypted.bin
```

#### Update failures
```bash
# Solution: Manual update or check permissions
pp-update --force --verbose
# or
pip install --upgrade --force-reinstall payloadprotector
```

### Debugging Options
```bash
# Verbose output
payloadprotector --input payload.bin --output encrypted.bin --verbose

# Quiet mode (minimal output)
payloadprotector --input payload.bin --output encrypted.bin --quiet
```

## 📊 Performance Benchmarks

### Encryption Speed
| File Size | Encryption Time | Memory Usage |
|-----------|----------------|--------------|
| 1 MB | ~0.1s | ~2 MB |
| 10 MB | ~0.8s | ~12 MB |
| 100 MB | ~7.2s | ~105 MB |

### Platform Performance
| Platform | Avg. Encryption Speed | Memory Overhead |
|----------|----------------------|----------------|
| Windows 10/11 | 15 MB/s | 2x file size |
| Linux | 18 MB/s | 1.8x file size |
| macOS | 16 MB/s | 2x file size |

## 🔄 Update System

### Automatic Updates
The tool includes a comprehensive update system that:
- Checks GitHub releases automatically
- Downloads updates securely over HTTPS
- Verifies downloads and performs integrity checks
- Creates automatic backups before updates
- Supports rollback on failed updates

### Update Workflow
```bash
# Check for updates
payloadprotector --check-update

# If updates available
payloadprotector --update

# Verify installation
payloadprotector --version
```

## 🧪 Testing

### Running Tests
```bash
# Install test dependencies
pip install -e .[test]

# Run tests
pytest tests/

# Run with coverage
pytest --cov=payloadprotector tests/
```

### Manual Testing
```bash
# Test basic encryption
echo "Test payload" > test.bin
payloadprotector --input test.bin --output test.enc
python decryptor.py

# Test update system
payloadprotector --check-update
```

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup
```bash
git clone https://github.com/HellReys/Offensive-Payload-Protector.git
cd Offensive-Payload-Protector
pip install -e .[dev]
```

## 📝 Changelog

### v1.1.0 (2025-01-19)
- ✅ **Initial stable release**
- ✅ **AES-256-CBC encryption** implementation
- ✅ **XOR obfuscation layer** with ephemeral keys
- ✅ **Cross-platform payload execution** (Windows/Linux/macOS)
- ✅ **Automatic update system** with GitHub integration
- ✅ **Version management** and rollback functionality
- ✅ **Comprehensive CLI** with extensive options
- ✅ **Anti-sandbox techniques** and evasion capabilities
- ✅ **Memory-only execution** for stealth operations

### Planned Features (v1.2.0)
- 🔄 **Multi-threading support** for faster encryption
- 🔄 **Plugin system** for custom obfuscation methods
- 🔄 **GUI interface** for non-technical users
- 🔄 **Advanced evasion techniques**
- 🔄 **Payload compression** options

## 🎯 Use Cases

### Red Team Operations
- Payload delivery in penetration testing
- Bypassing antivirus detection
- Secure payload storage and transport
- Multi-stage payload deployment

### Security Research
- Malware analysis evasion techniques
- Encryption algorithm testing
- Cross-platform compatibility research
- Anti-sandbox technique development

### Educational Purposes
- Understanding encryption mechanisms
- Learning about payload protection
- Studying evasion techniques
- Security tool development

## 📚 Documentation

### Community
- [Issues](https://github.com/HellReys/Offensive-Payload-Protector/issues) - Bug reports and feature requests

## 💖 Support This Project

If you find this tool useful, consider supporting its development:

- ⭐ **Star this repository** on GitHub
- 🐛 **Report bugs** and suggest features
- 💝 **Contribute code** and documentation
- ☕ **Buy me a coffee**: [buymeacoffee.com/hellreys](https://buymeacoffee.com/hellreys)
- 💎 **GitHub Sponsors**: [github.com/sponsors/HellReys](https://github.com/sponsors/HellReys)

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

### Third-Party Licenses
- **PyCryptodome**: BSD License
- **Requests**: Apache 2.0 License
- **Packaging**: Apache 2.0 License

## ⚠️ Legal Notice

This tool is intended for **authorized security testing and educational purposes only**. Users are fully responsible for complying with all applicable laws and regulations in their jurisdiction.

### Responsible Use Guidelines
- ✅ **Only use on systems you own or have explicit permission to test**
- ✅ **Ensure compliance with local laws and regulations**
- ✅ **Use for educational and authorized security testing only**
- ❌ **Do not use for malicious purposes or unauthorized access**
- ❌ **Do not use to harm individuals or organizations**

The author and contributors assume **no responsibility** for misuse of this software.

---

<div align="center">

**Made with ❤️ by [HellReys](https://github.com/HellReys)**

[⬆️ Back to top](#payload-protector)

</div>
