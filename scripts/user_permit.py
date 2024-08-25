import binascii
from Crypto.Cipher import Blowfish
from Crypto.Util.Padding import pad, unpad
import zlib

class UserPermit:
    def __init__(self):
        self.m_id = None
        self.hw_id = None
        self.checksum = None
        self.encrypted_hw_id = None
        self.permit_code = None

    def generate_encrypted_checksum(self, original_data: str) -> str:
       
        generated_checksum = zlib.crc32(original_data.encode()) & 0xFFFFFFFF

        checksum_hex = f"{generated_checksum:08X}"

        return checksum_hex

    def encrypt(self, hw_id: str, key: str, m_id: str) -> str:
        # Ensure key is in bytes
        key_bytes = key.encode()

        # Initialize the Blowfish cipher in ECB mode
        cipher = Blowfish.new(key_bytes, Blowfish.MODE_ECB)

        # Pad the hardware ID to match Blowfish block size
        padded_data = pad(hw_id.encode(), Blowfish.block_size)

        # Encrypt the padded data
        encrypted_data = cipher.encrypt(padded_data)

        # Convert encrypted data to hex
        self.encrypted_hw_id = binascii.hexlify(encrypted_data).decode().upper()
        
        # Generate the encrypted checksum
        self.checksum = self.generate_encrypted_checksum(self.encrypted_hw_id)

        # Combine the encrypted_hw_id, checksum, and m_id to create the permit code
        self.m_id = m_id.encode("utf-8").hex()

        self.permit_code = f"{self.encrypted_hw_id}{self.checksum}{self.m_id}"

        return self.permit_code

    def decrypt(self, key: str, permit_code: str) -> str:
        if len(permit_code) != 28:
            raise ValueError("Permit code length is not valid")

        # Extract components from the permit code
        self.permit_code = permit_code
        self.m_id = permit_code[-4:]  # Last 4 characters are the m_id
        self.checksum = permit_code[-12:-4]  # Next 8 characters are the checksum
        self.encrypted_hw_id = permit_code[:-12]  # The rest is the encrypted user ID

        self.m_id = bytes.fromhex(self.m_id).decode("utf-8")
        
        # Ensure key is in bytes
        key_bytes = key.encode()

        # Initialize the Blowfish cipher in ECB mode
        cipher = Blowfish.new(key_bytes, Blowfish.MODE_ECB)

        # Decrypt the data
        decrypted_data = cipher.decrypt(binascii.unhexlify(self.encrypted_hw_id))

        # Remove padding
        decrypted_data = unpad(decrypted_data, Blowfish.block_size)

        # Convert the decrypted data back to a string
        self.hw_id = decrypted_data.decode()

        return self.hw_id

    def __str__(self):
        return f"Permit Code: {self.permit_code}, Manufacturer ID: {self.m_id}, Decrypted Hardware ID: {self.hw_id}"
