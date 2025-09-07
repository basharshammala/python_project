import streamlit as st 
import requests
from token_mange import load_token, generate_long_lived_token

st.title("Facebook Dashboard")

token = load_token()
if not token:
    token = generate_long_lived_token()

@st.cache_data
def get_pages(token=token):
    url = "https://graph.facebook.com/v21.0/me/accounts"
    params = {"access_token": token}
    return requests.get(url, params=params)

# جلب الرد وتحويله للقائمة
pages_response = get_pages()
pages_json = pages_response.json()
pages_list = pages_json.get("data", [])  # هنا صار عندك القائمة الصحيحة

# قائمة أسماء الصفحات للـ selectbox
page_names = [page["name"] for page in pages_list]
selected_page = st.selectbox("Select the page:", page_names)

# الحصول على بيانات الصفحة المختارة من القائمة
page_info = next((p for p in pages_list if p["name"] == selected_page), None)

# @st.cache_data
# def get_page_insights(page_id=page_info["id"], page_token=page_info["access_token"]):
#     metrics = "page_impressions,page_posts_impressions"
#     url = f"https://graph.facebook.com/v21.0/{page_id}/insights"
#     params = {"metric": metrics, "access_token": page_token}
#     response = requests.get(url, params=params)
#     data = response.json().get("data", [])
#     return data

# insights = get_page_insights()

# if insights:
#     for metric in insights:
#         st.write("Metric:", metric.get("name"))
#         st.write("Period:", metric.get("period"))
#         st.write("Values:", metric.get("values"))
#         st.markdown("---")
# else:
#     st.warning("لم يتم العثور على بيانات تحليلية لهذه الصفحة.")
if page_info:
    st.write("Page Name:", page_info["name"])
    st.write("Page ID:", page_info["id"])
    st.write("Page Access Token:", page_info["access_token"])
