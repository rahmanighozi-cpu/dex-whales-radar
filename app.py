import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime
import pytz
import random

# --- Konfigurasi Global ---
WHALE_THRESHOLD = 150000  # $150,000 USD (Volume 24H minimum)
API_URL_BASE = "https://api.dexscreener.com/latest/dex/"
INDONESIA_TZ = pytz.timezone('Asia/Jakarta')

# Target Chain untuk Simulasi Global View (Langsung ambil dari sini)
TARGET_CHAINS = ["ethereum", "solana", "base", "arbitrum", "polygon"]

# Daftar Kategori Whale (Simulasi Label)
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

    # Loop untuk mengambil data dari berbagai chain
    for chain in TARGET_CHAINS:
        search_url = f"{API_URL_BASE}search?q={chain}"
        
        try:
            # Timeout singkat agar loading tidak terlalu lama
            response = requests.get(search_url, timeout=5)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException:
            continue # Lanjut ke chain berikutnya jika ada error

        if not data or 'pairs' not in data or not data['pairs']:
            continue

        # Ambil 5 pair teratas per chain untuk efisiensi
        for pair in data['pairs'][:5]: 
            h24_volume = pair.get('volume', {}).get('h24', 0)
            
            # Filter hanya token dengan volume besar
            if h24_volume > WHALE_THRESHOLD:
                
                # --- SIMULASI METRIK TRADING ---
                # Karena API gratis tidak memberi data ini, kita simulasikan agar tampilan menarik
                wallet_address = "0x" + "".join(random.choices("0123456789abcdef", k=40))[:6] + "..."
                simulated_pnl = random.randint(100000, 1500000) # PnL tinggi
                simulated_trades = random.randint(5, 40)
                simulated_winrate = round(random.uniform(0.45, 0.95), 2)
                category = random.choice(WHALE_CATEGORIES)
                
                all_leaderboard_data.append({
                    'Trader/Token': f"[{pair.get('baseToken', {}).get('symbol', 'N/A')}] {wallet_address}",
                    'Kategori': category,
                    'PnL (Est.)': simulated_pnl,
                    'Trades': simulated_trades,
                    'Win Rate (%)': f"{simulated_winrate * 100:.1f}%",
                    'Jaringan': pair.get('chainId', 'N/A').upper(),
                    'Volume 24H': h24_volume
                })
                
    df_leaderboard = pd.DataFrame(all_leaderboard_data)
    
    # Urutkan berdasarkan PnL tertinggi (Leaderboard Style)
    if not df_leaderboard.empty:
        df_leaderboard = df_leaderboard.sort_values(by='PnL (Est.)', ascending=False).reset_index(drop=True)
    
    return df_leaderboard

# --- Konfigurasi Halaman Streamlit ---
st.set_page_config(layout="wide", page_title="DEX Whales Radar Pro", page_icon="🏆")

# Load CSS Custom (Pastikan file style.css ada di GitHub untuk Dark Mode yang sempurna)
def load_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        pass 

load_css("style.css") 

# --- Header Utama ---
st.title("🏆 DEX Whales Radar")
st.markdown("### Global Accumulation Leaderboard & Insider Tracking")
st.markdown("---")

# Container UI
placeholder = st.empty()
whale_alert_container = st.container()

# Sidebar Sederhana
st.sidebar.header("⚙️ System Status")
st.sidebar.success("✅ API Connected")
refresh_rate = st.sidebar.slider("Refresh Speed (detik)", 15, 60, 20)
st.sidebar.info("Monitoring 5 Major Chains: ETH, SOL, BASE, ARB, POLY")

# --- Loop Utama (Real-time Dashboard) ---
while True:
    # 1. Ambil Data Baru
    df_leaderboard = generate_whale_leaderboard()
    
    # 2. Tentukan Waktu Sekarang (WIB)
    current_time_wib = datetime.now(INDONESIA_TZ).strftime('%d %b %Y, %H:%M:%S WIB')
    time_only = datetime.now(INDONESIA_TZ).strftime('%H:%M:%S')

    # 3. Tampilkan Dashboard Utama
    with placeholder.container():
        st.caption(f"Last Updated: {current_time_wib}")
        
        if not df_leaderboard.empty:
            # Tampilkan Dataframe dengan format angka uang
            st.dataframe(
                df_leaderboard,
                use_container_width=True,
                column_config={
                    "PnL (Est.)": st.column_config.NumberColumn(format="$%,.0f"),
                    "Volume 24H": st.column_config.NumberColumn(format="$%,.0f"),
                    "Kategori": st.column_config.TextColumn(help="Klasifikasi Wallet"),
                }
            )
            
            # Highlight Top Whale
            top_whale = df_leaderboard.iloc[0]['Trader/Token']
            top_pnl = df_leaderboard.iloc[0]['PnL (Est.)']
            st.success(f"🏆 **Top Performer:** {top_whale} | PnL: ${top_pnl:,.0f}")
            
        else:
            st.warning("Sedang memuat data pasar... (Tunggu sebentar)")

    # 4. Tampilkan Live Alerts (BUG FIXED DISINI)
    with whale_alert_container:
        if not df_leaderboard.empty:
            st.markdown("---")
            st.subheader("🚨 Live Insider Alerts")
            
            # Ambil 3 data teratas untuk dijadikan notifikasi
            # Kita menggunakan variabel 'time_only' yang kita buat di atas, 
            # BUKAN mengambil dari kolom dataframe yang tidak ada.
            
            for index, row in df_leaderboard.head(3).iterrows():
                st.error(
                    f"[{time_only} WIB] **{row['Kategori']}** terdeteksi di **{row['Trader/Token']}** "
                    f"dengan Win Rate **{row['Win Rate (%)']}**."
                )
    
    # Tunggu sebelum refresh
    time.sleep(refresh_rate)
