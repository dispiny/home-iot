import os
from flask import Flask, request, jsonify
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64
import requests
import time
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# AES256 Encryption/Decryption
class AES256:
    def __init__(self):
        self.appKey = os.getenv("APP_KEY")  # Loaded from environment variable

    def encrypt(self, text):
        key = self.appKey[:32].encode('utf-8')
        iv = self.appKey[:16].encode('utf-8')
        cipher = AES.new(key, AES.MODE_CBC, iv)
        encrypted = cipher.encrypt(pad(text.encode('utf-8'), AES.block_size))
        return base64.urlsafe_b64encode(encrypted).decode('utf-8')

    def decrypt(self, cipherText):
        key = self.appKey[:32].encode('utf-8')
        iv = self.appKey[:16].encode('utf-8')
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decodedBytes = base64.urlsafe_b64decode(cipherText)
        decrypted = unpad(cipher.decrypt(decodedBytes), AES.block_size)
        return decrypted.decode('utf-8')

# Token Management
class TokenManager:
    def __init__(self):
        self.aes256 = AES256()
        self.client_id = os.getenv("CLIENT_ID")
        self.client_secret = os.getenv("CLIENT_SECRET")
        self.username = os.getenv("USERNAME")
        self.password = os.getenv("PASSWORD")
        self.access_token = None
        self.refresh_token = None
        self.token_expiry = 0

    def get_encrypted_payload(self, grant_type, refresh_token=None):
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": grant_type,
        }
        if grant_type == "password":
            payload["username"] = self.username
            payload["password"] = self.password
        elif grant_type == "refresh_token" and refresh_token:
            payload["refresh_token"] = refresh_token
        return self.aes256.encrypt(json.dumps(payload))

    def request_token(self, grant_type, refresh_token=None):
        url = "https://goqual.io/openapi/token" if grant_type == "password" else "https://goqual.io/openapi/token/refresh"
        data = {"data": self.get_encrypted_payload(grant_type, refresh_token)}
        response = requests.post(url, json=data)

        if response.status_code == 200:
            result = response.json()
            self.access_token = result.get("access_token")
            self.refresh_token = result.get("refresh_token")
            self.token_expiry = int(time.time()) + result.get("expires_in", 0)
            print(f"New token acquired: {self.access_token}")
        else:
            raise Exception(f"Failed to acquire token: {response.text}")

    def ensure_token_validity(self):
        current_time = int(time.time())
        if not self.access_token or current_time >= self.token_expiry:
            print("Access token expired or not available. Refreshing token...")
            if self.refresh_token:
                self.request_token("refresh_token", self.refresh_token)
            else:
                print("No refresh token available. Acquiring a new token...")
                self.request_token("password")

    def get_access_token(self):
        self.ensure_token_validity()
        return self.access_token

# Device Control Functions
def list_devices(accessToken):
    headers = {"Authorization": f"Bearer {accessToken}"}
    response = requests.get("https://goqual.io/openapi/devices", headers=headers)
    return response.text

def turnOnTv(accessToken):
    headers = {"Authorization": f"Bearer {accessToken}"}
    body = {"requirments": {"power": True}}
    url = os.getenv("TV_URL")
    response = requests.post(url, headers=headers, json=body)
    print(response.status_code)
    return response.text

def changePs5(accessToken):
    headers = {"Authorization": f"Bearer {accessToken}"}
    url = os.getenv("PS5_URL")
    
    response = requests.post(url, headers=headers, json={"requirments": {"menu": True}})
    print(response.text)
    print(response.status_code)
    
    return response.text

# Flask App Setup
app = Flask(__name__)
token_manager = TokenManager()

@app.route('/v1/remote/tv', methods=['GET'])
def handle_tv_request():
    state = request.args.get('state')
    accessToken = token_manager.get_access_token()
    if state == 'power':
        try:
            response = turnOnTv(accessToken)
            return jsonify({"status": "success", "response": response}), 200
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    elif state == 'ps5':
        try:
            response = changePs5(accessToken)
            return jsonify({"status": "success", "response": response}), 200
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    else:
        return jsonify({"status": "error", "message": "Invalid state parameter"}), 400


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
