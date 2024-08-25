import os
import zipfile
import io
import re
import binascii

from Crypto.Cipher import Blowfish
from Crypto.Util.Padding import unpad
from Crypto.Util.Padding import pad
from datetime import datetime

class Permit:
    def __init__(self, source_folder:str):
        self.date = None
        self.version = None
        self.enc_array = []
        self.ecs_array = []
        self.permit_file_path = self._get_permit_file(source_folder)
        self._parse_file(self.permit_file_path)

    def _get_permit_file(self, folder_path: str):
        # Search for the permit file in the source folder
        print("Searching for permit file in", folder_path)

        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.lower() == 'permit.txt':
                    return os.path.join(root, file)

        # If the file is not found, raise an exception
        raise ValueError("Permit file not found in the source folder: " + folder_path)

    def _parse_file(self, file_path):
        with open(file_path, 'r') as file:
            lines = file.readlines()

        current_list = None

        for line in lines:
            line = line.strip()
            if line.startswith(':DATE'):
                # Parse the date and time from the line
                date_part = line.split()[1]  # Extracts the date (e.g., 20050809)
                time_part = line.split()[2]  # Extracts the time (e.g., 11:11)

                # Convert the date and time to a datetime object
                try:
                    self.date = datetime.strptime(f"{date_part} {time_part}", "%Y%m%d %H:%M")
                except ValueError as e:
                    print(f"Error parsing date: {e}")
                    self.date = f"{date_part} {time_part}"  # Fallback to raw format if parsing fails
            elif line.startswith(':VERSION'):
                # Parse the version (e.g., 2)
                self.version = line.split()[1]
            elif line.startswith(':ENC'):
                current_list = 'ENC'
                continue  # Skip the :ENC line, move to the next lines
            elif line.startswith(':ECS'):
                current_list = 'ECS'
                continue  # Skip the :ECS line, move to the next lines
            else:
                # Parse each entry line depending on whether it's in the ENC or ECS section
                if current_list == 'ENC':
                    enc_line_part = line.split(',')[0]  # Extract the main ENC part (first field)
                    additional_fields = line.split(',')[1:]  # Extract the additional fields
                    enc_entry = self._parse_enc_line(enc_line_part, additional_fields)
                    self.enc_array.append(enc_entry)
                elif current_list == 'ECS':
                    parts = line.split(',')
                    if len(parts) == 4:
                        code = parts[0]
                        value1 = parts[1]
                        value2 = parts[2]
                        country = parts[3]
                        self.ecs_array.append(ECSEntry(code, value1, value2, country))

    def _parse_enc_line(self, enc_line, additional_fields):
        # First 8 bytes as the cell name
        cell_name = enc_line[:8]
        
        # Next 8 bytes as the expiry date
        expiry_date_str = enc_line[8:16]
        
        # Convert expiry date to a datetime object
        try:
            expiry_date = datetime.strptime(expiry_date_str, "%Y%m%d")
        except ValueError as e:
            print(f"Error parsing expiry date: {e}")
            expiry_date = expiry_date_str  # Fallback to raw format if parsing fails
        
        # Last 16 bytes as the checksum
        checksum = enc_line[-16:]
        
        # Remaining bytes in between as 16-byte cell keys
        cell_keys = []
        remaining_data = enc_line[16:-16]
        
        # Extract each 16-byte cell key
        for i in range(0, len(remaining_data), 16):
            cell_keys.append(remaining_data[i:i+16])
        
        # Parse additional fields (after the main string)
        additional_field1 = additional_fields[0]
        additional_field2 = additional_fields[1]
        country = additional_fields[2]

        return ENCCell(cell_name, expiry_date, checksum, cell_keys, additional_field1, additional_field2, country, enc_line)
    
    def decrypt_enc_files(self, source_folder:str, destination_folder:str, cell_decryption_key:str):
        
        print("Decrypting ENC files at source:", source_folder, "to destination:", destination_folder)

        # Decrypt each cell entry files in the ENC array and save them to the destination folder
        for cell_entry in self.enc_array:
            cell_entry.decrypt_cell_files(source_folder, destination_folder, cell_decryption_key)
        
        return

    def __repr__(self):
        return (f"Permit(date={self.date}, version={self.version}, "
                f"enc_array={self.enc_array}, ecs_array={self.ecs_array})")

