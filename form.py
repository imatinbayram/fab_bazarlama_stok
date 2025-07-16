import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Load customer data
customer_df = pd.read_excel("customer.xlsx")

st.title("FAB - Bazarlama")

# Select Region
region = st.selectbox("Filial seçin:", sorted(customer_df['region'].unique()))

# Filter customers by region
filtered_customers = customer_df[customer_df['region'] == region]

# Select Customer Name
name = st.selectbox("Müştəri seçin:", filtered_customers['name'].tolist())

# Get Customer Code for selected name
customer_row = filtered_customers[filtered_customers['name'] == name].iloc[0]
code = customer_row['code']

st.write(f"**Müştəri kodu:** `{code}`")

# Start form
with st.form("feedback_form"):
    fab = st.radio("Mağazada FAB Boya məhsulları var?", ["Bəli", "Xeyr"])
    fab_percent = st.number_input("FAB Boya məhsullarının mağazadakı ümumi boya məhsullarına görə payı neçə faizdir?", min_value=0, max_value=100, step=1) if fab == "Yes" else ""

    sobsan = st.radio("Mağazada Sobsan məhsulları var?", ["Bəli", "Xeyr"])
    sobsan_percent = st.number_input("Sobsan məhsullarının mağazadakı ümumi boya məhsullarına görə payı neçə faizdir?", min_value=0, max_value=100, step=1) if sobsan == "Yes" else ""

    submitted = st.form_submit_button("Təsdiqlə")

    if submitted:
        # Create a result row
        new_row = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "region": region,
            "code": code,
            "name": name,
            "fab": fab,
            "fab_percent": fab_percent,
            "sobsan": sobsan,
            "sobsan_percent": sobsan_percent
        }

        # Load or create result.xlsx
        result_file = "result.xlsx"
        if os.path.exists(result_file):
            result_df = pd.read_excel(result_file)
            result_df = pd.concat([result_df, pd.DataFrame([new_row])], ignore_index=True)
        else:
            result_df = pd.DataFrame([new_row])

        # Save updated results
        result_df.to_excel(result_file, index=False)
        st.success("Məlumatlar göndərildi!")
