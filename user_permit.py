from datetime import datetime
from Crypto.Cipher import Blowfish
from Crypto.Util.Padding import unpad
import binascii
import hashlib
from Crypto.Util.Padding import pad

class UserPermit:
    def __init__(self, permit_code: str):
        if len(permit_code) != 28: 
            raise ValueError("Permit code length is not valid")
        
        self.permit_code = permit_code
        self.m_id = permit_code[-4:]  # Last 4 characters are the m_id
        self.checksum = permit_code[-12:-4]  # Next 8 characters are the checksum
        self.encrypted_hw_id = permit_code[:-12]  # The rest is the encrypted user ID


    def decrypt_h_id(self, key: bytes) -> str:
        
        key_bytes = key.encode()

        cipher = Blowfish.new(key_bytes, Blowfish.MODE_ECB)

        decrypted_data = cipher.decrypt(binascii.unhexlify(self.encrypted_hw_id))

        decrypted_data = unpad(decrypted_data, Blowfish.block_size)

        self.decrypted_key = binascii.hexlify(decrypted_data).decode()
        
        return self.decrypted_key
        

    def encrypt_h_id(self, key: bytes) -> str:
        key_bytes = key.encode()

        # Initialize the Blowfish cipher in ECB mode
        cipher = Blowfish.new(key_bytes, Blowfish.MODE_ECB)

        # Convert the plaintext ID to bytes and pad it to the Blowfish block size
        padded_data = pad(self.plaintext_hw_id.encode(), Blowfish.block_size)

        # Encrypt the padded data
        encrypted_data = cipher.encrypt(padded_data)

        # Convert the encrypted data to a hex string
        self.encrypted_hw_id = binascii.hexlify(encrypted_data).decode()

        return self.encrypted_hw_id
    

    def __str__(self):
        return f"m_id: {self.m_id}, checksum: {self.checksum}, encrypted_hw_id: {self.encrypted_hw_id}"

# Example usage:
permit_code = "66B5CBFDF7E4139D5B6086C23130"
key = "10121"

user_permit = UserPermit(permit_code)
print(user_permit)  # Print the extracted components

decrypted_user_id = user_permit.decrypt_h_id(key)
print(f"Decrypted HW ID: {decrypted_user_id}")

decrypted_user_id = user_permit.encrypt_h_id(key)
print(f"Encrypted HW ID: {decrypted_user_id}")
