import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from io import BytesIO
from github import Github
import os

# ---------- CONFIG ----------
GITHUB_REPO = "fab_boya_form"
GITHUB_USER = "imatinbayram"
GITHUB_FILE_PATH = "result.xlsx"
RAW_GITHUB_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/{GITHUB_FILE_PATH}"

# ---------- LOAD EXISTING RESULT ----------
@st.cache_data(show_spinner=False)
def load_github_excel():
    try:
        response = requests.get(RAW_GITHUB_URL)
        if response.status_code == 200:
            return pd.read_excel(BytesIO(response.content))
    except:
        pass
    return pd.DataFrame()

# ---------- PUSH TO GITHUB ----------
def push_to_github(local_file, repo_name, token, commit_message, github_file_path):
    g = Github(token)
    repo = g.get_user().get_repo(repo_name)

    with open(local_file, "rb") as f:
        content = f.read()

    try:
        existing = repo.get_contents(github_file_path)
        repo.update_file(github_file_path, commit_message, content, existing.sha)
    except:
        repo.create_file(github_file_path, commit_message, content)

# ---------- STREAMLIT SESSION ----------
st.set_page_config(page_title="FAB - Bazarlama", layout="centered")

if "submitted" not in st.session_state:
    st.session_state.submitted = False

def restart_app():
    st.session_state.submitted = False
    st.rerun()

# ---------- UI ----------
st.title("FAB - Bazarlama")

customer_df = pd.read_excel("customer.xlsx")

if not st.session_state.submitted:
    regions = ["---"] + sorted(customer_df["region"].unique())
    region = st.selectbox("Filial seçin:", regions)

    if region != "---":
        customers = customer_df[customer_df["region"] == region]
        names = ["---"] + customers["name"].tolist()
        name = st.selectbox("Müştəri seçin:", names)

        if name != "---":
            code = customers[customers["name"] == name]["code"].iloc[0]
            st.write(f"**Müştəri kodu:** `{code}`")

            with st.form("form"):
                fab = st.radio("Mağazada FAB Boya məhsulları var?", ["", "Bəli", "Xeyr"], index=0)
                fab_percent = None
                if fab == "Bəli":
                    fab_percent = st.number_input("FAB məhsullarının mağazadakı payı (%)", 0, 100, step=1)

                sobsan = st.radio("Mağazada Sobsan məhsulları var?", ["", "Bəli", "Xeyr"], index=0)
                sobsan_percent = None
                if sobsan == "Bəli":
                    sobsan_percent = st.number_input("Sobsan məhsullarının mağazadakı payı (%)", 0, 100, step=1)

                submit = st.form_submit_button("Təsdiqlə")

                if submit:
                    if fab == "" or sobsan == "":
                        st.warning("Zəhmət olmasa bütün sualları cavablandırın.")
                    else:
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

                        # Load existing data
                        df = load_github_excel()
                        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

                        # Save locally
                        df.to_excel("result.xlsx", index=False)

                        # Push to GitHub
                        push_to_github(
                            local_file="result.xlsx",
                            repo_name=GITHUB_REPO,
                            token=st.secrets["github_token"],
                            commit_message="Update result.xlsx via Streamlit form",
                            github_file_path=GITHUB_FILE_PATH
                        )

                        st.session_state.submitted = True
                        st.rerun()

else:
    st.success("Məlumatlar uğurla göndərildi!")
    if st.button("Yeni"):
        restart_app()
