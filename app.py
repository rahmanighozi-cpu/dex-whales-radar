import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime
import pytz
import random

# --- Konfigurasi ---
WHALE_THRESHOLD = 100000  # $100,000 USD (Volume 24H sebagai proxy)
API_URL_BASE = "https://api.dexscreener.com/latest/dex/"
INDONESIA_TZ = pytz.timezone('Asia/Jakarta')

# Daftar Kategori Whale (Simulasi)
WHALE_CATEGORIES = [
    "🚨 Insider Trader (Simulasi)",
    "✅ Smart Money Alpha",
    "🐳 Whale Biasa",
    "🤖 High-Frequency Bot",
    "💼 Early VC Fund"
]

# --- Fungsi Generasi Data Leaderboard Simulasi ---
def generate_whale_leaderboard(chain_query):
    search_url = f"{API_URL_BASE}search?q={chain_query}"
    
    try:
        response = requests.get(search_url, timeout=10)
        data = response.json()
    except requests.exceptions.RequestException:
        return pd.DataFrame()

    leaderboard_data = []

    if not data or 'pairs' not in data or not data['pairs']:
        return pd.DataFrame()

    for pair in data['pairs'][:15]: # Fokus pada 15 token paling aktif
        h24_volume = pair.get('volume', {}).get('h24', 0)
        
        # Hanya masukkan pair dengan aktivitas tinggi ke Leaderboard
        if h24_volume > WHALE_THRESHOLD:
            
            # --- SIMULASI METRIK TRADING ---
            # Randomize untuk membuat Leaderboard terlihat dinamis
            
            wallet_address = "0x" + "".join(random.choices("0123456789abcdef", k=40))[:4] + "..."
            
            # PnL (Simulasi antara $50,000 hingga $800,000)
            simulated_pnl = random.randint(50000, 800000)
            
            # Trades (Simulasi antara 5 hingga 25)
            simulated_trades = random.randint(5, 25)
            
            # Win Rate (Simulasi antara 30% hingga 80%)
            simulated_winrate = round(random.uniform(0.30, 0.80), 2)
            
            # Kategori Whale (Simulasi)
            category = random.choice(WHALE_CATEGORIES)
            
            leaderboard_data.append({
                'Trader/Token': f"[{pair.get('baseToken', {}).get('symbol', 'N/A')}] Whale {wallet_address}",
                'Kategori': category,
                'PnL (Est.)': simulated_pnl,
                'Trades': simulated_trades,
                'Win Rate (%)': f"{simulated_winrate * 100:.1f}%",
            })
                
    df_leaderboard = pd.DataFrame(leaderboard_data)
    
    # Urutkan berdasarkan PnL tertinggi agar terlihat seperti Leaderboard
    df_leaderboard = df_leaderboard.sort_values(by='PnL (Est.)', ascending=False).reset_index(drop=True)
    
    return df_leaderboard

# --- Tampilan Dashboard Streamlit ---

st.set_page_config(layout="wide", page_title="DEX Whales Radar Pro", page_icon="🏆")

# Terapkan Custom CSS (pastikan file style.css ada!)
def load_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("File style.css tidak ditemukan. Tampilan UI mungkin tidak optimal.")

load_css("style.css") # Aktifkan Dark Mode

st.title("🏆 DEX Whales Radar: Top Accumulator Leaderboard")
st.markdown("### Analisis PnL, Win Rate, dan Kategori Smart Money")

# Containers
placeholder = st.empty()

# Sidebar Konfigurasi
st.sidebar.header("🔧 Pengaturan Data")
chain_input = st.sidebar.text_input("Fokus Jaringan (Contoh: eth, solana)", value="solana")
refresh_rate = st.sidebar.slider("Refresh Leaderboard (detik)", min_value=15, max_value=60, value=30, step=5)
st.sidebar.markdown("---")
st.sidebar.info("💡 Semua metrik (PnL, Win Rate, Kategori) adalah **simulasi** berbasis aktivitas token saat ini.")

# --- Loop Utama ---
while True:
    df_leaderboard = generate_whale_leaderboard(chain_input)
    
    current_time_wib = datetime.now(INDONESIA_TZ).strftime('%d %b %Y, %H:%M:%S WIB')

    with placeholder.container():
        
        st.markdown(f"**Terakhir Diperbarui:** {current_time_wib}")

        if not df_leaderboard.empty:
            
            # Tampilan Utama (Mirip Leaderboard)
            st.dataframe(
                df_leaderboard,
                use_container_width=True,
                column_config={
                    "PnL (Est.)": st.column_config.NumberColumn(format="$%,.0f"),
                }
            )
            
            # Ringkasan di bawah Leaderboard
            top_whale = df_leaderboard.iloc[0]['Trader/Token']
            st.success(f"**Top Whale Saat Ini:** {top_whale}. Estimasi PnL: ${df_leaderboard.iloc[0]['PnL (Est.)']:,.0f}")
            
        else:
            st.error(f"Data Whale Leaderboard tidak tersedia untuk {chain_input.upper()} saat ini.")
    
    # Tunggu sesuai refresh rate
    time.sleep(refresh_rate)
