import argparse
from scripts.s_63 import S63

def main():
    parser = argparse.ArgumentParser(description="S63 User Permit Tool")
    parser.add_argument(
        "--action", choices=["get_hw_id", "decrypt"], required=True, help="Action to perform: get_hw_id or decrypt"
    )
    parser.add_argument("--permit_code", required=True, help="User permit code")
    parser.add_argument("--m_key", required=True, help="Manufacturer key")

    args = parser.parse_args()

    # Initialize the S63 object
    s63_instance = S63(args.permit_code, args.m_key)

    if args.action == "get_hw_id":
        # Get and print the hardware ID
        hw_id = s63_instance.get_hw_id()
        print(f"Hardware ID: {hw_id}")

    elif args.action == "decrypt":
        # This is an example, you can add more specific decrypt-related functionality here
        s63_instance.decrypt(r"C:\Users\EverdreamSoft\Downloads\S-64_e3.0.2_ENC_Encrypted_TDS\S-64_e3.0.2_ENC_Encrypted_TDS\7 ENC Data Management\Test 7a\DS2", 
                             r"C:\Users\EverdreamSoft\Downloads\S-64_e3.0.2_ENC_Encrypted_TDS\S-64_e3.0.2_ENC_Encrypted_TDS\7 ENC Data Management\Test 7a\DS2.decrypted")

if __name__ == "__main__":
    main()
