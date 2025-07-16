import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Load customer data
customer_df = pd.read_excel("customer.xlsx")

st.title("FAB - Bazarlama")

# Add "---" to start of region list
regions = ["---"] + sorted(customer_df['region'].unique().tolist())
region = st.selectbox("Filial seçin:", regions)

# Only proceed if a valid region is selected
if region != "---":
    # Filter customers by region
    filtered_customers = customer_df[customer_df['region'] == region]
    customer_names = ["---"] + filtered_customers['name'].tolist()

    # Customer selection
    name = st.selectbox("Müştəri seçin:", customer_names)

    # Only proceed if valid customer is selected
    if name != "---":
        customer_row = filtered_customers[filtered_customers['name'] == name].iloc[0]
        code = customer_row['code']
        st.write(f"**Müştəri kodu:** `{code}`")

        # Form
        with st.form("feedback_form"):
            fab = st.radio("Mağazada FAB Boya məhsulları var?", ["Bəli", "Xeyr"], key="fab")
            fab_percent = None
            if fab == "Bəli":
                fab_percent = st.number_input(
                    "FAB Boya məhsullarının mağazadakı ümumi boya məhsullarına görə payı neçə faizdir?",
                    min_value=0, max_value=100, step=1, key="fab_percent"
                )

            sobsan = st.radio("Mağazada Sobsan məhsulları var?", ["Bəli", "Xeyr"], key="sobsan")
            sobsan_percent = None
            if sobsan == "Bəli":
                sobsan_percent = st.number_input(
                    "Sobsan məhsullarının mağazadakı ümumi boya məhsullarına görə payı neçə faizdir?",
                    min_value=0, max_value=100, step=1, key="sobsan_percent"
                )

            submitted = st.form_submit_button("Təsdiqlə")

            if submitted:
                new_row = {
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "region": region,
                    "code": code,
                    "name": name,
                    "fab": fab,
                    "fab_percent": fab_percent if fab == "Bəli" else "",
                    "sobsan": sobsan,
                    "sobsan_percent": sobsan_percent if sobsan == "Bəli" else ""
                }

                # Save to result.xlsx
                result_file = "result.xlsx"
                if os.path.exists(result_file):
                    result_df = pd.read_excel(result_file)
                    result_df = pd.concat([result_df, pd.DataFrame([new_row])], ignore_index=True)
                else:
                    result_df = pd.DataFrame([new_row])

                result_df.to_excel(result_file, index=False)
                st.success("Məlumatlar uğurla göndərildi!")
