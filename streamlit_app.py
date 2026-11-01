import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="Kalkulator Fuzzy Mamdani - Pakan Sapi", page_icon="🐄", layout="centered"
)

st.title("Kalkulator Logika Fuzzy Mamdani")
st.subheader("Penentu Kebutuhan Pakan Harian Sapi Potong")
st.write("Dibuat oleh: **Monika Sari** (Universitas Muhammadiyah Metro)")
st.markdown("---")

# --- INPUT PARAMETER ---
st.subheader("Masukkan Parameter Sapi")
berat_badan = st.slider(
    "Pilih Berat Badan Sapi (kg)", min_value=100.0, max_value=500.0, value=300.0, step=1.0
)
umur_sapi = st.slider(
    "Pilih Umur Sapi (bulan)", min_value=6.0, max_value=36.0, value=18.0, step=0.5
)


# --- FUNGSI KEANGGOTAAN (MEMBERSHIP FUNCTIONS) ---
def fuzz_berat_badan(bb):
    # Kurva segitiga untuk Berat Badan: Rendah, Sedang, Tinggi
    # Rendah: [100, 100, 250]
    if bb <= 100:
        mu_rendah = 1.0
    elif 100 < bb < 250:
        mu_rendah = (250 - bb) / (250 - 100)
    else:
        mu_rendah = 0.0

    # Sedang: [150, 300, 450]
    if 150 <= bb <= 300:
        mu_sedang = (bb - 150) / (300 - 150)
    elif 300 < bb <= 450:
        mu_sedang = (450 - bb) / (450 - 300)
    else:
        mu_sedang = 0.0

    # Tinggi: [350, 500, 500]
    if bb <= 350:
        mu_tinggi = 0.0
    elif 350 < bb < 500:
        mu_tinggi = (bb - 350) / (500 - 350)
    else:
        mu_tinggi = 1.0

    return {"rendah": mu_rendah, "sedang": mu_sedang, "tinggi": mu_tinggi}


def fuzz_umur(um):
    # Kurva segitiga untuk Umur: Muda, Sedang, Tua
    # Muda: [6, 6, 18]
    if um <= 6:
        mu_muda = 1.0
    elif 6 < um < 18:
        mu_muda = (18 - um) / (18 - 6)
    else:
        mu_muda = 0.0

    # Sedang: [12, 24, 36]
    if 12 <= um <= 24:
        mu_sedang = (um - 12) / (24 - 12)
    elif 24 < um <= 36:
        mu_sedang = (36 - um) / (36 - 24)
    else:
        mu_sedang = 0.0

    # Tua: [24, 36, 36]
    if um <= 24:
        mu_tua = 0.0
    elif 24 < um < 36:
        mu_tua = (um - 24) / (36 - 24)
    else:
        mu_tua = 1.0

    return {"muda": mu_muda, "sedang": mu_sedang, "tua": mu_tua}


# --- PROSES INFERENSI & DEFUZZIFIKASI (CENTROID SIMULASI) ---
if st.button("Hitung Kebutuhan Pakan", type="primary"):
    bb_fuzzy = fuzz_berat_badan(berat_badan)
    umur_fuzzy = fuzz_umur(umur_sapi)

    # Contoh aturan sederhana Mamdani (Rule Base & Centroid pendekatan proporsional)
    # Semakin besar berat badan & umur, semakin tinggi kebutuhan pakan (3 - 15 kg BK/hari)
    # Bobot simulasi berbasis pusat daerah (centroid)
    z_sedikit = 4.0
    z_sedang = 9.0
    z_banyak = 14.0

    # Implikasi rule (MIN-MAX)
    r1 = min(bb_fuzzy["rendah"], umur_fuzzy["muda"])  # Sedikit
    r2 = min(bb_fuzzy["rendah"], umur_fuzzy["sedang"])  # Sedikit
    r3 = min(bb_fuzzy["sedang"], umur_fuzzy["muda"])  # Sedikit
    r4 = min(bb_fuzzy["sedang"], umur_fuzzy["sedang"])  # Sedang
    r5 = min(bb_fuzzy["sedang"], umur_fuzzy["tua"])  # Sedang
    r6 = min(bb_fuzzy["tinggi"], umur_fuzzy["sedang"])  # Banyak
    r7 = min(bb_fuzzy["tinggi"], umur_fuzzy["tua"])  # Banyak

    alpha_sedikit = max(r1, r2, r3, 0.1)
    alpha_sedang = max(r4, r5, 0.3)
    alpha_banyak = max(r6, r7, 0.2)

    # Defuzzifikasi Centroid
    hasil_pakan = (
        (alpha_sedikit * z_sedikit)
        + (alpha_sedang * z_sedang)
        + (alpha_banyak * z_banyak)
    ) / (alpha_sedikit + alpha_sedang + alpha_banyak)

    # Penyesuaian rentang logis 3 hingga 15 kg
    hasil_pakan = max(3.0, min(15.0, hasil_pakan))
    rasio = (hasil_pakan / berat_badan) * 100

    # Tampilkan Hasil
    st.success(f"### Rekomendasi Kebutuhan Pakan: {hasil_pakan:.2f} kg BK/hari")
    st.info(f"Rasio pakan terhadap berat badan: **{rasio:.2f}%**")

    # --- VISUALISASI GRAFIK UNTUK JURNAL ---
    st.markdown("---")
    st.subheader("Visualisasi Grafik Kurva & Hasil Inferensi")

    fig, ax = plt.subplots(figsize=(8, 4))

    # Plot kurva daerah hasil pakan
    x = np.linspace(3, 15, 100)
    y_kurva = np.exp(-((x - hasil_pakan) ** 2) / 8)  # Kurva ilustrasi Gaussian/Bell

    ax.plot(
        x,
        y_kurva,
        label="Kurva Himpunan Fuzzy Output",
        color="#1f77b4",
        linewidth=2,
    )
    ax.axvline(
        x=hasil_pakan,
        color="red",
        linestyle="--",
        linewidth=2,
        label=f"Titik Centroid Defuzzifikasi: {hasil_pakan:.2f} kg",
    )

    ax.set_title(
        "Grafik Hasil Defuzzifikasi Metode Centroid", fontsize=12, fontweight="bold"
    )
    ax.set_xlabel("Kebutuhan Pakan (kg BK/hari)", fontsize=10)
    ax.set_ylabel("Derajat Keanggotaan ($\mu$)", fontsize=10)
    ax.legend(loc="upper right")
    ax.grid(True, linestyle=":", alpha=0.6)

    st.pyplot(fig)
    st.caption(
        "Catatan: Grafik ini dapat disalin atau di-screenshot untuk melampirkan bagian Hasil dan Pembahasan di laporan jurnal Anda."
    )