class ENCCell:
    def __init__(self, cell_name, expiry_date, checksum, cell_keys, additional_field1, additional_field2, country, original_field):
        self.cell_name = cell_name
        self.expiry_date = expiry_date
        self.checksum = checksum
        self.cell_keys = [CellKey(key) for key in cell_keys]  # Convert each cell key to a CellKey object
        self.additional_field1 = additional_field1
        self.additional_field2 = additional_field2
        self.country = country
        self.original_field = original_field  # Store the original field that includes name, date, and keys

    def decrypt_cell_files(self, source_folder:str, destination_folder:str, cell_decryption_key:str):
        
        if(self.__validate(cell_decryption_key.encode())):
            
            # Decrypt the cell keys first
            for key in self.cell_keys:
                key.decrypt(cell_decryption_key)

            cell_file_key_map = self.__get_cell_files_key_map(source_folder)
            
            for file, key in cell_file_key_map.items():
                self.__save_file(self.__decrypt_cell_file(file, key.decrypted_key), destination_folder)

        else:
            raise ValueError("Validation failed for cell: " + self.cell_name)

    def __validate(self, encryption_key):
        """
        Validate that the generated CRC32 hash, when encrypted, matches the checksum stored in the entry.
        """
        # Concatenate the original field (name, date, keys)
        data_to_validate = self.original_field[:-16]

        # Generate a CRC32 checksum from the ASCII bytes (left-hand byte first)
        generated_checksum = binascii.crc32(data_to_validate.encode()) & 0xFFFFFFFF

        # Encrypt the generated checksum using Blowfish
        try:
            # Convert the generated checksum to bytes
            checksum_bytes = generated_checksum.to_bytes(4, 'big')  # Convert to 4 bytes

            # Initialize the Blowfish cipher in ECB mode
            cipher = Blowfish.new(encryption_key, Blowfish.MODE_ECB)

            # Pad the checksum bytes to the Blowfish block size (8 bytes)
            padded_checksum = pad(checksum_bytes, Blowfish.block_size)

            # Encrypt the padded checksum
            encrypted_checksum = cipher.encrypt(padded_checksum)

            # Convert the encrypted checksum to hex
            encrypted_checksum_hex = binascii.hexlify(encrypted_checksum).decode().upper()


        except Exception as e:
            print(f"Encryption error for checksum: {e}")
            return False  # In case of encryption failure

        # Compare the encrypted checksum with the checksum provided in the entry
        is_valid = encrypted_checksum_hex == self.checksum
        
        return is_valid
    
    def __get_cell_files_key_map(self, folder_path):
        # Regular expression to match files like CELLNAME.000, CELLNAME.001, etc.
        pattern = re.compile(rf'^{self.cell_name}\.\d{{3}}$')
        matching_files = []

        # Walk through the directory and check for files that match the pattern
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if pattern.match(file):
                    matching_files.append(os.path.join(root, file))

        return self.__map_files_to_keys(matching_files, self.cell_keys)

    def __map_files_to_keys(self, files, cell_keys):
        # Dictionary to hold the final mapping of file -> key
        file_key_map = {}

        for file in files:
            # Extract the file extension (e.g., ".000", ".001")
            extension = file.split('.')[-1]

            # Convert the extension to an integer index if possible
            try:
                index = int(extension)
                if index < len(cell_keys):
                    file_key_map[file] = cell_keys[index]
                else:
                    # If the index is out of bounds, default to the first key
                    file_key_map[file] = cell_keys[0]
            except ValueError:
                # If the extension isn't a valid integer, default to the first key
                file_key_map[file] = cell_keys[0]

        return file_key_map

    def __decrypt_cell_file(self, input_file, cell_key):
        # Read the encrypted data from the file
        with open(input_file, 'rb') as f:
            encrypted_data = f.read()
                
        # Decrypt the file content
        # Create a Blowfish cipher object in ECB mode with the provided key
        cipher = Blowfish.new(bytes.fromhex(cell_key), Blowfish.MODE_ECB)
        
        # Decrypt the data
        decrypted_padded_data = cipher.decrypt(encrypted_data)
        
        # Unpad the decrypted data to get the original unpadded data
        decrypted_data = unpad(decrypted_padded_data, Blowfish.block_size)
        
        return decrypted_data
    
    def __save_file(self, zipped_data, output_folder):
        """
        Unzips the decrypted data and saves only the files directly into the output folder,
        ignoring any folder structure in the archive.
        """
        with zipfile.ZipFile(io.BytesIO(zipped_data)) as z:
            for file_info in z.infolist():
                if not file_info.is_dir():
                    # Extract the file and save it directly in the output folder
                    extracted_file = z.open(file_info)
                    output_file_path = os.path.join(output_folder, os.path.basename(file_info.filename))
                    # Save the file content
                    with open(output_file_path, 'wb') as output_file:
                        output_file.write(extracted_file.read())
            
    def __repr__(self):
        return (f"ENCCell(cell_name={self.cell_name}, expiry_date={self.expiry_date}, "
                f"checksum={self.checksum}, cell_keys={self.cell_keys}, "
                f"additional_field1={self.additional_field1}, additional_field2={self.additional_field2}, country={self.country})")

class CellKey:
    def __init__(self, key_data):
        self.key_data = key_data
        self.decrypted_key = None
    
    def decrypt(self, decryption_key:str):
        """
        Decrypt this cell key using Blowfish with the provided decryption key.
        """
        try:
           
            # Convert the key data from hex to bytes
            key_bytes = binascii.unhexlify(self.key_data)

            # Initialize the Blowfish cipher in ECB mode
            cipher = Blowfish.new(decryption_key.encode(), Blowfish.MODE_ECB)

            # Decrypt the key and unpad it
            decrypted_data = unpad(cipher.decrypt(key_bytes), Blowfish.block_size)
            
            # Store the decrypted key for later validation
            self.decrypted_key = binascii.hexlify(decrypted_data).decode()
        
            return self.decrypted_key
        
        except Exception as e:
            print(f"Decryption error for key {self.key_data}: {e}")
            return None  # In case of decryption failure

    def __repr__(self):
        return f"CellKey(key_data={self.key_data}, decrypted_key={self.decrypted_key})"

