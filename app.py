import streamlit as st
import pandas as pd

# Kullanıcılar (şimdilik sabit)
users = {
    "admin": "admin123",
    "firma_ahmet": "ahmet2024",
    "firma_oto": "oto2024"
}

# Login fonksiyonu
def login():
    st.title("🔐 Giriş Yap")

    username = st.text_input("Kullanıcı Adı")
    password = st.text_input("Şifre", type="password")

    if st.button("Giriş"):
        if username in users and users[username] == password:
            st.session_state["logged_in"] = True
        else:
            st.error("Hatalı giriş")

# Login kontrol
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    login()
    st.stop()

# ===== ANA SİSTEM =====

st.title("📦 AI Satınalma Asistanı")

file = st.file_uploader("Excel yükle", type=["xlsx"])

if file:
    df = pd.read_excel(file)

    results = []

    for _, row in df.iterrows():
        alinacak = max(
            (row["Aylık Tüketim"]/30 * row["Tedarik Süresi"] + row["Aylık Tüketim"]*0.3)
            - row["Mevcut Stok"], 0
        )

        results.append({
            "Stok Kodu": row["Stok Kodu"],
            "Ürün": row["Ürün Adı"],
            "Alınacak": round(alinacak),
            "Tedarikçi": row["Tedarikçi"],
            "Maliyet": round(alinacak * row["Birim Fiyat"], 2)
        })

    result_df = pd.DataFrame(results)

    st.dataframe(result_df)
    st.write("Toplam:", result_df["Maliyet"].sum(), "TL")