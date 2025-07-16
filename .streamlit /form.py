import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Load customer data
customer_df = pd.read_excel("customer.xlsx")

st.title("Customer Feedback Form")

# Select Region
region = st.selectbox("Select Region", sorted(customer_df['region'].unique()))

# Filter customers by region
filtered_customers = customer_df[customer_df['region'] == region]

# Select Customer Name
name = st.selectbox("Select Customer", filtered_customers['name'].tolist())

# Get Customer Code for selected name
customer_row = filtered_customers[filtered_customers['name'] == name].iloc[0]
code = customer_row['code']

st.write(f"**Customer Code:** `{code}`")

# Start form
with st.form("feedback_form"):
    fab = st.radio("FAB?", ["Yes", "No"])
    fab_percent = st.number_input("FAB Percent", min_value=0, max_value=100, step=1) if fab == "Yes" else ""

    sobsan = st.radio("Sobsan?", ["Yes", "No"])
    sobsan_percent = st.number_input("Sobsan Percent", min_value=0, max_value=100, step=1) if sobsan == "Yes" else ""

    submitted = st.form_submit_button("Submit")

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
        st.success("Form submitted and saved to result.xlsx")
