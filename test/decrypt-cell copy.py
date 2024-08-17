from Crypto.Cipher import Blowfish
from Crypto.Util.Padding import pad, unpad
import binascii

def form_hw_id6(hw_id):
    """
    Append the first byte of the HW_ID to the end to create HW_ID6 (6 bytes).
    """
    hw_id6 = hw_id + hw_id[:1]
    return hw_id6

def decrypt_eck(eck_hex, key):
    """
    Decrypt the ECK using the Blowfish algorithm with HW_ID6 as the key and unpad the result.
    """
    # Convert the ECK from hex to bytes
    eck_bytes = binascii.unhexlify(eck_hex)
    
    # Create a Blowfish cipher object in ECB mode with the provided key
    cipher = Blowfish.new(key, Blowfish.MODE_ECB)
    
    # Decrypt the data
    decrypted_padded_data = cipher.decrypt(eck_bytes)
    
    # Unpad the decrypted data to get the original 5-byte data
    decrypted_data = unpad(decrypted_padded_data, Blowfish.block_size)
    
    return decrypted_data

# Example input values
hw_id = b'12345'  # 5-byte HW_ID
eck1_hex = 'BBA63203A5992420'  # Example 16-character hex string representing ECK1
eck2_hex = 'BBA63203A5992420'  # Example 16-character hex string representing ECK2

#70DC6E093C49997F
# Step a: Form HW_ID6
hw_id6 = form_hw_id6(hw_id)
print(f"HW_ID6: {hw_id6}")

# Step b & c: Decrypt ECK1 to get CK1
ck1 = decrypt_eck(eck1_hex, hw_id6)
print(f"CK1 (decrypted ECK1): {ck1.hex()}")

# Step d & e: Decrypt ECK2 to get CK2
ck2 = decrypt_eck(eck2_hex, hw_id6)
print(f"CK2 (decrypted ECK2): {ck2.hex()}")
