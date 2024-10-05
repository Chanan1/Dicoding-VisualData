import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import folium

# Judul aplikasi
st.title("Analisis Data Penjualan E-commerce")

# Baca data dari file CSV
all_df = pd.read_csv("all_df.csv")
all_df['order_purchase_timestamp'] = pd.to_datetime(all_df['order_purchase_timestamp'])  # Ubah tipe data menjadi timestamp

# Sidebar untuk pilihan analisis
st.sidebar.title("Pilihan Analisis")
options = st.sidebar.selectbox("Pilih Analisis", [
    "RFM Analysis",
    "Geoanalysis",
    "Time Series Analysis",
])

def rfm_analysis(df):
    # Hitung nilai RFM untuk setiap pelanggan
    rfm_df = df.groupby('customer_id').agg({
        'order_purchase_timestamp': lambda x: (df['order_purchase_timestamp'].max() - x.max()).days,  # Recency
        'order_id': 'nunique',  # Frequency
        'price': 'sum'  # Monetary
    })
    rfm_df.columns = ['Recency', 'Frequency', 'Monetary']

    # Tentukan skor RFM (dengan quintile)
    # Recency
    try:
        rfm_df['R_score'] = pd.qcut(rfm_df['Recency'], 5, labels=[5, 4, 3, 2, 1], duplicates='drop')
    except ValueError as e:
        st.write(f"Error in Recency score calculation: {e}")

    # Frequency - Cek jika Frequency seragam
    if rfm_df['Frequency'].nunique() > 1:
        try:
            rfm_df['F_score'] = pd.qcut(rfm_df['Frequency'], 5, labels=[1, 2, 3, 4, 5], duplicates='drop')
        except ValueError as e:
            st.write(f"Error in Frequency score calculation: {e}")
    else:
        # Jika semua Frequency sama, beri nilai default
        rfm_df['F_score'] = 3  # Contoh default score

    # Monetary
    try:
        rfm_df['M_score'] = pd.qcut(rfm_df['Monetary'], 5, labels=[1, 2, 3, 4, 5], duplicates='drop')
    except ValueError as e:
        st.write(f"Error in Monetary score calculation: {e}")

    # Gabungkan skor RFM menjadi satu kolom
    if 'F_score' in rfm_df.columns:
        rfm_df['RFM_score'] = rfm_df['R_score'].astype(str) + rfm_df['F_score'].astype(str) + rfm_df['M_score'].astype(str)

    # Tampilkan tabel RFM
    st.write(rfm_df)



# Fungsi untuk Geoanalysis
# Fungsi untuk Geoanalysis
def geoanalysis(df):
    # Hapus data duplikat untuk pelanggan
    customers_df = df[['customer_id', 'customer_state']].drop_duplicates()

    # Visualisasi distribusi pelanggan berdasarkan state
    plt.figure(figsize=(12, 6))
    sns.countplot(x='customer_state', data=customers_df, order=customers_df['customer_state'].value_counts().index)
    plt.title('Distribution of Customers by State')
    plt.xlabel('State')
    plt.ylabel('Number of Customers')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # Tampilkan visualisasi distribusi pelanggan
    st.pyplot(plt)
    plt.clf()  # Bersihkan plot setelah menampilkan

       # --- Geospatial Visualization ---
    st.subheader("Geospatial Visualization")

    # Dapatkan koordinat geografis kota-kota
    # Anda mungkin perlu mengganti 'customer_city' dengan kolom yang berisi nama kota di data Anda
    cities = df[['customer_city', 'customer_state']].drop_duplicates()  

    # Buat peta Folium
    m = folium.Map(location=[-23.55, -46.63], zoom_start=4)  # Koordinat awal dan zoom level

    # Tambahkan marker untuk setiap kota
    for index, row in cities.iterrows():
        folium.Marker(
            location=[-23.55, -46.63], # Ganti dengan koordinat kota
            popup=f"Kota: {row['customer_city']}, State: {row['customer_state']}",  # Informasi yang ditampilkan saat marker diklik
        ).add_to(m)

    # Tampilkan peta di Streamlit
    st.components.v1.html(m._repr_html_(), width=700, height=500)

# Fungsi untuk Time Series Analysis
def time_series_analysis(df):
    # Agregasi data penjualan per hari
    daily_sales = df.groupby('order_purchase_timestamp')['price'].sum().reset_index()
    daily_sales['order_purchase_timestamp'] = pd.to_datetime(daily_sales['order_purchase_timestamp'])
    daily_sales = daily_sales.set_index('order_purchase_timestamp')

    # Visualisasi tren penjualan
    plt.figure(figsize=(12, 6))
    daily_sales['price'].plot()
    plt.title('Daily Sales Trend')
    plt.xlabel('Date')
    plt.ylabel('Total Sales')
    plt.tight_layout()

    # Tampilkan visualisasi tren penjualan
    st.pyplot(plt)

# Tampilkan hasil analisis berdasarkan pilihan
if options == "RFM Analysis":
    rfm_analysis(all_df)
elif options == "Geoanalysis":
    geoanalysis(all_df)
elif options == "Time Series Analysis":
    time_series_analysis(all_df)
