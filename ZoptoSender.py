import csv
import requests
import time

def zoptoSenderpy(api_key, input_file):
    zopto_api_url = "https://zopto.com/api/rest/prod/user/messages"

    print(f"DEBUG: Received API Key in zoptoSenderpy: {api_key}")
    
    if not api_key:
        print("Error: No API key provided.")
        return

    processed_profiles = set() 

    try:
        with open(input_file, mode='r', newline='', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)

            for row in reader:
                profile_id = row.get('Profile ID', '').strip()
                message = row.get('Full Message', '').strip()

                if profile_id and message and profile_id not in processed_profiles and "SUBJECT:" not in message:
                    time.sleep(45)
                    send_message(api_key, zopto_api_url, profile_id, message)
                    processed_profiles.add(profile_id)  
                else:
                    print(f"Skipping invalid, duplicate, or improperly formatted row: {row}")

        print("All messages processed.")
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
    except Exception as e:
        print(f"Unexpected error: {e}")

def send_message(api_key, zopto_api_url, profile_id, message, method="SN"):
    headers = {
        "token": api_key,
        "Content-Type": "application/json"
    }
    
    payload = {
        "body": message,
        "method": method,
        "profile_id": profile_id
    }
    
    try:
        response = requests.put(zopto_api_url, json=payload, headers=headers)
        response_json = response.json()

        if response_json.get("success"):
            print(f"Message successfully queued for profile {profile_id}. Message ID: {response_json.get('message_id')}")
        else:
            print(f"Failed to send message to profile {profile_id}: {response_json.get('message', 'Unknown error')}")
    
    except requests.exceptions.JSONDecodeError:
        print(f"Failed to parse JSON response for profile {profile_id}. Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Request error while sending message to profile {profile_id}: {e}")
    except Exception as e:
        print(f"Unexpected error sending message to profile {profile_id}: {e}")
