import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="AI Satınalma Asistanı", layout="wide")

# ===== USER LOAD =====
def load_users():
    with open("users.json", "r") as f:
        return json.load(f)

def save_users(users):
    with open("users.json", "w") as f:
        json.dump(users, f, indent=4)

users = load_users()

# ===== LOGIN =====
def login():
    st.title("🔐 Giriş Yap")

    username = st.text_input("Kullanıcı Adı")
    password = st.text_input("Şifre", type="password")

    if st.button("Giriş"):
        if username in users and users[username]["password"] == password:
            st.session_state["logged_in"] = True
            st.session_state["user"] = username
            st.session_state["role"] = users[username]["role"]
        else:
            st.error("Hatalı giriş")

# ===== SESSION =====
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    login()
    st.stop()

# ===== HEADER =====
st.sidebar.write(f"👤 {st.session_state['user']}")
st.sidebar.write(f"🔑 {st.session_state['role']}")

if st.sidebar.button("Çıkış Yap"):
    st.session_state["logged_in"] = False
    st.rerun()

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

# ===== ADMIN PANEL =====
if st.session_state["role"] == "admin":
    st.sidebar.markdown("---")
    st.sidebar.subheader("⚙️ Admin Panel")

    new_user = st.sidebar.text_input("Yeni kullanıcı")
    new_pass = st.sidebar.text_input("Şifre", type="password")

    if st.sidebar.button("Kullanıcı ekle"):
        if new_user and new_pass:
            users[new_user] = {"password": new_pass, "role": "user"}
            save_users(users)
            st.sidebar.success("Kullanıcı eklendi")
        else:
            st.sidebar.error("Boş bırakılamaz")