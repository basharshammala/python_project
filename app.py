import streamlit as st 
import streamlit_shadcn_ui as ui
import requests
from token_mange import load_token, generate_long_lived_token
import matplotlib.pyplot  as plt
import pandas as pd 
import plotly.express as px
import seaborn as sns
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

@st.cache_data
def get_date(ad_account_id, access_token=token):
     url = f"https://graph.facebook.com/v21.0/{ad_account_id}/insights"
     params = {
    "fields": "date_start,spend,action_values",
    "date_preset": "last_year", 
    "time_increment": 1, 
    "access_token": access_token
    }
     all_data =  []
     while True:
         response = requests.get(url, params=params).json()
         all_data.extend(response.get('data',[]))
         if "paging" in response and "cursors" in response["paging"]:
             after_cursor = response["paging"]["cursors"].get("after")
             if after_cursor:
                 params["after"] = after_cursor
         else:
             break 

        
     return all_data

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
    "fields": "actions,action_values",
    "date_preset": "last_year",  
    "access_token": access_token
    }
    return requests.get(url, params=params).json()

@st.cache_data
def get_top5_purchase_campaigns(ad_account_id, access_token=token):

    campaigns = get_campaigns(ad_account_id, access_token)["data"]
    campaigns_list = []

    for campaign in campaigns:
        campaign_id = campaign["id"]
        insights = get_campaigns_info(campaign_id, access_token)
        if "data" in insights and len(insights["data"]) > 0:
            actions_values = insights["data"][0].get("action_values", [])
            purchase_value = 0
            for item in actions_values:
                if item.get("action_type") == "purchase":
                    purchase_value = float(item.get("value", 0))
            campaigns_list.append({
                "name": campaign.get("name", ""),
                "purchase_value": purchase_value
            })

    top5 = sorted(campaigns_list, key= lambda x: x["purchase_value"], reverse=True)[:5]
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

# get the information for the pages 
selected_col, boxes_col =  st.columns([1,5]) 
page_name =  [ page['name'] for page in get_pages()['data'] ]
with selected_col:
    selected_page = st.selectbox("Select the page:", page_name)
page_info = next((page for page in get_pages()['data'] if page['name'] == selected_page), None)

