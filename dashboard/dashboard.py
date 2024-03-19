import pandas as pd 
import matplotlib.pyplot as plt 
import seaborn as sns 
import streamlit as st 
from babel.numbers import format_currency 
sns.set_theme(style="dark")


def create_product_byreview_df(df):
    product_byreview_df = df.groupby(by=['category_eng']).review_score.mean().reset_index()
    
    return product_byreview_df

def create_product_byrevenue_df(df):
    product_byrevenue_df =df.groupby(by=['category_eng']).payment_value.sum().reset_index()
    
    return product_byrevenue_df

def create_revenue_bystates_df(df):
    revenue_bystates_df = df.groupby("customer_state")["order_id"].count().reset_index().sort_values("order_id", ascending = False).head(10)
    return revenue_bystates_df

def create_rfm_df(df):
    
    
    rfm = df.groupby(by="id", as_index=False).agg({
        "order_purchase_timestamp" : "max",
        "order_id" : "nunique",
        "payment_value" : "sum"
    })
    rfm.columns = ["cust_id", "max_order_timestamp", "frequency", "monetary"]


    rfm["max_order_timestamp"] = rfm["max_order_timestamp"].dt.date
    recent_date = df["order_purchase_timestamp"].dt.date.max()
    rfm["recency"] = rfm["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm.drop("max_order_timestamp", axis=1, inplace= True)
    return rfm


all_df = pd.read_csv("main_data.csv")
all_df.rename(columns={
    "product_category_name_english" : "category_eng"
}, inplace=True)

all_df['id'] = all_df['customer_unique_id'].str[:5]

# all_df = pd.read_csv("rawgithub")

datetime_columns = ["order_purchase_timestamp", "order_delivered_customer_date"]
all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(inplace=True)

for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])
    
    
# Membuat komponen filter
date_min = all_df["order_purchase_timestamp"].min()
date_max = all_df["order_purchase_timestamp"].max()

with st.sidebar:
    # Menambah logo perusahaan
    st.image("shop.png")
    
    # Mengambil start date dan end date dari date input
    
    start_dt, end_dt = st.date_input(
        label='Rentang Waktu', min_value=date_min,
        max_value=date_max,
        value=[date_min, date_max]
    )
    
    
main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_dt)) &
                 (all_df["order_purchase_timestamp"] <= str(end_dt))]

product_byreview_df = create_product_byreview_df(main_df)
product_byrevenue_df = create_product_byrevenue_df(main_df)
revenue_bystates_df = create_revenue_bystates_df(main_df)
rfm = create_rfm_df(main_df)

st.header('OTRA ECommerce Dashboard :sparkles:')

st.subheader('Best and Worst Performing Product Categories Based On Review')


# total_reviews = all_df['review_score'].value_counts().max()
# st.metric("Total Reviews", value=total_reviews)
    
fig, ax = plt.subplots(nrows= 1, ncols= 2, figsize=(50, 20))

all_df.rename(columns={
    "product_category_name_english" : "category_eng"
}, inplace=True)

sns.barplot(x = 'review_score', y = 'category_eng', data=product_byreview_df.sort_values(by='review_score', ascending=False).head(10), palette='magma', ax=ax[0])
ax[0].set_xlabel('Avg Review Score', fontsize=50)
ax[0].set_ylabel(None)
ax[0].set_title('Most Satisfaction', loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=40)
ax[0].tick_params(axis='x', labelsize=35)

sns.barplot(x = 'review_score', y = 'category_eng', data=product_byreview_df.sort_values(by="review_score", ascending=True).head(10), palette='magma', ax=ax[1])
ax[1].set_xlabel('Avg Review Score',  fontsize=50)
ax[1].set_ylabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title('Least Satisfaction', loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=40)
ax[1].tick_params(axis='x', labelsize=35)

plt.tight_layout(pad = 1)

st.pyplot(fig)

st.subheader('Best and Worst Performing Product Categories Based On Revenue')



fig, ax = plt.subplots(nrows= 1, ncols= 2, figsize=(16, 8))


sns.barplot(x = 'payment_value', y = 'category_eng', data=product_byrevenue_df.sort_values(by="payment_value", ascending=False).head(10), palette='viridis', ax=ax[0])
ax[0].set_xlabel(None)
ax[0].set_ylabel(None)
ax[0].set_title('High Revenue', loc="center", fontsize=25)
ax[0].tick_params(axis='y', labelsize=20)
ax[0].tick_params(axis='x', labelsize=15)

sns.barplot(x = 'payment_value', y = 'category_eng', data=product_byrevenue_df.sort_values(by="payment_value", ascending=True).head(10), palette='viridis', ax=ax[1])
ax[1].set_xlabel(None)
ax[1].set_ylabel(None)
ax[1].set_title('Low Revenue',loc="center", fontsize=25)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].tick_params(axis='y', labelsize=20)
ax[1].tick_params(axis='x', labelsize=15)

st.pyplot(fig)

st.subheader('The Highest Orders by States')

fig, ax = plt.subplots(figsize=(16, 8))
sns.barplot(y = "order_id", x = "customer_state", data = revenue_bystates_df , palette = 'plasma')
ax.set_ylabel(None)
ax.set_xlabel("States", fontsize=20)
ax.set_title(None)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)


st.subheader("Customer Based on RFM Parameters")
 
col1, col2, col3 = st.columns(3)
 
with col1:
    avg_recency = round(rfm.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)
    
 
with col2:
    avg_frequency = round(rfm.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)
 
with col3:
    avg_frequency = format_currency(rfm.monetary.mean(), "AUD", locale='es_CO') 
    st.metric("Average Monetary", value=avg_frequency)
 
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))

colors = ["#344e41", "#3a5a40", "#588157", "#a3b18a", "#dad7cd"]


sns.barplot(y="recency", x="cust_id", data=rfm.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("cust_id", fontsize=30)
ax[0].set_title("By recency", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=35)

sns.barplot(y="frequency", x="cust_id", data=rfm.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("cust_id", fontsize=30)
ax[1].set_title("By Frequency", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=35)
 
sns.barplot(y="monetary", x="cust_id", data=rfm.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel("cust_id", fontsize=30)
ax[2].set_title("By Monetary", loc="center", fontsize=50)
ax[2].tick_params(axis='y', labelsize=30)
ax[2].tick_params(axis='x', labelsize=35)
 
st.pyplot(fig)
 
st.caption('Copyright (c) Ade Alvi 2024')


    