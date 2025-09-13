import streamlit as st 
import requests
from token_mange import load_token, generate_long_lived_token
import matplotlib.pyplot  as plt

# app config 
st.set_page_config(page_title='FacebookDashboard', page_icon="🌍", layout="wide")
st.subheader("🌍 Facebook Dashboard")
# st.markdown("##")


token = load_token()
ad_account = ""
if not token:
    token = generate_long_lived_token()

# ====================================================================================
# get the pages information from the accounts 
@st.cache_data
def get_pages(token=token):
    url = "https://graph.facebook.com/v21.0/me/accounts"
    params = {"access_token": token}
    return requests.get(url, params=params).json()

# get the bussines id 
@st.cache_data
def get_bussines_account(page_id, page_access_token):
        url = f"https://graph.facebook.com/v21.0/{page_id}"
        params = {
            "fields": "id,name,business",
            "access_token": page_access_token
        }
        return requests.get(url, params=params).json()

# get the accounts that connect by the adaccount
@st.cache_data
def get_adaccounts(business_id, token):
    url = f"https://graph.facebook.com/v21.0/{business_id}/owned_ad_accounts"
    params = {"fields":"id,account_id,name",
         "access_token": token}
    return requests.get(url, params=params).json()

# get the insights for the account 
@st.cache_data
def get_insights(ad_account_id, access_token=token):
     url = f"https://graph.facebook.com/v21.0/{ad_account_id}/insights"
     params = {
    "fields": "impressions,reach,spend,clicks,actions,action_values",
    "date_preset": "last_year",  
    "access_token": access_token
    }
     return requests.get(url, params=params).json()

# get the campaigns
@st.cache_data
def get_campaigns(ad_account_id, access_token=token):
     url = f"https://graph.facebook.com/v21.0/{ad_account_id}/campaigns"
     params = {
    "fields": "name,insights",
    "date_preset": "last_year",  
    "access_token": access_token
    }
     return requests.get(url, params=params).json()

# get the info about the campaigns
@st.cache_data
def get_campaigns_info(campaign_id,access_token=token):
    url = f"https://graph.facebook.com/v21.0/{campaign_id}/insights"
    params = {
    "fields": "spend,clicks,impressions,actions,action_values",
    "date_preset": "last_year",  
    "access_token": access_token
    }
    return requests.get(url, params=params).json()

@st.cache_data
def get_top5_purchase_campaigns(ad_account_id, access_token=token):
    # جلب جميع الحملات
    campaigns = get_campaigns(ad_account_id, access_token)["data"]
    
    campaigns_list = []
    
    for campaign in campaigns:
        campaign_id = campaign["id"]
        insights = get_campaigns_info(campaign_id, access_token)
        if "data" in insights and len(insights["data"]) > 0:
            actions_values = insights["data"][0].get("action_values", [])
            # البحث عن قيمة الشراء purchase
            purchase_value = 0
            for item in actions_values:
                if item.get("action_type") == "purchase":
                    purchase_value = float(item.get("value", 0))
            campaigns_list.append({
                "name": campaign.get("name", ""),
                "purchase_value": purchase_value
            })
    
    # ترتيب الحملات حسب قيمة الشراء واختيار أعلى 5
    top5 = sorted(campaigns_list, key=lambda x: x["purchase_value"], reverse=True)[:5]
    return top5

# get the currancy 
@st.cache_data
def get_currancy (ad_account_id,access_token=token) : 
     url = f"https://graph.facebook.com/v21.0/{ad_account_id}"
     params = {
    "fields": "currency",
    "access_token": access_token
    }
     return requests.get(url, params=params).json()


# ====================================================================================
page_name =  [ page['name'] for page in get_pages()['data'] ]
selected_page = st.selectbox("Select the page:", page_name)
page_info = next((page for page in get_pages()['data'] if page['name'] == selected_page), None)
# if page_info : 
#      st.write(f'PageName: {page_info['name']}')
#      st.write(f'PageName: {page_info['id']}')
#      st.write(f'PageName: {page_info['access_token']}')

# get bussines account
# st.json(get_bussines_account(page_info['id'], page_info['access_token']))

