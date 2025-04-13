> ⚠️ **Disclaimer:** This project is for **educational purposes only**. The author is not responsible for any misuse or damage caused by this tool.

# Offensive Payload Protector  
**Hybrid encryption tool for Red Team operations.**  

## Features  
- AES-256 + XOR obfuscation for payload encryption.  
- Generates in-memory executable stubs to bypass AV.  
- Supports Windows/Linux payloads (PE/ELF).
- CLI and API support.

## 📦 Installation
```bash
git clone https://github.com/HellReys/Offensive-Payload-Protector.git
cd Offensive-Payload-Protector
python setup.py install
```
## Encrypt the Payload 
```bash
payloadprotector --input {YOUR PAYLOAD FILE} --output {ENCRYPTED FILE NAME} --key {"YOUR SECRET PASSWORD"} --xor_key {"YOUR XOR KEY"}
```
## Example
```bash
payloadprotector --input payload.bin --output encrypted.bin --key "MySecretPassword" --xor_key "1a2b3c4d"
```
## Execute
```bash
python decryptor.py
# or on Linux:
./decryptor.py
```


## 🔧 Technical Details
| Component       | Technology Used |
|----------------|----------------|
| Encryption     | AES-256-CBC    |
| Key Derivation | SHA-256        |
| Obfuscation    | XOR            |


## ❓ FAQ
### Q: Why am I getting "Access Denied" errors?
A: Disable your AV during testing as it may block memory operations.


## 💖 Support This Project
If you like this project, consider supporting me on Patreon:  
- [Buy Me a Coffee](https://buymeacoffee.com/hellreys)
- [PayPal](https://paypal.me/berkali06?country.x=LT&locale.x=en_US)
