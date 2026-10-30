import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Dashboard Ekonomi & Kemiskinan Jabar",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS CUSTOM UNTUK TAMPILAN HEADER ---
st.markdown("""
    <style>
    .main-header { font-size: 2.2rem; font-weight: bold; color: #1a1a1a; margin-bottom: 0.2rem; text-align: center; }
    .sub-header { font-size: 1.1rem; color: #666; text-align: center; margin-bottom: 2rem; }
    [data-testid="stSidebar"] { background-color: #f8f9fa; }
    </style>
""", unsafe_allow_html=True)

# Menampilkan Header
st.markdown('<div class="main-header"> Dashboard Ekonomi & Kemiskinan Jawa Barat</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Integrasi Data: PostgreSQL (Cloud) & SQLite (Lokal)</div>', unsafe_allow_html=True)

# --- KONEKSI DATABASE & PENGAMBILAN DATA ---
# Memanggil URL secara aman dari sistem rahasia Streamlit Cloud
POSTGRES_URL = st.secrets["POSTGRES_URL"]
SQLITE_URL = "sqlite:///data_analitik.db"

@st.cache_data(ttl=600)
def load_and_merge_data():
    engine_pg = create_engine(POSTGRES_URL)
    engine_sqlite = create_engine(SQLITE_URL)
    
    df_umk = pd.read_sql("SELECT * FROM tabel_umk", engine_pg)
    df_garis = pd.read_sql("SELECT * FROM tabel_garis_kemiskinan", engine_pg)
    df_jml = pd.read_sql("SELECT * FROM tabel_jumlah_miskin", engine_sqlite)
    df_kedalaman = pd.read_sql("SELECT * FROM tabel_kedalaman_kemiskinan", engine_sqlite)
    
    df_merged = pd.merge(df_umk, df_garis, on=['nama_kabupaten_kota', 'tahun'], suffixes=('', '_drop'))
    df_merged = pd.merge(df_merged, df_jml, on=['nama_kabupaten_kota', 'tahun'], suffixes=('', '_drop'))
    df_merged = pd.merge(df_merged, df_kedalaman, on=['nama_kabupaten_kota', 'tahun'], suffixes=('', '_drop'))
    
    df_merged = df_merged.loc[:, ~df_merged.columns.str.endswith('_drop')]
    df_merged['tahun'] = df_merged['tahun'].astype(int) 
    
    # --- PERBAIKAN FORMAT NAMA WILAYAH ---
    # Mengubah "KABUPATEN BOGOR" menjadi "Kabupaten Bogor", lalu menyingkatnya jadi "Kab. Bogor"
    df_merged['nama_kabupaten_kota'] = df_merged['nama_kabupaten_kota'].str.title()
    df_merged['nama_kabupaten_kota'] = df_merged['nama_kabupaten_kota'].str.replace('Kabupaten', 'Kab.')
    
    return df_merged

try:
    df = load_and_merge_data()
except Exception as e:
    st.error(f"❌ Gagal mengambil data. Pastikan URL dan Password benar: {e}")
    st.stop()

# --- SIDEBAR FILTER ---
with st.sidebar:
    st.markdown("### Kontrol Visualisasi")
    
    tahun_tersedia = sorted(df['tahun'].unique(), reverse=True)
    tahun_pilihan = st.selectbox("Pilih Tahun:", tahun_tersedia)
    
    kabupaten_list = sorted(df['nama_kabupaten_kota'].unique())
    kabupaten_pilihan = st.multiselect("Pilih Wilayah:", options=kabupaten_list, default=kabupaten_list[:8])

df_filtered = df[(df['tahun'] == tahun_pilihan) & (df['nama_kabupaten_kota'].isin(kabupaten_pilihan))].copy()

if df_filtered.empty:
    st.warning("⚠️ Silakan pilih minimal satu wilayah dari menu samping.")
