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

# Slider Berat Badan (tanpa pecahan .00)
berat_badan = st.slider(
    "Pilih Berat Badan Sapi (kg)",
    min_value=100,
    max_value=500,
    value=174,
    step=1,
)

# Slider Umur Sapi (tanpa pecahan .00)
umur_sapi = st.slider(
    "Pilih Umur Sapi (bulan)", min_value=6, max_value=36, value=10, step=1
)


# --- FUNGSI KEANGGOTAAN (MEMBERSHIP FUNCTIONS) ---
def fuzz_berat_badan(bb):
    # Ringan: [100, 100, 250]
    if bb <= 100:
        mu_ringan = 1.0
    elif 100 < bb < 250:
        mu_ringan = (250 - bb) / (250 - 100)
    else:
        mu_ringan = 0.0

    # Sedang: [150, 300, 450]
    if 150 <= bb <= 300:
        mu_sedang = (bb - 150) / (300 - 150)
    elif 300 < bb < 450:
        mu_sedang = (450 - bb) / (450 - 300)
    else:
        mu_sedang = 0.0

    # Berat: [350, 500, 500]
    if bb <= 350:
        mu_berat = 0.0
    elif 350 < bb < 500:
        mu_berat = (bb - 350) / (500 - 350)
    else:
        mu_berat = 1.0

    return {"ringan": mu_ringan, "sedang": mu_sedang, "berat": mu_berat}


def fuzz_umur(um):
    # Muda: [6, 6, 18], Dewasa: [12, 24, 36], Tua: [24, 36, 36]
    if um <= 6:
        mu_muda = 1.0
    elif 6 < um < 18:
        mu_muda = (18 - um) / (18 - 6)
    else:
        mu_muda = 0.0

    if 12 <= um <= 24:
        mu_dewasa = (um - 12) / (24 - 12)
    elif 24 < um <= 36:
        mu_dewasa = (36 - um) / (36 - 24)
    else:
        mu_dewasa = 0.0

    if um <= 24:
        mu_tua = 0.0
    elif 24 < um < 36:
        mu_tua = (um - 24) / (36 - 24)
    else:
        mu_tua = 1.0

    return {"muda": mu_muda, "dewasa": mu_dewasa, "tua": mu_tua}


# --- EVALUASI STATUS FUZZY REAL-TIME ---
bb_fuzzy = fuzz_berat_badan(berat_badan)
umur_fuzzy = fuzz_umur(umur_sapi)

status_bb = max(bb_fuzzy, key=bb_fuzzy.get)
nilai_bb = bb_fuzzy[status_bb]

status_umur = max(umur_fuzzy, key=umur_fuzzy.get)
nilai_umur = umur_fuzzy[status_umur]

st.markdown(
    f"💡 **Status Fuzzy Saat Ini:** Berat Badan masuk kategori **{status_bb.upper()}** ($\mu = {nilai_bb:.2f}$) | Umur masuk kategori **{status_umur.upper()}** ($\mu = {nilai_umur:.2f}$)"
)

# --- PROSES INFERENSI & DEFUZZIFIKASI ---
if st.button("Hitung Kebutuhan Pakan", type="primary"):
    z_sedikit = 4.0
    z_sedang = 9.0
    z_banyak = 14.0

    r1 = min(bb_fuzzy["ringan"], umur_fuzzy["muda"])
    r2 = min(bb_fuzzy["ringan"], umur_fuzzy["dewasa"])
    r3 = min(bb_fuzzy["sedang"], umur_fuzzy["muda"])
    r4 = min(bb_fuzzy["sedang"], umur_fuzzy["dewasa"])
    r5 = min(bb_fuzzy["sedang"], umur_fuzzy["tua"])
    r6 = min(bb_fuzzy["berat"], umur_fuzzy["dewasa"])
    r7 = min(bb_fuzzy["berat"], umur_fuzzy["tua"])

    alpha_sedikit = max(r1, r2, r3, 0.1)
    alpha_sedang = max(r4, r5, 0.3)
    alpha_banyak = max(r6, r7, 0.2)

    hasil_pakan = (
        (alpha_sedikit * z_sedikit)
        + (alpha_sedang * z_sedang)
        + (alpha_banyak * z_banyak)
    ) / (alpha_sedikit + alpha_sedang + alpha_banyak)

    hasil_pakan = max(3.0, min(15.0, hasil_pakan))
    rasio = (hasil_pakan / berat_badan) * 100

    st.success(f"### Rekomendasi Kebutuhan Pakan: {hasil_pakan:.2f} kg BK/hari")
    st.info(f"Rasio pakan terhadap berat badan: **{rasio:.2f}%**")

    # --- VISUALISASI GRAFIK UNTUK JURNAL ---
    st.markdown("---")
    st.subheader("Visualisasi Grafik Kurva & Hasil Inferensi")

    fig, ax = plt.subplots(figsize=(8, 4))
    x = np.linspace(3, 15, 100)
    y_kurva = np.exp(-((x - hasil_pakan) ** 2) / 8)

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
