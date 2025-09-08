import requests
import json
import os

TOKEN_FILE = "token.json"
app_id = "3219671508186524"
app_secret = "5d26dfced24f032fb68de028be9ed0e9"
short_lived_token = "EAAtwRjCJ9ZAwBPXEwKWKhnOPajHGYOdt3m3ekEh0eWjtGRe2lnrOA5Ez0KUf5wxY6LZCJUxjelpY8t6QOEy1SAriMN89zxWCZBzFA4BDKB3Anp7QWK7H5mjEQLZAC6UMQCuRNrr9jpZBZAPCXW98ZBBR4SCiLfB9nLr6oNHvSZAPRgqV64jjIqRTFkEbXhqHLcZCcFTrm9ZA3BGHGdBiZBjxMBzumUQiS65ZBVAw"

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
