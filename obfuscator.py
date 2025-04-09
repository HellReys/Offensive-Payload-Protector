from hashlib import sha256
import os

def xor_encrypt(data, key):
    return bytes([data[i] ^ key[i % len(key)] for i in range(len(data))])

def obfuscate_key(aes_key, xor_key=None):
    """Returns: (obfuscated_key_hex, xor_key_hex)"""
    aes_key_hashed = sha256(aes_key.encode()).digest()
    xor_key = xor_key or os.urandom(16)  # Generate random XOR key if none provided
    obfuscated = xor_encrypt(aes_key_hashed, xor_key)
    return obfuscated.hex(), xor_key.hex()