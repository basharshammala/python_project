import streamlit as st 
import requests
from token_mange import load_token, generate_long_lived_token

st.title("Facebook Dashboard")
token = load_token()
if not token:
    token = generate_long_lived_token()



url = "https://graph.facebook.com/v21.0/me/accounts"
params = {"access_token": token,
          'fields':['id','name']}
response = requests.get(url, params=params)

pages = response.json()
page_names = [page["name"] for page in pages.get("data", [])]
selected_page = st.selectbox("select the page:", page_names)
st.write("the selected page is :", selected_page)

# st.text('ss')
# st.json(response.json())