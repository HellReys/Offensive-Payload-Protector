# encryptor.py
"""
AES-256 Encryption Module
Handles secure key generation and file encryption.
"""

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes
import secrets
import binascii
from hashlib import sha256


def generate_aes_key(key_input=None):
    """
    Generate a secure AES-256 key.

    Args:
        key_input: None (auto-generate), hex string, or password string

    Returns:
        32-byte AES key
    """
    if key_input is None:
        return secrets.token_bytes(32)

    if isinstance(key_input, str):
        if len(key_input) == 64 and all(c in '0123456789abcdef' for c in key_input.lower()):
            return binascii.unhexlify(key_input)
        return sha256(key_input.encode()).digest()

    raise ValueError("Key must be 32-byte hex string or password")


def encrypt_payload(input_file, output_file, key=None):
    """
    Encrypt file with AES-256-CBC.

    Returns:
        dict: {
            'aes_key_hex': str,
            'iv_hex': str,
            'output_file': str
        }
    """
    key = generate_aes_key(key)
    iv = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)

    with open(input_file, 'rb') as f:
        plaintext = f.read()

    ciphertext = cipher.encrypt(pad(plaintext, AES.block_size))

    with open(output_file, 'wb') as f:
        f.write(iv + ciphertext)

    return {
        'aes_key_hex': key.hex(),
        'iv_hex': iv.hex(),
        'output_file': output_file
    }