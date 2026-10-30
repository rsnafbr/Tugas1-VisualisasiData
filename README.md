# Dashboard Analisis Ekonomi & Kemiskinan Jawa Barat
Aplikasi web visualisasi data interaktif yang dibangun untuk memenuhi Tugas Mandiri Terstruktur Mata Kuliah Visualisasi Data dan Informasi.

# Arsitektur Multi-DBMS
- DBMS 1 (Relational - Cloud): PostgreSQL (Supabase)
    Berfungsi menyimpan data master dan ekonomi utama (`tabel_umk`, `tabel_garis_kemiskinan`).
- DBMS 2 (Embedded - Lokal): SQLite (`data_analitik.db`)
    Berfungsi menyimpan data analitik/metrik kemiskinan (`tabel_jumlah_miskin`, `tabel_kedalaman_kemiskinan`).

# Alur Data Pipeline & Integrasi
1. Data mentah dari file CSV dibaca menggunakan pustaka Pandas.
2. Skrip migrasi (`seed_data.py`) memasukkan data mentah ke masing-masing DBMS secara otomatis menggunakan SQLAlchemy.
3. Di dalam aplikasi utama (`app.py`), data ditarik dari kedua DBMS secara bersamaan, kemudian digabungkan (data federation / joining) menggunakan fungsi `pd.merge()` berdasarkan kunci `nama_kabupaten_kota` dan `tahun`.

# Sumber Data Asli (Sitasi)
Open Data Jabar / Badan Pusat Statistik (BPS) Provinsi Jawa Barat.