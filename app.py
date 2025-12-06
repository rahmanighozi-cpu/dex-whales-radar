import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime
import pytz
import random

# --- Konfigurasi Global ---
WHALE_THRESHOLD = 150000  # $150,000 USD (Dinaikkan agar Leaderboard lebih eksklusif)
API_URL_BASE = "https://api.dexscreener.com/latest/dex/"
INDONESIA_TZ = pytz.timezone('Asia/Jakarta')
# Target Chain untuk Simulasi Global View (tanpa search bar)
TARGET_CHAINS = ["ethereum", "solana", "base", "arbitrum", "polygon"]

# Daftar Kategori Whale (Simulasi)
WHALE_CATEGORIES = [
    "🚨 Insider Trader",
    "✅ Smart Money Alpha",
    "🐳 Whale Biasa",
    "🤖 High-Frequency Bot",
    "💼 Early VC Fund"
]

# --- Fungsi Generasi Data Leaderboard Simulasi ---
def generate_whale_leaderboard():
    all_leaderboard_data = []

    for chain in TARGET_CHAINS:
        search_url = f"{API_URL_BASE}search?q={chain}"
        
        try:
            response = requests.get(search_url, timeout=8)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException:
            continue # Lanjut ke chain berikutnya jika ada error

        if not data or 'pairs' not in data or not data['pairs']:
            continue

        for pair in data['pairs'][:10]: # Ambil 10 pair teratas per chain
            h24_volume = pair.get('volume', {}).get('h24', 0)
            
            if h24_volume > WHALE_THRESHOLD:
                
                # --- SIMULASI METRIK TRADING ---
                wallet_address = "0x" + "".join(random.choices("0123456789abcdef", k=40))[:10] + "..."
                simulated_pnl = random.randint(100000, 1200000) # PnL lebih tinggi
                simulated_trades = random.randint(10, 35)
                simulated_winrate = round(random.uniform(0.40, 0.90), 2)
                category = random.choice(WHALE_CATEGORIES)
                
                all_leaderboard_data.append({
                    'Trader/Token': f"[{pair.get('baseToken', {}).get('symbol', 'N/A')}] Whale {wallet_address}",
                    'Kategori': category,
                    'PnL (Est.)': simulated_pnl,
                    'Trades': simulated_trades,
                    'Win Rate (%)': f"{simulated_winrate * 100:.1f}%",
                    'Jaringan': pair.get('chainId', 'N/A').upper()
                })
                
    df_leaderboard = pd.DataFrame(all_leaderboard_data)
    df_leaderboard = df_leaderboard.sort_values(by='PnL (Est.)', ascending=False).reset_index(drop=True)
    
    return df_leaderboard

# --- Tampilan Dashboard Streamlit ---

st.set_page_config(layout="wide", page_title="DEX Whales Radar Pro", page_icon="🏆")

# Terapkan Custom CSS (untuk Nansen Look)
def load_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        pass # Lanjutkan tanpa CSS jika file tidak ada

load_css("style.css") # Memuat Custom CSS

# --- Judul Utama ---
st.title("🏆 DEX Whales Radar: Global Accumulation Leaderboard")
st.markdown("Analisis Akumulasi Terbaru, Win Rate, dan Kategori Smart Money")
st.markdown("---")


# Containers
placeholder = st.empty()
whale_alert_container = st.container()

# Sidebar hanya untuk pengaturan refresh
st.sidebar.header("🔧 Pengaturan Global")
refresh_rate = st.sidebar.slider("Refresh Data (detik)", min_value=15, max_value=60, value=20, step=5)
st.sidebar.markdown("---")
st.sidebar.info("💡 Data diambil secara otomatis dari 5 jaringan utama (Global View).")

# --- Loop Utama ---
while True:
    df_leaderboard = generate_whale_leaderboard()
    
    current_time_wib = datetime.now(INDONESIA_TZ).strftime('%d %b %Y, %H:%M:%S WIB')

    with placeholder.container():
        
        st.markdown(f"**Data Global Diperbarui:** {current_time_wib}")
        st.subheader("Top Traders Terdeteksi")

        if not df_leaderboard.empty:
            
            # Tampilan Leaderboard (UI Mirip Nansen)
            st.dataframe(
                df_leaderboard,
                use_container_width=True,
                column_config={
                    "PnL (Est.)": st.column_config.NumberColumn(format="$%,.0f"),
                    "Kategori": st.column_config.TextColumn(help="Klasifikasi disimulasikan"),
                }
            )
            
            # Ringkasan di bawah
            top_whale = df_leaderboard.iloc[0]['Trader/Token']
            st.toast(f"🚨 Top Global Whale Terdeteksi: {top_whale}", icon='🏆')
            
        else:
            st.warning(f"Tidak ada akumulasi besar terdeteksi di 5 jaringan utama saat ini. (Threshold > ${WHALE_THRESHOLD:,})")

    # --- Bagian Live Alert (Dipertahankan di bawah) ---
    with whale_alert_container:
        if not df_leaderboard.empty:
            st.markdown("---")
            st.subheader("🚨 Live Accumulation Alerts")
            
            # Tampilkan 3 notifikasi akumulasi terbesar
            for index, row in df_leaderboard.head(3).iterrows():
                st.error(f"[{row['Waktu (WIB)']}] **{row['Kategori']}** mengakumulasi **{row['Trader/Token']}** dengan Estimasi PnL ${row['PnL (Est.)']:,.0f}.")
    
    # Tunggu sesuai refresh rate
    time.sleep(refresh_rate)
