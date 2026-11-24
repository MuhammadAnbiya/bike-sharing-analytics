# Proyek Analisis Data: Bike Sharing Dataset

Dashboard interaktif berbasis Streamlit untuk menganalisis pola penyewaan sepeda pada periode 2011–2012 berdasarkan tren bulanan, musim, kondisi cuaca, tipe hari, serta segmen pengguna (`casual` dan `registered`).

## Tautan Dashboard & Repositori
- **Streamlit Cloud:** https://bike-sharing-analytics-anbi.streamlit.app/
- **GitHub Repository:** https://github.com/MuhammadAnbiya/bike-sharing-analytics

## Struktur Direktori
- `dashboard/` : Berisi skrip utama aplikasi Streamlit (`dashboard.py`) serta dataset hasil pembersihan (`day_clean.csv`, `hour_clean.csv`).
- `data/` : Berisi dataset mentah (`day.csv`, `hour.csv`).
- `notebook.ipynb` : Jupyter Notebook yang memuat seluruh proses analisis data (Data Wrangling, Exploratory Data Analysis, Visualization, Analisis Lanjutan, dan Conclusion).
- `requirements.txt` : Daftar pustaka Python yang dibutuhkan untuk menjalankan proyek.
- `url.txt` : Tautan publik aplikasi dashboard pada Streamlit Community Cloud.

## Setup Environment - Anaconda
```bash
conda create --name main-ds python=3.9
conda activate main-ds
pip install -r requirements.txt
```

## Setup Environment - Shell/Terminal
1. Buka terminal dan arahkan ke direktori utama proyek (folder yang memuat `requirements.txt`), lalu buat dan aktifkan *virtual environment*:
```bash
python -m venv venv

# Aktivasi di Windows (CMD/PowerShell):
venv\Scripts\activate

# Aktivasi di macOS/Linux:
source venv/bin/activate
```

2. Instal seluruh pustaka Python dari `requirements.txt`:
```bash
pip install -r requirements.txt
```

## Run Streamlit App
Setelah *environment* aktif dan seluruh pustaka terinstal, jalankan dashboard secara lokal dengan perintah berikut:
```bash
streamlit run dashboard/dashboard.py
```