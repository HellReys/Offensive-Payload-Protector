from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import argparse
import os


def encrypt_payload(input_file, output_file, key):
    #Creating random IV for AES
    iv = get_random_bytes(16)
    cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv)

    with open(input_file, 'rb') as f:
        plaintext = f.read()

    #encrypt the payload and add IV to the file
    ciphertext = cipher.encrypt(pad(plaintext, AES.block_size))
    with open(output_file, 'wb') as f:
        f.write(iv + ciphertext)
    print(f"[+] Payload encrypted and saved to {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Malware Payload Encryptor")
    parser.add_argument("--input", required=True, help="Input payload file (e.g., evil.exe)")
    parser.add_argument("--output", required=True, help="Output encrypted file (e.g., encrypted.bin)")
    parser.add_argument("--key", required=True, help="Encryption key (e.g., MySuperSecretKey)")
    args = parser.parse_args()

    encrypt_payload(args.input, args.output, args.key)


if __name__ == "__main__":
    main()