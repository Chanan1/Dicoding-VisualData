import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from folium.plugins import MarkerCluster
# Judul aplikasi
st.title("Analisis Data Penjualan E-commerce")

# Baca data dari file CSV
all_df = pd.read_csv("Dashboard/all_df.csv")
all_df['order_purchase_timestamp'] = pd.to_datetime(all_df['order_purchase_timestamp'])  # Ubah tipe data menjadi timestamp

# Sidebar untuk pilihan analisis
st.sidebar.title("Pilihan Analisis")
options = st.sidebar.selectbox("Pilih Analisis", [
    "Geoanalysis",
    "RFM Analysis",
])

# Fungsi untuk Geoanalysis

def geoanalysis(df):
    
     # --- Analisis Produk yang Paling Sering Dibeli ---
    st.subheader("Top 10 Produk yang Paling Sering Dibeli")
    
    # Hitung jumlah pembelian setiap produk
    product_counts = df['product_category_name'].value_counts().reset_index()
    product_counts.columns = ['product_category_name', 'purchase_count']
    
    # Ambil 10 produk teratas
    top_10_products = product_counts.head(10)

    # Buat palet warna dengan warna menyorot
    colors = ['dimgray' if (x != top_10_products['product_category_name'].iloc[0]) else 'crimson' for x in top_10_products['product_category_name']]

    # Buat visualisasi bar chart
    plt.figure(figsize=(12, 6))
    sns.barplot(x='purchase_count', y='product_category_name', data=top_10_products, palette=colors)
    plt.title('Top 10 Most Frequently Purchased Products', fontsize=16)
    plt.xlabel('Number of Purchases', fontsize=12)
    plt.ylabel('Product Category', fontsize=12)
    plt.tight_layout()

    # Tampilkan visualisasi produk di Streamlit
    st.pyplot(plt)

    # --- Analisis Jumlah Order Berdasarkan State ---
    st.subheader("Top 10 State Berdasarkan Jumlah Order")
    
    # Hitung jumlah order per state
    orders_by_state = df.groupby('customer_state')['order_id'].nunique().reset_index(name='Number of Orders')
    orders_by_state = orders_by_state.sort_values(by=['Number of Orders'], ascending=False)

    # Ambil 10 state teratas
    top_states_orders = orders_by_state.head(10)

    # Buat visualisasi bar plot dengan kustomisasi
    plt.figure(figsize=(12, 8))
    sns.set(style="whitegrid")
    barplot = sns.barplot(x='Number of Orders', y='customer_state', data=top_states_orders, palette='Blues_d')

    # Tambahkan label dan judul
    plt.title('Top 10 States by Number of Orders', fontsize=16)
    plt.xlabel('Number of Orders', fontsize=12)
    plt.ylabel('State', fontsize=12)
    plt.tight_layout()

    # Tampilkan visualisasi di Streamlit
    st.pyplot(plt)

    # Analisis Tambahan: Jumlah Order per City
    st.subheader("Jumlah Order Berdasarkan Kota")

    # Hitung jumlah order per kota
    orders_by_city = df.groupby('customer_city')['order_id'].nunique().reset_index(name='Number of Orders')
    top_10_cities = orders_by_city.sort_values(by='Number of Orders', ascending=False).head(10)

    # Visualisasi Jumlah Order Berdasarkan Kota
    plt.figure(figsize=(12, 6))
    sns.barplot(x='Number of Orders', y='customer_city', data=top_10_cities, palette='viridis')
    plt.title('Top 10 Cities by Number of Orders')
    plt.xlabel('Number of Orders')
    plt.ylabel('City')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # Tampilkan visualisasi
    st.pyplot(plt)
    
        # --- Geospatial Visualization ---
    st.subheader("Geospatial Visualization")

    # Dapatkan koordinat geografis kota-kota (sesuaikan dengan data latitude dan longitude jika ada)
    cities = df[['customer_city', 'customer_state']].drop_duplicates()

    # Buat peta Folium dengan tile layer yang lebih menarik
    m = folium.Map(location=[-23.55, -46.63], zoom_start=4, tiles="CartoDB positron")

    # Gunakan MarkerCluster untuk mengelompokkan marker
    marker_cluster = MarkerCluster().add_to(m)

    # Tambahkan marker untuk setiap kota dengan tooltip
    for _, row in cities.iterrows():
        folium.Marker(
            location=[-23.55, -46.63],  # Ganti dengan koordinat kota yang sesuai (latitude/longitude)
            tooltip=f"{row['customer_city']}, {row['customer_state']}",  # Tooltip saat mouse diarahkan
            icon=folium.Icon(color="blue", icon="info-sign")  # Ikon lebih menarik
        ).add_to(marker_cluster)

    # Tampilkan peta di Streamlit
    st.components.v1.html(m._repr_html_(), width=700, height=500)

# Fungsi untuk RFM Analysis
def rfm_analysis(df):
    # Hitung nilai RFM untuk setiap pelanggan
    rfm_df = df.groupby('customer_id').agg({
        'order_purchase_timestamp': lambda x: (df['order_purchase_timestamp'].max() - x.max()).days,  # Recency
        'order_id': 'nunique',  # Frequency
        'price': 'sum'  # Monetary
    })
    rfm_df.columns = ['Recency', 'Frequency', 'Monetary']

    # Tentukan skor RFM (dengan quintile)
    try:
        if len(rfm_df['Recency'].unique()) >= 5:  # Pastikan data cukup untuk kuintil
            rfm_df['R_score'] = pd.qcut(rfm_df['Recency'], 5, labels=[5, 4, 3, 2, 1], duplicates='drop')
        else:
            rfm_df['R_score'] = 3  # Nilai default jika data terlalu sedikit
    except ValueError as e:
        st.write(f"Error in Recency score calculation: {e}")
        rfm_df['R_score'] = 3  # Nilai default jika terjadi error

    try:
        if len(rfm_df['Frequency'].unique()) >= 5:  # Pastikan data cukup untuk kuintil
            rfm_df['F_score'] = pd.qcut(rfm_df['Frequency'], 5, labels=[1, 2, 3, 4, 5], duplicates='drop')
        else:
            rfm_df['F_score'] = 3  # Nilai default jika data terlalu sedikit
    except ValueError as e:
        st.write(f"Error in Frequency score calculation: {e}")
        rfm_df['F_score'] = 3  # Nilai default jika terjadi error

    try:
        if len(rfm_df['Monetary'].unique()) >= 5:  # Pastikan data cukup untuk kuintil
            rfm_df['M_score'] = pd.qcut(rfm_df['Monetary'], 5, labels=[1, 2, 3, 4, 5], duplicates='drop')
        else:
            rfm_df['M_score'] = 3  # Nilai default jika data terlalu sedikit
    except ValueError as e:
        st.write(f"Error in Monetary score calculation: {e}")
        rfm_df['M_score'] = 3  # Nilai default jika terjadi error

    # Gabungkan skor RFM menjadi satu kolom
    if 'F_score' in rfm_df.columns:
        rfm_df['RFM_score'] = rfm_df['R_score'].astype(str) + rfm_df['F_score'].astype(str) + rfm_df['M_score'].astype(str)

    # Tampilkan tabel RFM
    st.write(rfm_df)

# Tampilkan hasil analisis berdasarkan pilihan
if options == "Geoanalysis":
    geoanalysis(all_df)
elif options == "RFM Analysis":
    rfm_analysis(all_df)
