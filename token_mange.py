import requests
import json
import os

TOKEN_FILE = "token.json"
app_id = "3219671508186524"
app_secret = "5d26dfced24f032fb68de028be9ed0e9"
short_lived_token = "EAAtwRjCJ9ZAwBPdPmxcIzGqTHqMA4F8z7vZA443lOyUKxceaeQwZCq628VEoiNNrJ31y5aGxZBstzG2DzZC69o4RZCcFH8ZAn2TbCGqFzQW02DGZArbgaWruND1Gs1XZC35O9ZCa7zZCY1BFVleeJ9iU4lx4sDXKi6K1ZCZBAqJuZCwfftIm4qV0dkhVx8fJwd4YbWoLhePJ6LZB90IkeaLWTjZBQgFiZAsIyytLd3esW"

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