# get the bussiness account in the pages 
bussiness_account =  get_bussines_account(page_info['id'], page_info['access_token']).get("business",{})
if bussiness_account :
    bussiness_id = bussiness_account.get('id') 
    bussiness_name = bussiness_account.get('name')

    # get the ad_account in bussiness account 
    ad_account = get_adaccounts(bussiness_id, token=token)
    ad_account_list =  ad_account.get('data',[])
    if ad_account_list:
        # create a selected box for ad_accounts
        ad_account_name =  [name.get('name') for name in ad_account_list]
        with selected_col:
            selected_ad_account = st.selectbox("Select the ad_account:", ad_account_name)
        ad_account_info = next((ad for ad in ad_account_list if ad['name'] == selected_ad_account), None)

        # get the currancy for ad account 
        currancy  = get_currancy(ad_account_info['id'])

        # the data for ad_account
        impressions = get_insights(ad_account_info['id'])['data'][0]['impressions']
        spend = get_insights(ad_account_info['id'])['data'][0]['spend']
        clicks = get_insights(ad_account_info['id'])['data'][0]['clicks']
        purchase = get_insights(ad_account_info['id'])['data'][0]['actions'][2]['value']
        omni_add_to_cart = get_insights(ad_account_info['id'])['data'][0]['actions'][3]['value'] 
        purchase_value = get_insights(ad_account_info['id'])['data'][0]['action_values'][0]['value']

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
        
        # divide pages into 4 boxes to place advertising ad account 
        with boxes_col:
            col1, col2, col3, col4 = st.columns(4)
            with col1 : 
                # col1.metric(label="👀 Impressions", value=f"{float(impressions):,}")
                ui.metric_card(title="👀 Impressions", content=f"{float(impressions):,}", description="+20.1% from last month", key="card1")
                
            with col2:
                # col2.metric(label="🖱️ Clicks", value=f"{float(clicks):,}")
                ui.metric_card(title="🖱️ Clicks", content=f"{float(clicks):,}", description="+20.1% from last month", key="card2")
                

            with col3:
                # col3.metric(label="💰 Spend", value=f"{float(spend):,} {currancy['currency']}")
                ui.metric_card(title="💰 Spend", content=f"{float(spend):,}", description="+20.1% from last month", key="card3")

            with col4:
                # col4.metric(label="🛒 Purchases", value=f"{float(purchase):,}")
                ui.metric_card(title="🛒 Purchases", content=f"{float(purchase):,}", description="+20.1% from last month", key="card4")
            
            col5, col6, col7, col8 = st.columns(4)
            with col5:
                # col5.metric(label="💵 Purchase Value", value=f"{float(purchase_value):,} {currancy['currency']}")
                ui.metric_card(title="💵 Purchase Value", content=f"{float(purchase_value):,} {currancy['currency']}", description="+20.1% from last month", key="card5")

            with col6:
                # col6.metric(label="📈 ROAS", value=f"{roas:,}")
                ui.metric_card(title="📈 ROAS", content=f"{roas:,}", description="+20.1% from last month", key="card6")

            with col7:
                # col7.metric(label="🖱️ CPC", value=f"{cpc:,} {currancy['currency']}")
                ui.metric_card(title="🖱️ CPC", content=f"{cpc:,} {currancy['currency']}", description="+20.1% from last month", key="card7")

            with col8:
                # col8.metric(label="🎯 CPA", value=f"{cpa:,} {currancy['currency']}")
                ui.metric_card(title="🎯 CPA", content=f"{cpa:,} {currancy['currency']}", description="+20.1% from last month", key="card8")
        
 
        st.markdown("##")
        top_col, shape_col =  st.columns([2,1])
        with top_col:
            st.subheader('Top 5 camp')
            for campaign in get_top5_purchase_campaigns(ad_account_info['id']):
                col_name, col_value, col_bar = st.columns([2, 1, 5])

                # اسم الحملة
                with col_name:
                    st.write(campaign["name"])
                # قيمة الشراء
                with col_value:
                    st.write(campaign["purchase_value"])
                # رسم شريطي أفقي
                with col_bar:
                    fig = px.bar(
                        x=[campaign["purchase_value"]],
                        y=[campaign["name"]],
                        orientation='h',
                        # text=[campaign["purchase_value"]],
                        width=400,
                        height=50,
                        range_x=[0, max([c["purchase_value"] for c in get_top5_purchase_campaigns(ad_account_info['id'])])*1.1]
                    )
                    fig.update_traces(marker_color='skyblue', textposition='outside')
                    fig.update_layout(
                        xaxis_title='',  # إزالة عنوان المحور x
                        yaxis_title='',  
                        xaxis=dict(showticklabels=False),
                        yaxis=dict(showticklabels=False),
                        margin=dict(l=0, r=0, t=0, b=0),
                        height=50
                    )
                    st.plotly_chart(fig, use_container_width=True)

# ----------- الرسم الثاني: Spend vs Purchase Value -----------

        with shape_col:
            st.subheader('spend vs purchases')
            # st.json(get_date(ad_account_info['id']))
            df_list = []
            for item in get_date(ad_account_info['id']):
                date = item["date_start"]
                spend = float(item.get("spend", 0))
                pv = 0
                for val in item.get("action_values", []):
                    if val.get("action_type") == "purchase":
                        pv = float(val.get("value", 0))
                df_list.append({"date": date, "spend": spend, "purchase": pv})

            df = pd.DataFrame(df_list)
            df["date"] = pd.to_datetime(df["date"])
            df.sort_values("date", inplace=True)

            fig2 = px.line(
                df,
                x="date",
                y=["spend", "purchase"],
                markers=True,
                labels={"value":"Value", "variable":"Metric", "date":"Date"},
                width=600,
                height=400
            )
            fig2.update_layout(
                legend=dict(title="Metrics"),
                xaxis_title="Date",
                yaxis_title="Value",
                margin=dict(l=20, r=20, t=20, b=20)
            )
            st.plotly_chart(fig2, use_container_width=True)

    else :
         st.write("there is no a ad_account..........")
         
    
         
else :
     st.write("there is no a bussiness account..........")














