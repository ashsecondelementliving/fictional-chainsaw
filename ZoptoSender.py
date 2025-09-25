import csv
import requests
import time
import os
import json
import hashlib

SENT_LOG = "/tmp/zopto_sent.json"  # persistent dedupe across runs/processes

def _load_sent():
    try:
        with open(SENT_LOG, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def _save_sent(d):
    tmp = SENT_LOG + ".tmp"
    with open(tmp, "w") as f:
        json.dump(d, f)
    os.replace(tmp, SENT_LOG)

def _msg_key(profile_id, message):
    pid = (profile_id or "").strip().lower()
    mh  = hashlib.sha256((message or "").strip().encode("utf-8")).hexdigest()
    return f"{pid}:{mh}"

def zoptoSenderpy(api_key, input_file):
    zopto_api_url = "https://zopto.com/api/rest/prod/user/messages"

    print(f"DEBUG: Received API Key in zoptoSenderpy: {api_key}")
    if not api_key:
        print("Error: No API key provided.")
        return 0, 0

    sent = _load_sent()
    queued = 0
    skipped = 0

    try:
        with open(input_file, mode='r', newline='', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)

            for row in reader:
                profile_id = (row.get('Profile ID') or row.get('profile_id') or '').strip()
                # support both column names
                message = (row.get('Full Message') or row.get('InMail Message') or '').strip()

                if not profile_id or not message or "SUBJECT:" in message:
                    skipped += 1
                    continue

                key = _msg_key(profile_id, message)
                if key in sent:
                    skipped += 1
                    continue

                time.sleep(45)
                send_message(api_key, zopto_api_url, profile_id, message)

                sent[key] = True
                queued += 1

        _save_sent(sent)
        print(f"All messages processed. queued={queued}, skipped={skipped}")
        return queued, skipped

    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        return 0, 0
    except Exception as e:
        print(f"Unexpected error: {e}")
        return queued, skipped

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
        try:
            response_json = response.json()
        except Exception:
            print(f"Non-JSON response for {profile_id}: {response.status_code} {response.text[:200]}")
            return

        if response_json.get("success"):
            print(f"Message successfully queued for profile {profile_id}. Message ID: {response_json.get('message_id')}")
        else:
            print(f"Failed to send message to profile {profile_id}: {response_json.get('message', 'Unknown error')}")

    except requests.exceptions.RequestException as e:
        print(f"Request error while sending message to profile {profile_id}: {e}")
    except Exception as e:
        print(f"Unexpected error sending message to profile {profile_id}: {e}")
