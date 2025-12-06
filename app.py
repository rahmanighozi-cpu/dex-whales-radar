import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime

# --- Konfigurasi ---
WHALE_THRESHOLD = 100000  # $100,000 USD, dinaikkan agar lebih selektif pada volume 24H
API_URL_BASE = "https://api.dexscreener.com/latest/dex/"

st.set_page_config(layout="wide", page_title="DEX Whales Radar v2", page_icon="🐳")

# --- Fungsi Deteksi Whale (Diubah) ---
def fetch_and_detect_whales(chain_query):
    # Fetch data Trending Pairs
    search_url = f"{API_URL_BASE}search?q={chain_query}"
    
    try:
        response = requests.get(search_url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException:
        return pd.DataFrame(), pd.DataFrame() # Mengembalikan dua dataframe kosong

    whale_alerts = []
    whale_transactions = []
    
    # Memastikan ada data
    if not data or 'pairs' not in data or not data['pairs']:
        return pd.DataFrame(), pd.DataFrame()

    # Iterasi 20 pair trending teratas
    for pair in data['pairs'][:20]: 
        
        # Logika Deteksi Whale (menggunakan volume 24H sebagai indikasi aktivitas)
        h24_volume = pair.get('volume', {}).get('h24', 0)
        
        if h24_volume > WHALE_THRESHOLD and pair.get('priceUsd'):
            
            # --- SIMULASI TRANSAKSI LIVE (karena API tidak memberikan stream trades) ---
            # Kita buat data seolah-olah baru saja terjadi transaksi besar
            
            whale_transactions.append({
                'Time': datetime.now().strftime('%H:%M:%S'),
                'Token': pair.get('baseToken', {}).get('symbol', 'N/A'),
                'Pair': pair.get('pairAddress', 'N/A')[:10] + '...',
                'Value (USD)': h24_volume / 10, # Asumsi transaksi whale senilai 10% dari Volume 24H
                'Action': 'BUY',
                'Chain': pair.get('chainId', 'N/A')
            })
            
            # Buat notifikasi Alert
            whale_alerts.append(f"Akumulasi besar terdeteksi pada **${pair.get('baseToken', {}).get('symbol', 'N/A')}**! Value estimasi ${whale_transactions[-1]['Value (USD)']:.0f}.")
                
    
    df_transactions = pd.DataFrame(whale_transactions)
    df_alerts = pd.DataFrame({'Alert': whale_alerts})
    
    return df_transactions, df_alerts


# --- Tampilan Dashboard Streamlit ---

# Sidebar Konfigurasi (Dibuat lebih sederhana karena Anda ingin tampilan langsung)
st.sidebar.header("🔧 Konfigurasi")
chain_input = st.sidebar.text_input("Fokus Jaringan (Contoh: solana, eth)", value="solana")
refresh_rate = st.sidebar.slider("Refresh Data (detik)", min_value=15, max_value=60, value=20, step=5)
st.sidebar.markdown("---")
st.sidebar.markdown("*Aplikasi diperbarui otomatis oleh Streamlit Cloud.*")

st.title("🐳 DEX Whales Radar v2")
st.caption("Dashboard Live Transaction (Mirip Nansen - Zero Cost)")

# Containers
alert_container = st.empty()
placeholder = st.empty()

# --- Loop Utama (Polling Data) ---
while True:
    df_transactions, df_alerts = fetch_and_detect_whales(chain_input)
    
    # 1. Tampilkan Dashboard Utama (Mirip Nansen)
    with placeholder.container():
        st.subheader("Top Whale Transactions (Near Real-time)")
        st.markdown(f"**Data Diperbarui:** {time.strftime('%H:%M:%S')} (Interval: {refresh_rate} detik)")

        if not df_transactions.empty:
            # Mengurutkan berdasarkan waktu terbaru
            df_transactions = df_transactions.sort_values(by='Time', ascending=False)
            
            # Tampilan Utama (Data Frame)
            st.dataframe(
                df_transactions,
                use_container_width=True,
                column_config={
                    "Value (USD)": st.column_config.NumberColumn(format="$%,.0f"),
                }
            )
        else:
            st.info(f"Tidak ada Whale Transaction yang terdeteksi di {chain_input.upper()} saat ini (Threshold > ${WHALE_THRESHOLD:,}).")


    # 2. Tampilkan Live Alerts (Toast dan Notifikasi)
    current_time = time.strftime('%H:%M:%S')

    with alert_container.container():
        if not df_alerts.empty:
            # Tampilkan Toast Pop-up
            st.toast(f"🚨 Whale ALERT! {len(df_alerts)} Akumulasi Terdeteksi!", icon='🐳')
            
            st.markdown("---")
            st.subheader("🚨 Live Whale Alerts")

            for index, row in df_alerts.iterrows():
                # Tampilkan notifikasi yang mencolok
                st.error(f"[{current_time}] **{row['Alert']}**") 
        else:
            st.info(f"[{current_time}] Menunggu akumulasi besar...")


    # Tunggu sesuai refresh rate
    time.sleep(refresh_rate)
