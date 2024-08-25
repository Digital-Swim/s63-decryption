import argparse
from scripts.s_63 import S63

def main():
    parser = argparse.ArgumentParser(description="S63 User Permit Tool")
    parser.add_argument(
        "--action", choices=["get_hw_id", "decrypt"], required=True, help="Action to perform: get_hw_id or decrypt"
    )
    parser.add_argument("--permit_code", required=True, help="User permit code")
    parser.add_argument("--m_key", required=True, help="Manufacturer key")
    parser.add_argument("--source_folder", required=False, help="Source folder for decryption")
    parser.add_argument("--dst_folder", required=False, help="Destination folder for decrypted output")

    args = parser.parse_args()

    # Initialize the S63 object
    s63_instance = S63(args.permit_code, args.m_key)

    if args.action == "get_hw_id":
        # Get and print the hardware ID
        hw_id = s63_instance.get_hw_id()
        print(f"Hardware ID: {hw_id}")

    elif args.action == "decrypt":
        if not args.source_folder or not args.dst_folder:
            print("Error: Both --source_folder and --dst_folder are required for the decrypt action.")
            return
        
        # Call the decrypt method with the provided source and destination folders
        s63_instance.decrypt(args.source_folder, args.dst_folder)
        print(f"Decryption completed from {args.source_folder} to {args.dst_folder}")

if __name__ == "__main__":
    main()
