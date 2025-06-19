> ⚠️ **Disclaimer:** This project is for **educational purposes only**. The author is not responsible for any misuse or damage caused by this tool.

# Offensive Payload Protector  
**Hybrid encryption tool for Red Team operations.**  

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/HellReys/Offensive-Payload-Protector/releases)
[![Python](https://img.shields.io/badge/python-3.6+-green.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-red.svg)](LICENSE)

## 🚀 Features  

### Core Security  
- **Military-grade encryption**  
  - AES-256-CBC with `secrets.token_bytes(32)` for true random keys  
  - SHA-256 fallback for password-based encryption  
  - Auto-generated IVs for each encryption  

### Advanced Obfuscation  
- **XOR layer with ephemeral keys**  
  - Uses `secrets.token_bytes(32)` for obfuscation keys  
  - Different key per session by default  

### Payload Delivery  
- **AV-evading stubs**  
  - In-memory execution (no disk writes)  
  - Cross-platform support:  
    - Windows PE files (Via VirtualProtect + CFUNCTYPE)  
    - Linux ELF binaries (Via mmap + PROT_EXEC)

### Update System 🆕
- **Automatic update checking**
- **One-click updates from GitHub releases**
- **Backup and rollback functionality**
- **Version management**

## 📦 Installation
```bash
git clone https://github.com/HellReys/Offensive-Payload-Protector.git
cd Offensive-Payload-Protector
pip install -r requirements.txt
python setup.py install
```

## 🔄 Keeping Updated

### Check for Updates
```bash
# Check if updates are available
payloadprotector --check-update
```

### Update to Latest Version
```bash
# Update to the latest version
payloadprotector --update

# Force update (even if no new version detected)
payloadprotector --force-update
```

### Version Information
```bash
# Show current version and build info
payloadprotector --version
```

## 🔐 Usage

### Encrypt the Payload 
```bash
# Auto-generate everything (recommended)
payloadprotector --input {YOUR_PAYLOAD_FILE} --output {ENCRYPTED_FILE_NAME}

# Advanced usage with custom keys
payloadprotector --input {YOUR_PAYLOAD_FILE} --output {ENCRYPTED_FILE_NAME} --key {"YOUR_SECRET_PASSWORD"} --xor_key {"YOUR_XOR_KEY"}
```

### Examples
```bash
# Auto-generate everything
payloadprotector --input payload.bin --output encrypted.bin

# Custom password-based encryption
payloadprotector --input payload.bin --output encrypted.bin --key "MySecretPassword"

# Full custom encryption
payloadprotector --input payload.bin --output encrypted.bin --key "MySecretPassword" --xor_key "1a2b3c4d5e6f7890"
```

### Execute Payload
```bash
# Run the generated decryptor
python decryptor.py

# On Linux (if made executable)
./decryptor.py
```

## 🔧 Technical Details  
| Component            | Technology Used                     | Security Notes                          |
|----------------------|-------------------------------------|-----------------------------------------|
| Key Generation       | `secrets.token_bytes(32)`           | Cryptographically secure RNG            |
| Encryption           | AES-256-CBC                         | IV automatically generated              |
| Key Obfuscation      | XOR with `secrets.token_bytes(32)`  | Prevents static analysis                |
| Fallback Key Input   | SHA-256 (when password provided)    | Maintains backwards compatibility      |
| Update System        | GitHub Releases API                 | Secure HTTPS downloads with backup     |

## 📋 Command Reference

### Main Commands
```bash
# Encryption (required arguments)
--input FILE        Input payload file
--output FILE       Output encrypted file

# Optional encryption parameters
--key STRING        AES key (hex/password/auto-generated)
--xor_key HEX       Custom XOR key (32-byte hex)
```

### Update Commands
```bash
--check-update      Check for available updates
--update           Update to latest version
--force-update     Force update regardless of version
--version          Show version information
```

### Standalone Update Tool
```bash
# Alternative update method
pp-update --check      # Check for updates
pp-update              # Perform update
pp-update --force      # Force update
```

## 🛡️ Security Features

### Anti-Detection
- **Dynamic key generation** - Each encryption uses unique keys
- **Memory-only execution** - No disk artifacts during payload execution  
- **Cross-platform stubs** - Native execution on Windows/Linux
- **Anti-sandbox delays** - Built-in evasion techniques

### Update Security
- **HTTPS-only downloads** - Secure update channel
- **Automatic backup** - Rollback capability on failed updates
- **Version verification** - Semantic version checking
- **Integrity validation** - Download verification

## ❓ FAQ

### Q: Why am I getting "Access Denied" errors?
A: Disable your AV during testing as it may block memory operations.

### Q: How do I rollback an update?
A: Failed updates automatically rollback. Manual backups are stored as `{installation_dir}_backup_{version}`.

### Q: Can I update without internet?
A: No, the update system requires internet access to check GitHub releases.

### Q: Are updates automatic?
A: No, updates are manual. Use `--check-update` to check and `--update` to install.

## 📝 Changelog

### v1.1.0 (2025-06-19)
- ✅ Initial release
- ✅ AES-256-CBC encryption
- ✅ XOR obfuscation layer
- ✅ Cross-platform payload execution
- ✅ Automatic update system
- ✅ Version management
- ✅ Backup and rollback functionality

## 💖 Support This Project
If you like this project, consider supporting me:  
- [Buy Me a Coffee](https://buymeacoffee.com/hellreys)
- [GitHub Sponsors](https://github.com/sponsors/HellReys)

## 📜 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Legal Notice
This tool is intended for authorized security testing and educational purposes only. Users are responsible for complying with applicable laws and regulations. The author assumes no responsibility for misuse of this software.