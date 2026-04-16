import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

st.set_page_config(page_title="AI Satınalma Asistanı", layout="wide")

USER_FILE = "users.json"

# ===== USER LOAD =====
def load_users():
    if not os.path.exists(USER_FILE):
        return {}
    with open(USER_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)

users = load_users()

# ===== MENU =====
menu = st.sidebar.selectbox("Menü", ["Giriş Yap", "Kayıt Ol"])

# ===== LOGIN =====
def login():
    st.title("🔐 Giriş Yap")

    username = st.text_input("Kullanıcı Adı")
    password = st.text_input("Şifre", type="password")

    if st.button("Giriş"):
        if username in users and users[username]["password"] == password:
            st.session_state["logged_in"] = True
            st.session_state["user"] = username
        else:
            st.error("Hatalı giriş")

# ===== REGISTER =====
def register():
    st.title("📝 Kayıt Ol")

    username = st.text_input("Kullanıcı Adı")
    password = st.text_input("Şifre", type="password")
    email = st.text_input("Email")
    company = st.text_input("Firma Adı")

    if st.button("Kayıt Ol"):
        if username in users:
            st.error("Bu kullanıcı zaten var")
        elif not username or not password or not email or not company:
            st.error("Tüm alanları doldurun")
        else:
            users[username] = {
                "password": password,
                "role": "user",
                "email": email,
                "company": company,
                "subscription": "inactive",
                "trial_start": datetime.now().strftime("%Y-%m-%d")
            }
            save_users(users)
            st.success("Kayıt başarılı! 7 gün ücretsiz kullanım başladı.")

# ===== SESSION =====
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    if menu == "Giriş Yap":
        login()
    else:
        register()
    st.stop()

# ===== USER =====
user = st.session_state["user"]
st.sidebar.write(f"👤 {user}")
st.sidebar.write(f"🏢 {users[user]['company']}")

if st.sidebar.button("Çıkış Yap"):
    st.session_state["logged_in"] = False
    st.rerun()

# ===== TRIAL SYSTEM =====
if users[user]["role"] != "admin":

    trial_start = datetime.strptime(users[user]["trial_start"], "%Y-%m-%d")
    today = datetime.now()

    days_passed = (today - trial_start).days
    remaining_days = 7 - days_passed

    if remaining_days <= 0 and users[user]["subscription"] != "active":
        st.error("❌ Deneme süreniz doldu. Lütfen ödeme yapınız.")
        st.stop()
    else:
        st.info(f"⏳ Deneme süresi: {remaining_days} gün kaldı")

        if remaining_days <= 2:
            st.warning("⚠️ Deneme süreniz bitmek üzere!")

# ===== ANA SİSTEM =====
st.title("📦 AI Satınalma Asistanı")

file = st.file_uploader("Excel yükle", type=["xlsx"])

if file:
    df = pd.read_excel(file)

    required_columns = [
        "Stok Kodu", "Ürün Adı", "Mevcut Stok",
        "Aylık Tüketim", "Tedarik Süresi",
        "Birim Fiyat", "Tedarikçi"
    ]

    if not all(col in df.columns for col in required_columns):
        st.error("❌ Excel formatı yanlış! Şablonu kullanın.")
    else:
        results = []

        for _, row in df.iterrows():
            alinacak = max(
                (row["Aylık Tüketim"]/30 * row["Tedarik Süresi"] + row["Aylık Tüketim"]*0.3)
                - row["Mevcut Stok"], 0
            )

            results.append({
                "Stok Kodu": row["Stok Kodu"],
                "Ürün": row["Ürün Adı"],
                "Alınacak Miktar": round(alinacak),
                "Tedarikçi": row["Tedarikçi"],
                "Maliyet (TL)": round(alinacak * row["Birim Fiyat"], 2)
            })

        result_df = pd.DataFrame(results)

        st.success("✅ Satın alma önerisi hazır")
        st.dataframe(result_df, use_container_width=True)

        toplam = result_df["Maliyet (TL)"].sum()
        st.markdown(f"## 💰 Toplam Maliyet: {toplam:,.2f} TL")

# ===== ADMIN PANEL =====
if users[user]["role"] == "admin":
    st.sidebar.markdown("---")
    st.sidebar.subheader("⚙️ Admin Panel")

    target_user = st.sidebar.text_input("Aktif edilecek kullanıcı")

    if st.sidebar.button("Aktif Et"):
        if target_user in users:
            users[target_user]["subscription"] = "active"
            save_users(users)
            st.sidebar.success("Kullanıcı aktif edildi")
        else:
            st.sidebar.error("Kullanıcı bulunamadı")
if users[user]["role"] == "admin":
    st.sidebar.markdown("### 👥 Kullanıcılar")

    for u in users:
        st.sidebar.write(f"- {u} ({users[u]['subscription']})")