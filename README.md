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
python user_permit.py --action create --hw_id <hardware_id> --key <encryption_key> --m_id <machine_id>
```

Parameters:
- --hw_id: The hardware ID (string) to be encrypted.
- --key: The encryption key used for Blowfish encryption.
- --m_id: The machine ID (typically the last 4 characters) to be included in the permit code.

#### Decrypting a User Permit

```bash
python user_permit.py --action decrypt --key <encryption_key> --permit_code <user_permit_code>
```

Parameters:

- --key: The encryption key used for decryption.
- --permit_code: The user permit code to be decrypted.


### Example 

```bash
> python user_permit.py --action create --hw_id "12345" --key "10121" --m_id "3130"
  Output -
  Generated User Permit: 66B5CBFDF7E4139D5B6086C23130

> python user_permit.py --action decrypt --key "10121" --permit_code "66B5CBFDF7E4139D5B6086C23130"
 Output -
 Decrypted Hardware ID: 12345
 Permit Code: 66B5CBFDF7E4139D5B6086C23130, m_id: 3130, checksum: 5B6086C2, Encrypted HW ID: 66B5CBFDF7E4139D, Decrypted HW ID: 12345


