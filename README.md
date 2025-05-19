> ⚠️ **Disclaimer:** This project is for **educational purposes only**. The author is not responsible for any misuse or damage caused by this tool.

# Offensive Payload Protector  
**Hybrid encryption tool for Red Team operations.**  

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

## 📦 Installation
```bash
git clone https://github.com/HellReys/Offensive-Payload-Protector.git
cd Offensive-Payload-Protector
python setup.py install
```
## Encrypt the Payload 
```bash
## Auto Generates Everything
payloadprotector --input {YOUR PAYLOAD FILE} --output {ENCRYPTED FILE NAME}
## Advanced usage with custom keys
payloadprotector --input {YOUR PAYLOAD FILE} --output {ENCRYPTED FILE NAME} --key {"YOUR SECRET PASSWORD"} --xor_key {"YOUR XOR KEY"}
```
## Example
```bash
## Auto Generates Everything
payloadprotector --input payload.bin --output encrypted.bin
## Advanced usage with custom keys
payloadprotector --input payload.bin --output encrypted.bin --key "MySecretPassword" --xor_key "1a2b3c4d"
```
## Execute
```bash
python decryptor.py
# or on Linux:
./decryptor.py
```


## 🔧 Technical Details  
| Component            | Technology Used                     | Security Notes                          |
|----------------------|-------------------------------------|-----------------------------------------|
| Key Generation       | `secrets.token_bytes(32)`           | Cryptographically secure RNG            |
| Encryption           | AES-256-CBC                         | IV automatically generated              |
| Key Obfuscation      | XOR with `secrets.token_bytes(32)`  | Prevents static analysis                |
| Fallback Key Input   | SHA-256 (when password provided)    | Maintains backwards compatibility      |


## ❓ FAQ
### Q: Why am I getting "Access Denied" errors?
A: Disable your AV during testing as it may block memory operations.


## 💖 Support This Project
If you like this project, consider supporting me:  
- [Buy Me a Coffee](https://buymeacoffee.com/hellreys)
- [GitHub Sponsors](https://github.com/sponsors/HellReys)
