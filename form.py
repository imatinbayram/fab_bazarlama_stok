import streamlit as st
import pandas as pd
import requests
import warnings

# Xəbərdarlıqları gizlət
warnings.simplefilter("ignore")

# Başlıq
st.title("📦 Stok Siyahısı - Prim Oranı və Depo Miktarı")

# API ünvanı və başlıqlar
api_url = "http://81.17.83.210:1999/api/Metin/GetQueryTable"
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# SQL sorğusu
sql_query = """
SELECT
    sto_isim,
    sto_kod,
    sto_prim_orani,
    dbo.fn_DepolardakiMiktarB(sto_kod, CONVERT(nvarchar(10), GETDATE(), 120)) AS miktar
FROM
    STOKLAR
WHERE
    sto_prim_orani IN (1, 2, 3, 4, 5);
"""

# JSON bədənində göndərmək üçün format
query_json = {
    "Query": sql_query
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
                csv = df.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label="📥 Excel kimi yüklə",
                    data=csv,
                    file_name="stok_melumatlari.csv",
                    mime='text/csv'
                )
        else:
            st.error(f"❌ API xətası: {result['Message']}")

    except requests.exceptions.RequestException as e:
        st.error(f"🔌 Bağlantı xətası: {e}")
    except Exception as e:
        st.error(f"🚫 Xəta baş verdi: {e}")
