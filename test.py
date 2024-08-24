import os
from decrypt_enc import ENCObject
from Crypto.Cipher import Blowfish
from Crypto.Util.Padding import unpad
import binascii
import zipfile
import io
import re

def store_permit_file_paths(folder_path):
    permit_file_paths = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower() == 'permit.txt':
                permit_file_paths.append(root)  # Store only the root path
    return permit_file_paths


def unzip_decrypted_data(decrypted_data, output_folder):
    """
    Unzips the decrypted data and saves only the files directly into the output folder,
    ignoring any folder structure in the archive.
    """
    with zipfile.ZipFile(io.BytesIO(decrypted_data)) as z:
        for file_info in z.infolist():
            if not file_info.is_dir():
                # Extract the file and save it directly in the output folder
                extracted_file = z.open(file_info)
                print(file_info)
                print(output_folder)
                output_file_path = os.path.join(output_folder, os.path.basename(file_info.filename))
                print(output_file_path)

                # Save the file content
                with open(output_file_path, 'wb') as output_file:
                    output_file.write(extracted_file.read())
    
    print(f"Decrypted and saved all files directly to {output_folder}")

def unzip_decrypted_data1(decrypted_data, output_folder):
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

def decrypt_file(input_file, hw_id, output_folder):
    
    #output_file = os.path.join(output_folder, os.path.basename(input_file))
    
    # Read the encrypted data from the file
    with open(input_file, 'rb') as f:
        encrypted_data = f.read()
    
    # Form HW_ID6
    #hw_id6 = form_hw_id6(hw_id)
    
    # Decrypt the file content
    decrypted_data = decrypt_eck(encrypted_data, hw_id)
    
    # Unzip the decrypted content and save the extracted files
    unzip_decrypted_data(decrypted_data, output_folder)


def find_cell_files(folder_path, cell_name):
    # Regular expression to match files like CELLNAME.000, CELLNAME.001, etc.
    pattern = re.compile(rf'^{cell_name}\.\d{{3}}$')
    matching_files = []

    # Walk through the directory and check for files that match the pattern
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if pattern.match(file):
                print(os.path.join(root, file))
                matching_files.append(os.path.join(root, file))

    return matching_files

# Example usage:
folder_path = r'C:\Users\EverdreamSoft\Downloads\S-64_e3.0.2_ENC_Encrypted_TDS\S-64_e3.0.2_ENC_Encrypted_TDS\7 ENC Data Management\Test 7a'  # Replace with the path to your folder
permit_file_roots = store_permit_file_paths(folder_path)


decryption_key = b'123451'  # Example key, replace with the actual key
#enc_data = ENCObject(r'C:\Users\EverdreamSoft\Desktop\Projects\Toni\DecryptS63\python\PERMIT.TXT')


print("Root paths containing 'permit.txt':")
for path in permit_file_roots:
    print(path)
    # Create a folder to store the decoded files
    decoded_folder_path = os.path.join(path, "decoded")    
    # Create the folder if it doesn't already exist
    if not os.path.exists(decoded_folder_path):
        os.makedirs(decoded_folder_path)
    print("Decoded files will be saved to:", decoded_folder_path)

    permit_obj = ENCObject( path + '\\PERMIT.TXT')
    for entry in permit_obj.enc_array:
        print (entry.cell_name)
        print(entry.cell_keys)

        #find all cell files with cell name in path 
        matching_files = find_cell_files(path, entry.cell_name)
        for file in matching_files:
            print(file)
            decrypt_file(file, bytes.fromhex(entry.cell_keys[0].decrypt(decryption_key)), decoded_folder_path)

        #key = enc_data.enc_array[1].cell_keys[0].decrypt(decryption_key)
        #decrypt_file('data/GB100002.000', bytes.fromhex(key))


    