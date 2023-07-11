import requests
import sys

DEBUG = False # set to True to see all server responses

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

def get_new_orders(server_address, username, password, cookies, session_id, version):
    query_endpoint = f"{server_address}/bitrix/admin/1c_exchange.php?type=sale&mode=query&{session_id}&version={version}"
    response = requests.get(query_endpoint, auth=(username, password), cookies=cookies)

    if response.status_code == 200:
        orders = response.text
        # Process the orders as needed
        print(orders)
    else:
        print(f"Error: {response.status_code} - {response.text}")

def complete_exchange(server_address, username, password, cookies, session_id, version):
    success_endpoint = f"{server_address}/bitrix/admin/1c_exchange.php?type=sale&mode=success&{session_id}&version={version}"
    response = requests.get(success_endpoint, auth=(username, password), cookies=cookies)

    if response.status_code == 200 and 'success' in response.text:
        if DEBUG: 
            print(response.text)
            print("Exchange completed successfully.")
    else:
        print(f"Completion Error: {response.status_code} - {response.text}")

# Get command line arguments
if len(sys.argv) < 5:
    print("Usage: python3 getorders.py <server_address> <username> <password> <version>")
    print("<version> is recommended to be 3.1")
    sys.exit(1)

server_address = sys.argv[1]
username = sys.argv[2]
password = sys.argv[3]
version = sys.argv[4]

# Step 1: Authenticate and get session ID
session_id, cookies = authenticate(server_address, username, password)

if session_id:
    # Step 2: Initialize exchange
    if initialize_exchange(server_address, username, password, cookies, session_id, version):
        # Step 3: Get new orders
        get_new_orders(server_address, username, password, cookies, session_id, version)
        # Step 4: Complete exchange
        complete_exchange(server_address, username, password, cookies, session_id, version)