bussiness_account =  get_bussines_account(page_info['id'], page_info['access_token']).get("business",{})
if bussiness_account :
    bussiness_id = bussiness_account.get('id') 
    bussiness_name = bussiness_account.get('name')
    ad_account = get_adaccounts(bussiness_id, token=token)
    # st.json(ad_account)
    ad_account_list =  ad_account.get('data',[])
    if ad_account_list:
        # st.write(ad_account_list)
        ad_account_name =  [name.get('name') for name in ad_account_list]
        selected_ad_account = st.selectbox("Select the ad_account:", ad_account_name)
        ad_account_info = next((ad for ad in ad_account_list if ad['name'] == selected_ad_account), None)
        currancy  = get_currancy(ad_account_info['id'])
        st.write(f"the currancy for this account is : {currancy['currency']}")
        # the data for ad_account
        impressions = get_insights(ad_account_info['id'])['data'][0]['impressions']
        spend = get_insights(ad_account_info['id'])['data'][0]['spend']
        clicks = get_insights(ad_account_info['id'])['data'][0]['clicks']
        purchase = get_insights(ad_account_info['id'])['data'][0]['actions'][2]['value']
        omni_add_to_cart = get_insights(ad_account_info['id'])['data'][0]['actions'][3]['value'] 
        purchase_value = get_insights(ad_account_info['id'])['data'][0]['action_values'][0]['value']
        # roas  =round(float(purchase_value)/float(spend), 3 ) 
        # cpc = round(float(spend)/ float(clicks), 3)
        if float(spend) > 0:
            roas = round(float(purchase_value) / float(spend), 3)
        else:
            roas = 0.0   

        if float(purchase) > 0 : 
            cpa = round(float(spend) / float(purchase), 3)  
        else :
            cpa = 0.0

        
        if float(clicks) > 0:
            cpc = round(float(spend) / float(clicks), 3)
        else:
            cpc = 0.0
        col1, col2, col3, col4 = st.columns(4)
        with col1 : 
             st.metric(label="👀 Impressions", value=f"{float(impressions):,}")
        with col2:
            st.metric(label="🖱️ Clicks", value=f"{float(clicks):,}")
        with col3:
            st.metric(label="💰 Spend", value=f"{float(spend):,} {currancy['currency']}")
        with col4:
            st.metric(label="🛒 Purchases", value=f"{float(purchase):,}")
        
        col5, col6, col7, col8 = st.columns(4)
        with col5:
            st.metric(label="💵 Purchase Value", value=f"{float(purchase_value):,} {currancy['currency']}")

        with col6:
            st.metric(label="📈 ROAS", value=f"{roas:,}")

        with col7:
            st.metric(label="🖱️ CPC", value=f"{cpc:,} {currancy['currency']}")

        with col8:
            st.metric(label="🎯 CPA", value=f"{cpa:,} {currancy['currency']}")
        
        # st.json(get_campaigns(ad_account_info['id']))
        id = get_campaigns(ad_account_info['id'])
        
        # st.json(get_campaigns_info(id['data'][5]['id']))
        # st.write(get_top5_purchase_campaigns(ad_account_info['id']))
        for campaign in get_top5_purchase_campaigns(ad_account_info['id']):
            col_name, col_value, col_bar = st.columns([2, 1, 5])  # تقسيم الأعمدة
            with col_name:
                st.write(campaign["name"])
            with col_value:
                st.write(campaign["purchase_value"])
            with col_bar:
        # رسم شريطي صغير
                fig, ax = plt.subplots(figsize=(4, 0.3))  # ارتفاع صغير للـ mini bar
                ax.barh([0], [campaign["purchase_value"]], color='skyblue')
                ax.set_xlim(0, max([c["purchase_value"] for c in get_top5_purchase_campaigns(ad_account_info['id'])]) * 1.1)  # مقياس موحد
                ax.axis('off')  # إزالة المحاور
                st.pyplot(fig)

        


        


    else :
         st.write("there is no a ad_account..........")
         
    
         
else :
     st.write("there is no a bussiness account..........")














