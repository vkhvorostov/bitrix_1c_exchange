import requests
import sys
import os
import random
import string
import zipfile

DEBUG = False # set to True to see all server responses

def generate_random_string(length):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string

def zip_file(filename, zip_filename):
    base_path = os.path.dirname(filename)
    base_name = os.path.basename(filename)
    zip_filepath = f'{base_path}/{zip_filename}'
    try:
        with zipfile.ZipFile(zip_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(filename, arcname=base_name)
        return zip_filepath
    except FileNotFoundError as e:
        print(f"Error reading file '{filename}': {e}")
        return False

def authenticate(server_address, username, password):
    checkauth_endpoint = f"{server_address}/bitrix/admin/1c_exchange.php?type=sale&mode=checkauth"
    response = requests.get(checkauth_endpoint, auth=(username, password))

    if response.status_code == 200:
        if DEBUG: print(response.text)
        response_lines = response.text.splitlines()

        if response_lines[0] != 'success':
            print("Authentication Error")
            return None

        session_id = response_lines[3]
        return session_id, response.cookies

    print(f"Authentication Error: {response.status_code} - {response.text}")
    return None

def initialize_exchange(server_address, username, password, cookies, session_id, version):
    init_endpoint = f"{server_address}/bitrix/admin/1c_exchange.php?type=sale&mode=init&{session_id}&version={version}"
    response = requests.get(init_endpoint, auth=(username, password), cookies=cookies)

    if response.status_code == 200 and 'failure' not in response.text:
        if DEBUG: print(response.text)
        return True
    else:
        print(f"Initialization Error: {response.status_code} - {response.text}")
        return False

def send_file(server_address, username, password, cookies, session_id, version, xml_file):
    zip_filename = 'test_' + generate_random_string(8) + '.zip'
    zip_filepath = zip_file(xml_file, zip_filename)
    if not zip_filepath:
        return False
    file_endpoint = f"{server_address}/bitrix/admin/1c_exchange.php?type=sale&mode=file&filename={zip_filename}&{session_id}&version={version}"
    try:
        with open(zip_filepath, 'rb') as file:
            response = requests.post(file_endpoint, auth=(username, password), cookies=cookies, data=file.read(), headers={'Content-Type': 'application/octet-stream'})

            if response.status_code == 200 and 'failure' not in response.text:
                if DEBUG: print(response.text)
                os.remove(zip_filepath)
                return True
            else:
                print(f"Error sending file: {response.status_code} - {response.text}")
                return False
    except IOError as e:
        print(f"Error reading file '{zip_filepath}': {e}")
        return False
    

def import_file(server_address, username, password, cookies, session_id, version, xml_file):
    base_name = os.path.basename(xml_file)
    import_endpoint = f"{server_address}/bitrix/admin/1c_exchange.php?type=sale&mode=import&filename={base_name}&{session_id}&version={version}"
    response = requests.get(import_endpoint, auth=(username, password), cookies=cookies)

    if response.status_code == 200:
        if 'success' in response.text:
            print(response.text) 
            return True
        elif 'progress' in response.text:
            if DEBUG: print(response.text) 
            return 'progress'
        else:
            if DEBUG: print(response.text)
            return False        
    else:
        print(f"Import Error: {response.status_code} - {response.text}")
        return False

# Get command line arguments
if len(sys.argv) < 6:
    print("Usage: python3 sendorders.py <server_address> <username> <password> <version> <xml_file>")
    print("<version> is recommended to be 3.1")
    sys.exit(1)

server_address = sys.argv[1]
username = sys.argv[2]
password = sys.argv[3]
version = sys.argv[4]
xml_file = sys.argv[5]

# Step 1: Authenticate and get session ID
session_id, cookies = authenticate(server_address, username, password)

if session_id:
    # Step 2: Initialize exchange
    if initialize_exchange(server_address, username, password, cookies, session_id, version):
        # Step 3: Send a file
        if send_file(server_address, username, password, cookies, session_id, version, xml_file):
            # Step 4: Importing a file
            while 'progress' == import_file(server_address, username, password, cookies, session_id, version, xml_file):
                pass