from Crypto.Cipher import Blowfish
from Crypto.Util.Padding import unpad
import binascii
import zipfile
import io

from decrypt_enc import ENCObject

def unzip_decrypted_data(decrypted_data, output_folder):
    """
    Unzips the decrypted data and saves the extracted files to the output folder.
    """
    with zipfile.ZipFile(io.BytesIO(decrypted_data)) as z:
        z.extractall(output_folder)
    print(f"Decrypted and unzipped files saved to {output_folder}")

def form_hw_id6(hw_id):
    """
    Append the first byte of the HW_ID to the end to create HW_ID6 (6 bytes).
    """
    hw_id6 = hw_id + hw_id[:1]
    return hw_id6

def decrypt_eck(eck_bytes, key):
    """
    Decrypt the ECK using the Blowfish algorithm with HW_ID6 as the key and unpad the result.
    """

    print(key)

    # Create a Blowfish cipher object in ECB mode with the provided key
    cipher = Blowfish.new(key, Blowfish.MODE_ECB)
    
    # Decrypt the data
    decrypted_padded_data = cipher.decrypt(eck_bytes)
    
    # Unpad the decrypted data to get the original unpadded data
    decrypted_data = unpad(decrypted_padded_data, Blowfish.block_size)
    
    return decrypted_data

def decrypt_file(input_file, hw_id):
    
    output_file = input_file + '.decoded'
    
    # Read the encrypted data from the file
    with open(input_file, 'rb') as f:
        encrypted_data = f.read()
    
    # Form HW_ID6
    #hw_id6 = form_hw_id6(hw_id)
    
    # Decrypt the file content
    decrypted_data = decrypt_eck(encrypted_data, hw_id)
    
    # Unzip the decrypted content and save the extracted files
    unzip_decrypted_data(decrypted_data, output_file)




#hw_id_hex = '494a804f6a'
#hw_id = bytes.fromhex(hw_id_hex)
    
#CK1 (decrypted ECK1): 494a804f6a
#CK2 (decrypted ECK2): 494a804f6a

#decrypt_file('data/GB100002.000', hw_id)
#decrypt_file('data/GB100002.001', hw_id)
#decrypt_file('data/GB100002.005', hw_id)

decryption_key = b'123451'  # Example key, replace with the actual key
enc_data = ENCObject(r'C:\Users\EverdreamSoft\Desktop\Projects\Toni\DecryptS63\python\PERMIT.TXT')

key = enc_data.enc_array[1].cell_keys[0].decrypt(decryption_key)
decrypt_file('data/GB100002.000', bytes.fromhex(key))
