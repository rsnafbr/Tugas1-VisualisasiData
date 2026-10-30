import pandas as pd
from sqlalchemy import create_engine

# --- 1. PENGATURAN KONEKSI DATABASE ---
POSTGRES_URL = "postgresql://postgres.xzsnkcrytszyfrzojzfs:rsnafbr0702@aws-0-eu-west-1.pooler.supabase.com:6543/postgres"

# SQLite otomatis membuat file lokal bernama 'data_analitik.db' di dalam folder proyek
SQLITE_URL = "sqlite:///data_analitik.db"

# Membuat 'mesin' penghubung
engine_postgres = create_engine(POSTGRES_URL)
engine_sqlite = create_engine(SQLITE_URL)

# --- 2. MEMBACA DATA CSV KE PANDAS DATAFRAME ---
# Dataset untuk PostgreSQL (Data Ekonomi/Master)
df_umk = pd.read_csv("od_19868_daftar_upah_minimum_kabupatenkota_di_drh_prov_jaba_v2.csv")
df_garis_kemiskinan = pd.read_csv("od_20003_garis_kemiskinan_berdasarkan_kabupatenkota_v2.csv")

# Dataset untuk SQLite (Data Log/Analitik Kemiskinan)
df_jml_miskin = pd.read_csv("od_16425_jumlah_penduduk_miskin_berdasarkan_kabupatenkota_v1.csv")
df_kedalaman_miskin = pd.read_csv("od_18026_indeks_kedalaman_kemiskinan_berdasarkan_kabupatenkota.csv")

# --- 3. MEMASUKKAN DATA KE POSTGRESQL (DBMS 1) ---
# Format: to_sql(nama_tabel, koneksi_engine, opsi_jika_tabel_sudah_ada, hilangkan_index_pandas)
df_umk.to_sql("tabel_umk", engine_postgres, if_exists="replace", index=False)
df_garis_kemiskinan.to_sql("tabel_garis_kemiskinan", engine_postgres, if_exists="replace", index=False)
print("Berhasil! Data master ekonomi sudah masuk ke PostgreSQL Supabase.")

# --- 4. MEMASUKKAN DATA KE SQLITE (DBMS 2) ---
df_jml_miskin.to_sql("tabel_jumlah_miskin", engine_sqlite, if_exists="replace", index=False)
df_kedalaman_miskin.to_sql("tabel_kedalaman_kemiskinan", engine_sqlite, if_exists="replace", index=False)
print("Berhasil! Data analitik kemiskinan sudah masuk ke file lokal SQLite.")