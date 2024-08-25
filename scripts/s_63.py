import os
import re
import os
from Crypto.Cipher import Blowfish
from Crypto.Util.Padding import unpad
import binascii
import zipfile
import io
import re
from user_permit import UserPermit
from .permit import Permit
from .permit import CellKey

class S63:

    def __init__(self, user_permit_code:str, manufacturer_key:str):
        self.__manufacturer_key = manufacturer_key
        self.__user_permit_code = user_permit_code
        self.user_permit = UserPermit()
        self.user_permit.decrypt(self.__manufacturer_key, self.__user_permit_code)
        self.permit = None

    def get_hw_id(self):
        return self.user_permit.hw_id
    
    def decrypt(self, source_folder:str, destination_folder:str):
        self.__process(source_folder, destination_folder)
        pass

    def __process(self, source_folder:str, destination_folder:str):
        
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)

        self.permit = Permit(source_folder)

        print("Permit file found")
    
        self.__decrypt_enc_files(source_folder, destination_folder)

        return

    def __decrypt_enc_files(self, source_folder:str, destination_folder:str):

        print("Decrypting ENC files...")
        for cell_entry in self.permit.enc_array:
            matching_files = self.__find_cell_files(source_folder, cell_entry.cell_name)
            for file in matching_files:
                print(f"Decrypting {file}...")
                cell_key:CellKey =cell_entry.cell_keys[0]
                cell_key.decrypt(self.user_permit.hw_id + self.user_permit.hw_id[0])
                key = bytes.fromhex(cell_key.decrypted_key)
                self.__decrypt_file1(file, key, destination_folder)

        
        return 

    def __find_cell_files(self, folder_path, cell_name):
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

    def __decrypt_file1(self, input_file, hw_id, output_folder):
        # Read the encrypted data from the file
        with open(input_file, 'rb') as f:
            encrypted_data = f.read()
                
        # Decrypt the file content
        decrypted_data = self.__decrypt_file_data(encrypted_data, hw_id)
        
        # Unzip the decrypted content and save the extracted files
        self.__unzip_decrypted_data(decrypted_data, output_folder)

    def __decrypt_file_data(self, data_bytes, key):

        # Create a Blowfish cipher object in ECB mode with the provided key
        cipher = Blowfish.new(key, Blowfish.MODE_ECB)
        
        # Decrypt the data
        decrypted_padded_data = cipher.decrypt(data_bytes)
        
        # Unpad the decrypted data to get the original unpadded data
        decrypted_data = unpad(decrypted_padded_data, Blowfish.block_size)
        
        return decrypted_data
    
    def __unzip_decrypted_data(self, decrypted_data, output_folder):
        """
        Unzips the decrypted data and saves only the files directly into the output folder,
        ignoring any folder structure in the archive.
        """
        with zipfile.ZipFile(io.BytesIO(decrypted_data)) as z:
            for file_info in z.infolist():
                if not file_info.is_dir():
                    # Extract the file and save it directly in the output folder
                    extracted_file = z.open(file_info)
                    output_file_path = os.path.join(output_folder, os.path.basename(file_info.filename))
                    # Save the file content
                    with open(output_file_path, 'wb') as output_file:
                        output_file.write(extracted_file.read())
        
        print(f"Decrypted and saved all files directly to {output_folder}")


    def __copy(self):
        pass


    def __decrypt_file(self):
        pass

