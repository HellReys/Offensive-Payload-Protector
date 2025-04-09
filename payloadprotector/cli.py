import argparse
from .encryptor import encrypt_payload
from .obfuscator import obfuscate_key
from .stub_generator import generate_decryptor


def main():
    parser = argparse.ArgumentParser(description="Offensive Payload Encryptor")
    parser.add_argument("--input", required=True, help="Input payload file")
    parser.add_argument("--output", required=True, help="Encrypted output file")
    parser.add_argument("--key", required=True, help="Encryption key")
    parser.add_argument("--xor_key", help="Custom XOR key (hex format)")

    args = parser.parse_args()

    # 1. Encrypt payload
    encrypt_payload(args.input, args.output, args.key)

    # 2. Obfuscate key
    xor_key = bytes.fromhex(args.xor_key) if args.xor_key else None
    obfuscated, xor_key_hex = obfuscate_key(args.key, xor_key)

    # 3. Generate decryptor
    generate_decryptor(args.output, obfuscated, xor_key_hex)
    print(f"[+] XOR Key: {xor_key_hex}")


if __name__ == "__main__":
    main()