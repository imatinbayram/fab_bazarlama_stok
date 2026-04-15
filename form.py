import streamlit as st
import pandas as pd
import requests
import warnings
import io

# Xəbərdarlıqları gizlət
warnings.simplefilter("ignore")

# Başlıq
st.title("📦 Stok Siyahısı - Depo Miktarı")

#Sehifenin nastroykasi
st.set_page_config(
    page_title='📦 Stok Siyahısı - Depo Miktarı',
    page_icon='logo.png',
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "# FAB Markalar \n Bu hesabat FAB şirkətlər qrupu üçün hazırlanmışdır."
    }
)

css_header = """
<style>

    [data-testid="stHeader"] {
        display: none;
    }
    
    [data-testid="stElementToolbar"] {
        display: none;
    }
    
</style>
<title>FAB MARKALAR</title>
<meta name="description" content="FAB Şirkətlər Qrupu" />
"""

st.markdown(css_header, unsafe_allow_html=True)


# API ünvanı və başlıqlar
api_url = "http://81.17.83.210:1999/api/Metin/GetQueryTable"
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# SQL sorğusu
sql_query = """
SELECT
    sto_isim STOK_AD,
    sto_kod STOK_KOD,
    sto_prim_orani BAZARLAMA_QOL,
    MikroDB_V16_05.dbo.fn_DepolardakiMiktarB(sto_kod, CONVERT(nvarchar(10), GETDATE(), 120)) AS MIQDAR
FROM
    MikroDB_V16_05.dbo.STOKLAR
WHERE
    sto_prim_orani IN (1, 2, 3, 4, 5);
"""

# JSON bədənində göndərmək üçün format
query_json = {
    "Query": sql_query,
    "Kod": "QVERTY"
}

# API sorğusu göndərilir
with st.spinner("Məlumatlar yüklənir..."):
    try:
        response = requests.get(api_url, json=query_json, headers=headers, verify=False)
        response.raise_for_status()
        result = response.json()

        if result["Code"] == 0:
            df = pd.DataFrame(result["Data"])
            if df.empty:
                st.warning("⚠️ Nəticə tapılmadı.")
            else:
                st.success("✅ Məlumat uğurla alındı.")
                st.dataframe(df, use_container_width=True)
                
                # Yükləmə düyməsi
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, sheet_name='Stoklar')
                
                excel_data = output.getvalue()
                
                st.download_button(
                    label="📥 Excel kimi yüklə",
                    data=excel_data,
                    file_name="stok_melumatlari.xlsx",
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
        else:
            st.error(f"❌ API xətası: {result['Message']}")

    except requests.exceptions.RequestException as e:
        st.error(f"🔌 Bağlantı xətası: {e}")
    except Exception as e:
        st.error(f"🚫 Xəta baş verdi: {e}")
