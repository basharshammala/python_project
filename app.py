import streamlit as st 
import requests
from token_mange import load_token, generate_long_lived_token

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
             st.metric(label="👀 Impressions", value=impressions)
        with col2:
            st.metric(label="🖱️ Clicks", value=clicks)
        with col3:
            st.metric(label="💰 Spend", value=spend)
        with col4:
            st.metric(label="🛒 Purchases", value=purchase)
        
        col5, col6, col7, col8 = st.columns(4)
        with col5:
            st.metric(label="💵 Purchase Value", value=purchase_value)

        with col6:
            st.metric(label="📈 ROAS", value=roas)

        with col7:
            st.metric(label="🖱️ CPC", value=f"${cpc}")

        with col8:
            st.metric(label="🎯 CPA", value=f"${cpa}")

        


        


    else :
         st.write("there is no a ad_account..........")
         
    
         
else :
     st.write("there is no a bussiness account..........")














