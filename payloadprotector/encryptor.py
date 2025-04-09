from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes
from hashlib import sha256


def encrypt_payload(input_file, output_file, key):
    iv = get_random_bytes(16)
    aes_key = sha256(key.encode()).digest()  # 32-byte key
    cipher = AES.new(aes_key, AES.MODE_CBC, iv)

    with open(input_file, 'rb') as f:
        plaintext = f.read()

    ciphertext = cipher.encrypt(pad(plaintext, AES.block_size))
    with open(output_file, 'wb') as f:
        f.write(iv + ciphertext)
    print(f"[+] Encrypted: {output_file}")