else:
    # --- METRIK RINGKASAN HTML CARDS ---
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    
    avg_umk = df_filtered['besaran_upah_minimum'].mean()
    total_miskin = df_filtered['jumlah_penduduk_miskin'].sum()
    avg_garis = df_filtered['garis_kemiskinan'].mean()
    avg_kedalaman = df_filtered['indeks_kedalaman_kemiskinan'].mean()
    
    def create_card(title, value, border_color):
        return f"""
        <div style="background-color: #ffffff; padding: 20px; border-radius: 10px; 
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); border: 1px solid #e0e0e0; 
                    border-top: 5px solid {border_color}; text-align: center; height: 110px;">
            <p style="margin: 0; font-size: 1rem; color: #4B5563; font-weight: 600;">{title}</p>
            <p style="margin: 5px 0 0 0; font-size: 1.6rem; color: #1f2937; font-weight: bold;">{value}</p>
        </div>
        """

    with col_m1:
        st.markdown(create_card("Rata-rata UMK", f"Rp {avg_umk:,.0f}", "#8B5CF6"), unsafe_allow_html=True)
    with col_m2:
        st.markdown(create_card("Total Penduduk Miskin", f"{total_miskin:,.1f} Ribu", "#EF4444"), unsafe_allow_html=True)
    with col_m3:
        st.markdown(create_card("Garis Kemiskinan", f"Rp {avg_garis:,.0f}", "#10B981"), unsafe_allow_html=True)
    with col_m4:
        st.markdown(create_card("Indeks Kedalaman", f"{avg_kedalaman:.2f}", "#3B82F6"), unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True) 

    # --- KAMUS KOORDINAT JAWA BARAT ---
    koordinat_jabar = {
        'Kab. Bogor': [-6.5518, 106.6241], 'Kab. Sukabumi': [-7.0252, 106.5387],
        'Kab. Cianjur': [-7.3249, 107.1049], 'Kab. Bandung': [-7.1025, 107.4907],
        'Kab. Garut': [-7.4475, 107.6938], 'Kab. Tasikmalaya': [-7.3547, 108.0640],
        'Kab. Ciamis': [-7.2713, 108.3551], 'Kab. Kuningan': [-6.9756, 108.4839],
        'Kab. Cirebon': [-6.7645, 108.4776], 'Kab. Majalengka': [-6.8365, 108.2274],
        'Kab. Sumedang': [-6.8384, 107.9257], 'Kab. Indramayu': [-6.4011, 108.1345],
        'Kab. Subang': [-6.5413, 107.7618], 'Kab. Purwakarta': [-6.5779, 107.4477],
        'Kab. Karawang': [-6.2944, 107.3067], 'Kab. Bekasi': [-6.2307, 107.1751],
        'Kab. Bandung Barat': [-6.8407, 107.4571], 'Kab. Pangandaran': [-7.6896, 108.5140],
        'Kota Bogor': [-6.5971, 106.7972], 'Kota Sukabumi': [-6.9237, 106.9287],
        'Kota Bandung': [-6.9175, 107.6191], 'Kota Cirebon': [-6.7320, 108.5523],
        'Kota Bekasi': [-6.2383, 106.9756], 'Kota Depok': [-6.4025, 106.7942],
        'Kota Cimahi': [-6.8778, 107.5423], 'Kota Tasikmalaya': [-7.3274, 108.2232],
        'Kota Banjar': [-7.3746, 108.5332]
    }
    df_filtered['lat'] = df_filtered['nama_kabupaten_kota'].map(lambda x: koordinat_jabar.get(x, [0,0])[0])
    df_filtered['lon'] = df_filtered['nama_kabupaten_kota'].map(lambda x: koordinat_jabar.get(x, [0,0])[1])

    # --- VISUALISASI PETA ---
    st.markdown(f"### Peta Persebaran Kemiskinan di Jawa Barat ({tahun_pilihan})")
    fig_map = px.scatter_map(
        df_filtered,
        lat="lat",
        lon="lon",
        hover_name="nama_kabupaten_kota",
        hover_data={"lat": False, "lon": False, "jumlah_penduduk_miskin": True, "indeks_kedalaman_kemiskinan": True},
        size="jumlah_penduduk_miskin", 
        color="indeks_kedalaman_kemiskinan", 
        color_continuous_scale="Reds",
        size_max=30,
        zoom=6.5, 
        center={"lat": -6.9, "lon": 107.6}, 
        map_style="carto-positron",
        labels={
            "indeks_kedalaman_kemiskinan": "Indeks Kedalaman", 
            "jumlah_penduduk_miskin": "Penduduk Miskin (Ribu)"
        }
    )
    fig_map.update_layout(coloraxis_colorbar=dict(title="Indeks Kedalaman"), margin={"r":0,"t":10,"l":0,"b":0})
    st.plotly_chart(fig_map, use_container_width=True)
    
    st.markdown("<br><hr><br>", unsafe_allow_html=True)

    # --- VISUALISASI GRAFIK ---
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"#### Korelasi UMK vs Jumlah Kemiskinan ({tahun_pilihan})")
        fig_scatter = px.scatter(
            df_filtered,
            x="besaran_upah_minimum",
            y="jumlah_penduduk_miskin",
            color="nama_kabupaten_kota",
            size="garis_kemiskinan",
            hover_name="nama_kabupaten_kota",
            labels={
                "besaran_upah_minimum": "UMK (Rp)",
                "jumlah_penduduk_miskin": "Penduduk Miskin (Ribu)",
                "nama_kabupaten_kota": "Wilayah"
            },
            template="plotly_white",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_scatter.update_layout(showlegend=False, margin=dict(l=0, r=0, t=20, b=0))
        st.plotly_chart(fig_scatter, use_container_width=True)

    with col2:
        st.markdown(f"#### Indeks Kedalaman Kemiskinan ({tahun_pilihan})")
        fig_bar = px.bar(
            df_filtered.sort_values('indeks_kedalaman_kemiskinan', ascending=True),
            x="indeks_kedalaman_kemiskinan",
            y="nama_kabupaten_kota",
            color="indeks_kedalaman_kemiskinan",
            orientation='h',
            color_continuous_scale="Viridis",
            labels={
                "indeks_kedalaman_kemiskinan": "Skor Indeks",
                "nama_kabupaten_kota": "" 
            },
            template="plotly_white"
        )
        fig_bar.update_layout(coloraxis_showscale=False, margin=dict(l=0, r=0, t=20, b=0))
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- TABEL DATA ---
    st.markdown("### Tabel Rincian Data")
    df_display = df_filtered[['nama_kabupaten_kota', 'besaran_upah_minimum', 'garis_kemiskinan', 'jumlah_penduduk_miskin', 'indeks_kedalaman_kemiskinan']].copy()
    df_display.columns = ["Kabupaten / Kota", "UMK (Rupiah)", "Garis Kemiskinan", "Jumlah Penduduk Miskin (Ribu)", "Indeks Kedalaman"]
    
    st.dataframe(
        df_display.style.format({
            'UMK (Rupiah)': "Rp {:,.0f}",
            'Garis Kemiskinan': "Rp {:,.0f}",
            'Jumlah Penduduk Miskin (Ribu)': "{:,.1f}",
            'Indeks Kedalaman': "{:.2f}"
        }),
        use_container_width=True,
        hide_index=True
    )