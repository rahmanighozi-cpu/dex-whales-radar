import streamlit as st
import requests
import pandas as pd
import time

# --- Konfigurasi ---
WHALE_THRESHOLD = 10000  # $10,000 USD
API_URL_BASE = "https://api.dexscreener.com/latest/dex/"

st.set_page_config(layout="wide", page_title="DEX Whales Radar", page_icon="🐳")

st.title("🐳 DEX Whales Radar (Zero Cost)")
st.caption("Memantau Akumulasi Besar menggunakan data publik DEX Screener.")

# --- Fungsi Deteksi Whale ---
def fetch_and_detect_whales(chain_query):
    search_url = f"{API_URL_BASE}search?q={chain_query}"
    
    try:
        response = requests.get(search_url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        # Jika gagal fetch (koneksi/rate limit)
        return pd.DataFrame(), []

    whale_alerts = []
    whale_data = []

    if not data or 'pairs' not in data or not data['pairs']:
        return pd.DataFrame(), []

    # Ambil 20 pair trending teratas
    for pair in data['pairs'][:20]: 
        try:
            h24_volume = pair.get('volume', {}).get('h24', 0)
            
            # LOGIKA DETEKSI AKUMULASI BESAR Sederhana
            # Jika Volume 24H cukup besar DAN harga tersedia, asumsikan ada aktivitas whale
            if h24_volume > 100000 and pair.get('priceUsd') and pair.get('priceUsd') != '0':
                
                # Buat data untuk tampilan
                whale_data.append({
                    'Token': pair.get('baseToken', {}).get('symbol', 'N/A'),
                    'Pair': pair.get('pairAddress', 'N/A')[:6] + '...',
                    'Price (USD)': float(pair.get('priceUsd', 0)),
                    'Volume 24H (USD)': h24_volume,
                    'Whale Alert': '🚨 Whale Activity High',
                    'Aksi Terakhir': f"Volume 24H: ${h24_volume:,.0f}"
                })
                
                # Buat notifikasi Alert
                whale_alerts.append(f"🐳 **ALERT:** Akumulasi besar terdeteksi pada **${pair.get('baseToken', {}).get('symbol', 'N/A')}**! Volume 24H mencapai ${h24_volume:,.0f}.")
                
        except Exception:
            continue

    df = pd.DataFrame(whale_data)
    return df, whale_alerts


# --- Tampilan Dashboard Streamlit ---

# Sidebar Konfigurasi
st.sidebar.header("🔧 Konfigurasi")
chain_input = st.sidebar.text_input("Chain/Token Query (Contoh: solana, eth)", value="solana")
refresh_rate = st.sidebar.slider("Refresh Data (detik)", min_value=15, max_value=120, value=30, step=15)

# Container untuk Live Alert dan Dashboard Utama
alert_container = st.empty()
placeholder = st.empty()

# --- Loop Utama (Polling Data) ---
while True:
    df_whales, alerts = fetch_and_detect_whales(chain_input)
    
    with placeholder.container():
        st.subheader(f"Dashboard Akumulasi Besar (Query: {chain_input.upper()})")
        st.markdown(f"**Terakhir Diperbarui:** {time.strftime('%H:%M:%S')}")

        if not df_whales.empty:
            # Tampilan Utama (Data Frame)
            st.dataframe(
                df_whales,
                use_container_width=True,
                column_config={
                    "Price (USD)": st.column_config.NumberColumn(format="$%.4f"),
                    "Volume 24H (USD)": st.column_config.NumberColumn(format="$%,.0f"),
                }
            )
        else:
            st.info("Tidak ada data Whale yang terdeteksi atau API sedang sibuk.")

    # Tampilkan Live Alerts
    with alert_container.container():
        if alerts:
            st.markdown("---")
            st.subheader("🚨 Live Whale Alerts")
            for alert in alerts:
                st.success(alert) # Menggunakan success untuk tampilan notifikasi

    # Tunggu sesuai refresh rate
    time.sleep(refresh_rate)
