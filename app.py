import streamlit as st
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# Judul Aplikasi Web
st.title("Kalkulator Logika Fuzzy Mamdani")
st.subheader("Penentuan Kebutuhan Pakan Harian Sapi Potong")
st.write("Dibuat oleh: **Monika Sari** (Universitas Muhammadiyah Metro)")

st.markdown("---")

# Slider Input dari Pengguna
berat_badan_input = st.slider("Pilih Berat Badan Sapi (kg)", 100, 500, 200, 1)
umur_sapi_input = st.slider("Pilih Umur Sapi (bulan)", 6, 36, 12, 1)

if st.button("Hitung Kebutuhan Pakan"):
    # 1. Definisi Variabel dan Semesta Pembicaraan
    berat_badan = ctrl.Antecedent(np.arange(100, 501, 1), 'berat_badan')
    umur_sapi    = ctrl.Antecedent(np.arange(6, 37, 1), 'umur_sapi')
    pakan_harian = ctrl.Consequent(np.arange(3, 16, 1), 'pakan_harian')

    # 2. Fungsi Keanggotaan Segitiga
    berat_badan['ringan'] = fuzz.trimf(berat_badan.universe, [100, 100, 250])
    berat_badan['sedang'] = fuzz.trimf(berat_badan.universe, [150, 250, 350])
    berat_badan['berat']  = fuzz.trimf(berat_badan.universe, [250, 500, 500])

    umur_sapi['muda']   = fuzz.trimf(umur_sapi.universe, [6, 6, 18])
    umur_sapi['dewasa'] = fuzz.trimf(umur_sapi.universe, [12, 24, 36])
    umur_sapi['tua']    = fuzz.trimf(umur_sapi.universe, [24, 36, 36])

    pakan_harian['sedikit'] = fuzz.trimf(pakan_harian.universe, [3, 3, 7])
    pakan_harian['sedang']  = fuzz.trimf(pakan_harian.universe, [6, 9, 12])
    pakan_harian['banyak']  = fuzz.trimf(pakan_harian.universe, [10, 15, 15])

    # 3. Basis Aturan (9 Rule)
    rule1 = ctrl.Rule(berat_badan['ringan'] & umur_sapi['muda'], pakan_harian['sedikit'])
    rule2 = ctrl.Rule(berat_badan['ringan'] & umur_sapi['dewasa'], pakan_harian['sedikit'])
    rule3 = ctrl.Rule(berat_badan['ringan'] & umur_sapi['tua'], pakan_harian['sedikit'])
    rule4 = ctrl.Rule(berat_badan['sedang'] & umur_sapi['muda'], pakan_harian['sedang'])
    rule5 = ctrl.Rule(berat_badan['sedang'] & umur_sapi['dewasa'], pakan_harian['sedang'])
    rule6 = ctrl.Rule(berat_badan['sedang'] & umur_sapi['tua'], pakan_harian['sedikit'])
    rule7 = ctrl.Rule(berat_badan['berat'] & umur_sapi['muda'], pakan_harian['banyak'])
    rule8 = ctrl.Rule(berat_badan['berat'] & umur_sapi['dewasa'], pakan_harian['banyak'])
    rule9 = ctrl.Rule(berat_badan['berat'] & umur_sapi['tua'], pakan_harian['sedang'])

    pakan_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9])
    simulasi = ctrl.ControlSystemSimulation(pakan_ctrl)

    # Masukkan Input User
    simulasi.input['berat_badan'] = berat_badan_input
    simulasi.input['umur_sapi'] = umur_sapi_input

    # Jalankan Simulasi
    simulasi.compute()
    hasil = simulasi.output['pakan_harian']

    # Tampilkan Hasil di Web
    st.success(f"### Rekomendasi Kebutuhan Pakan: **{hasil:.2f} kg BK/hari**")
    
    # Hitung persentase terhadap bobot badan
    persen = (hasil / berat_badan_input) * 100
    st.info(f"Rasio pakan terhadap berat badan: **{persen:.2f}%**")
