from Crypto.Cipher import Blowfish
from Crypto.Util.Padding import unpad
import binascii


# Define the key and the encrypted hex string
#key = b'10121'
#encrypted_hex = '66B5CBFDF7E4139D'

key = b'123451'
encrypted_hex = 'BBA63203A5992420'


# Convert the hex string back to bytes
encrypted_bytes = binascii.unhexlify(encrypted_hex)

# Create a Blowfish cipher object in ECB mode
cipher = Blowfish.new(key, Blowfish.MODE_ECB)

# Decrypt the data
decrypted_padded_data = cipher.decrypt(encrypted_bytes)

# Unpad the decrypted data to get the original plaintext
decrypted_data = unpad(decrypted_padded_data, Blowfish.block_size)

print("Decrypted H_ID:", decrypted_data.decode('utf-8'))
