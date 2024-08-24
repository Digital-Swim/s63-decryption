import argparse
from scripts.user_permit import UserPermit  # Import the UserPermit class from user_permit.py

def main():
    parser = argparse.ArgumentParser(description="User Permit Creation and Decryption Tool")
    parser.add_argument(
        "--action", choices=["create", "decrypt"], required=True, help="Action to perform: create or decrypt"
    )
    parser.add_argument("--hw_id", help="Hardware ID (used in create action)")
    parser.add_argument("--m_key", required=True, help="Manufacturer key")
    parser.add_argument("--m_id", help="<anufacturer ID (used in create action)")
    parser.add_argument("--permit_code", help="User Permit Code (used in decrypt action)")

    args = parser.parse_args()

    user_permit = UserPermit()

    if args.action == "create":
        if not args.hw_id or not args.m_id:
            print("Error: --hw_id and --m_id are required for the create action")
            return
        permit_code = user_permit.encrypt(args.hw_id, args.m_key, args.m_id)
        print(f"Generated User Permit: {permit_code}")

    elif args.action == "decrypt":
        if not args.permit_code:
            print("Error: --permit_code is required for the decrypt action")
            return
        decrypted_hw_id = user_permit.decrypt(args.m_key, args.permit_code)
        print(f"Hardware ID: {decrypted_hw_id}")
        print(user_permit)

if __name__ == "__main__":
    main()
