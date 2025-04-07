> ⚠️ **Disclaimer:** This project is for **educational purposes only**. The author is not responsible for any misuse or damage caused by this tool.

# Offensive Payload Protector  
**Hybrid encryption tool for Red Team operations.**  

## Features  
- AES-256 + XOR obfuscation for payload encryption.  
- Generates in-memory executable stubs to bypass AV.  
- Supports Windows/Linux payloads (PE/ELF).  

## Usage  
```bash
python payload_encryptor.py --input shellcode.bin --output encrypted.bin --key S3cr3tK3y
