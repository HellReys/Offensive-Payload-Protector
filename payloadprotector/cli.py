import argparse
import binascii
import secrets
import sys
from .encryptor import encrypt_payload
from .obfuscator import obfuscate_key
from .stub_generator import generate_decryptor
from .updater import PayloadProtectorUpdater
from .version import get_version_info, get_version


def main():
    parser = argparse.ArgumentParser(
        description="Payload Protector - Hybrid encryption tool for Red Team operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Encrypt payload with auto-generated keys
  payloadprotector --input payload.bin --output encrypted.bin

  # Encrypt with custom password
  payloadprotector --input payload.bin --output encrypted.bin --key "MyPassword"

  # Check for updates
  payloadprotector --check-update

  # Update to latest version
  payloadprotector --update
        """
    )

    # Main functionality arguments
    parser.add_argument("--input", help="Input file (e.g., payload.bin)")
    parser.add_argument("--output", help="Encrypted output file")
    parser.add_argument("--key", help="AES key (32-byte hex, password, or random if omitted)")
    parser.add_argument("--xor_key", help="Custom XOR key (32-byte hex)")

    # Update system arguments
    parser.add_argument("--update", action="store_true",
                        help="Update to the latest version")
    parser.add_argument("--check-update", action="store_true",
                        help="Check for available updates")
    parser.add_argument("--force-update", action="store_true",
                        help="Force update even if no new version available")

    # Information arguments
    parser.add_argument("--version", action="store_true",
                        help="Show version information")

    args = parser.parse_args()

    # Handle version display
    if args.version:
        print(get_version_info())
        return

    # Handle update operations
    if args.update or args.check_update or args.force_update:
        updater = PayloadProtectorUpdater()

        if args.check_update:
            updater.check_only()
        elif args.update or args.force_update:
            success = updater.update(force=args.force_update)
            if not success:
                print("[!] Update failed")
                sys.exit(1)
        return

    # Validate required arguments for encryption
    if not args.input or not args.output:
        parser.error("--input and --output are required for encryption operations")

    try:
        print(f"[*] Payload Protector v{get_version()}")
        print(f"[*] Encrypting: {args.input} -> {args.output}")

        # 1. Encryption (All logic in encryptor.py)
        result = encrypt_payload(args.input, args.output, args.key)
        print(f"[+] AES Key (hex): {result['aes_key_hex']}")
        print(f"[+] IV (hex): {result['iv_hex']}")

        # 2. Obfuscation
        xor_key = binascii.unhexlify(args.xor_key) if args.xor_key else secrets.token_bytes(32)
        obfuscated, xor_key_hex = obfuscate_key(binascii.unhexlify(result['aes_key_hex']), xor_key)

        # 3. Generate Decryptor
        generate_decryptor(args.output, obfuscated.hex(), xor_key_hex)
        print(f"[+] XOR Key (hex): {xor_key_hex}")
        print(f"[+] Decryptor generated: decryptor.py")
        print(f"[*] Run 'python decryptor.py' to execute the payload")

    except FileNotFoundError:
        print(f"[!] Input file not found: {args.input}")
        sys.exit(1)
    except Exception as e:
        print(f"[!] Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()