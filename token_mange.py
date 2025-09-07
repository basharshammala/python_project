import requests
import json
import os

TOKEN_FILE = "token.json"
app_id = "1084712410505235"
app_secret = "45e3afc8d75b1d0802390e499e0a2982"
short_lived_token = "EAAPaiknpYBMBPY17c2BjVlN4YmCMr0vaCzZCluA62hRIaFGBGUzR30WdGar4LfBAbLJxZC2WX2cQXYDvXTUMF4MY9xppZBkHQEMW1BAYXpJCxTrbN8CF6zxF1dRezW5zhUwZBwmApZAkjXV6KD2en0JEQlZAflXwP9avvTGWw84Bw2VQzwBlzT4dDRDkZCU1vpniUHyVhPqvF4ZCjkc3Hxf41kZBBNaQTNZAQ1w34BKOMRzNpZAPYsd"

def save_token(token):
    with open(TOKEN_FILE, "w") as f:
        json.dump({"access_token": token}, f)

def load_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            return json.load(f).get("access_token")
    return None
def generate_long_lived_token(short_lived_token=short_lived_token):
    url = "https://graph.facebook.com/v21.0/oauth/access_token"
    params = {
        "grant_type": "fb_exchange_token",
        "client_id": app_id,
        "client_secret": app_secret,
        "fb_exchange_token": short_lived_token
    }
    response = requests.get(url, params=params)
    token = response.json().get("access_token")
    if token:
        save_token(token)
    return token
