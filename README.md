# User Permit Tool

This project provides a utility for creating and decrypting user permits using Blowfish encryption. The core functionality is implemented in the `user_permit.py` file located in the `tools` directory. The `user_permit_tool.py` script provides a command-line interface (CLI) for interacting with the user permit system.

## Project Structure

- Root Folder 
    - Scripts


## Prerequisites

Before running the scripts, make sure you have the necessary Python packages installed:

```bash
pip install pycryptodome
```


### Usage

#### Creating a User Permit

```bash
python user_permit.py --action create --hw_id <hardware_id> --m_key <manufacturer_key> --m_id <manufacturer_id>
```

Parameters:
- --hw_id: The hardware ID (string) to be encrypted.
- --m_key: The manufacturer key used for Blowfish encryption.
- --m_id: The manufacturer ID (typically the last 4 characters) to be included in the permit code.

#### Decrypting a User Permit

```bash
python user_permit.py --action decrypt --m_key <manufacturer_key> --permit_code <user_permit_code>
```

Parameters:

- --m_key: The manufacturer key used for decryption.
- --permit_code: The user permit code to be decrypted.


### Example 

```bash
> python user_permit.py --action create --hw_id "12345" --m_key "10121" --m_id "10"
  Output -
  Generated User Permit: 66B5CBFDF7E4139D5B6086C23130

> python user_permit.py --action decrypt --m_key "10121" --permit_code "66B5CBFDF7E4139D5B6086C23130"
 Output -
 Manufacturer ID: 10
 Hardware ID: 12345
 Permit Code: 66B5CBFDF7E4139D5B6086C23130, Manufacturer ID: 10, Decrypted Hardware ID: 12345



> python.exe .\s_63.py --action get_hw_id  --m_key "10121" --permit_code "66B5CBFDF7E4139D5B6086C23130"   

 Output -
 Hardware ID: 12345  

> python.exe .\s_63.py --action decrypt  --m_key "10121" --permit_code "66B5CBFDF7E4139D5B6086C23130" --source_folder "Path_to_encrypted_data" --dst_folder  "path for decrypted output"

Output -
 Files decrypted at dst_folder


