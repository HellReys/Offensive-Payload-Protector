import argparse
import binascii
import secrets
from .encryptor import encrypt_payload
from .obfuscator import obfuscate_key
from .stub_generator import generate_decryptor

def main():
    parser = argparse.ArgumentParser(description="Payload Encryptor CLI")
    parser.add_argument("--input", required=True, help="Input file (e.g., payload.bin)")
    parser.add_argument("--output", required=True, help="Encrypted output file")
    parser.add_argument("--key", help="AES key (32-byte hex, password, or random if omitted)")
    parser.add_argument("--xor_key", help="Custom XOR key (32-byte hex)")
    args = parser.parse_args()

    # 1. Şifreleme (Tüm mantık encryptor.py'da)
    result = encrypt_payload(args.input, args.output, args.key)
    print(f"[+] AES Key (hex): {result['aes_key_hex']}")
    print(f"[+] IV (hex): {result['iv_hex']}")

    # 2. Obfuscation
    xor_key = binascii.unhexlify(args.xor_key) if args.xor_key else secrets.token_bytes(32)
    obfuscated, xor_key_hex = obfuscate_key(binascii.unhexlify(result['aes_key_hex']), xor_key)

    # 3. Decryptor Oluşturma
    generate_decryptor(args.output, obfuscated.hex(), xor_key_hex)
    print(f"[+] XOR Key (hex): {xor_key_hex}")

if __name__ == "__main__":
    main()