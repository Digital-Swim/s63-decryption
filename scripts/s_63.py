import os
import shutil

from pathlib import Path
from user_permit import UserPermit
from .permit import Permit

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

        self.permit = Permit(source_folder)

        # Append the destination folder with ENC_ROOT
        target_folder = os.path.join(destination_folder, "ENC_ROOT")

        if not os.path.exists(target_folder):
            os.makedirs(target_folder)

        # Copy Permit file to the destination folder
        shutil.copy(self.permit.permit_file_path, os.path.join(destination_folder, "permit.txt"))
    
        # Decrypt the ENC files to the destination folder
        self.permit.decrypt_enc_files(source_folder, target_folder, (self.user_permit.hw_id + self.user_permit.hw_id[0]))

        # Copy the rest of the files
        self.__copy_files(source_folder, target_folder)

        return
        
    def __copy_files(self, source_folder:str, destination_folder:str):

        # Convert source and destination folders to Path objects for easier manipulation
        source = Path(source_folder)
        destination = Path(destination_folder)

        # Create the destination folder if it doesn't exist
        destination.mkdir(parents=True, exist_ok=True)

        # Get a set of filenames already in the destination folder (no paths, just names)
        existing_files = {file.name for file in destination.iterdir() if file.is_file()}

        # Recursively copy files from the source folder to the destination folder
        for file in source.rglob('*'):
            if file.is_file() and file.name.lower() != 'permit.txt':  # Exclude permit.txt
                if file.name not in existing_files:
                    destination_file = destination / file.name
                    shutil.copy(file, destination_file)
