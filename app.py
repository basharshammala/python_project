import streamlit as st 
import requests
from token_mange import load_token, generate_long_lived_token

st.title("Facebook Dashboard")

token = load_token()
ad_account = ""
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
page_info = next((p for p in pages_list if p["name"] == selected_page), None)
if page_info:
    st.write("Page Name:", page_info["name"])
    st.write("Page ID:", page_info["id"])
    st.write("Page Access Token:", page_info["access_token"])

@st.cache_data
def get_adaccounts(page_id, page_access_token):
        url = f"https://graph.facebook.com/v21.0/{page_id}"
        params = {
            "fields": "id,name,connected_instagram_account,business",
            "access_token": page_access_token
        }
        return requests.get(url, params=params).json()

page_details = get_adaccounts(page_info["id"], page_info["access_token"])
    
    # إذا الصفحة تابعة لعمل (Business) نجلب الحسابات الإعلانية
business_id = page_details.get("business", {}).get("id")
if business_id:
    @st.cache_data
    def get_business_adaccounts(business_id, token):
        url = f"https://graph.facebook.com/v21.0/{business_id}/owned_ad_accounts"
        params = {"access_token": token}
        return requests.get(url, params=params).json()

    adaccounts_json = get_business_adaccounts(business_id, token)
        
        # استخراج account_id فقط
    adaccounts_list = adaccounts_json.get("data", [])
    for ad in adaccounts_list:
        ad_account = ad.get("id")
        st.write("account_id:", ad.get("id"))

else:
        st.info("No business linked, cannot fetch ad accounts directly.")

@st.cache_data
def get_insights(ad_account_id, access_token=token):
     url = f"https://graph.facebook.com/v21.0/{ad_account_id}/insights"
     params = {
    "fields": "impressions,reach,spend,clicks,actions,action_values",
    "date_preset": "last_year",  # آخر 30 يوم، يمكن تغييره
    "access_token": access_token
    }
     return requests.get(url, params=params)
insigths = get_insights( ad.get("id"))
data =  insigths.json()
# st.write(data['data'])
st.json(data['data'][0])




















# الحصول على بيانات الصفحة المختارة من القائمة
# page_info = next((p for p in pages_list if p["name"] == selected_page), None)

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
# if page_info:
#     st.write("Page Name:", page_info["name"])
#     st.write("Page ID:", page_info["id"])
#     st.write("Page Access Token:", page_info["access_token"])



# ad_account_id = "1739460083058612"
# access_token = "EAAtwRjCJ9ZAwBPZAg9hYWwEQHf4wLUXNStambAZBBSAxcYZApOZBJG5uOt3pKmtlcn07z2XGHwuGHDvDdmzxZCH4z6u8YdYSvFAOX8vjGqL70vrkri2RGaeDZAIDqaS0hegtY9BlMpPlTZBaLHZAisMEH2edjWPkiCq3Vgt92hmnEfuEyfTyTPe42GKzulbK2PfhlzAH2"



# url = f"https://graph.facebook.com/v21.0/act_{ad_account_id}/insights"
# params = {
#     "fields": "impressions,reach,spend",
#     "date_preset": "last_30d",  # يمكن تغيير الفترة
#     "access_token": access_token
# }

# response = requests.get(url, params=params)
# data = response.json().get("data", [])

# for entry in data:
#     st.write("Impressions:", entry.get("impressions"))
#     st.write("Reach:", entry.get("reach"))
#     st.write("Spend:", entry.get("spend"))