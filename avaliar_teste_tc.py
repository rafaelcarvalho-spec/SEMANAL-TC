import numpy as np
import pydicom as dicom
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import cv2
import os

# ---------------- Funções ----------------
def circular_mask(h, w, center=None, radius=None):
    if center is None:
        center = (w // 2, h // 2)
    if radius is None:
        radius = min(center[0], center[1], w - center[0], h - center[1])
    Y, X = np.ogrid[:h, :w]
    return (X - center[0])**2 + (Y - center[1])**2 <= radius**2

def plot_img(img, name, rois=None, radius=25, phantom_circle=None):
    """Plota imagem em HU (sem normalização)."""
    fig, ax = plt.subplots()
    ax.imshow(img, cmap='gray')
    if phantom_circle is not None:
        x, y, r = phantom_circle
        circ = plt.Circle((x, y), r, color='blue', fill=False, linestyle='--', linewidth=1.5)
        ax.add_artist(circ)
    if rois:
        for c in rois:
            ax.add_artist(plt.Circle(c, radius, color='red', fill=False, linewidth=1.5))
    ax.axis('off')
    ax.set_title(name, fontsize=10)
    return fig

def crop_rois(img, centers, size=50):
    rois = []
    r = size // 2
    for x, y in centers:
        x0, y0 = max(x - r, 0), max(y - r, 0)
        roi = img[y0:y0 + size, x0:x0 + size].copy()
        h_roi, w_roi = roi.shape
        mask = circular_mask(h_roi, w_roi, radius=min(r, h_roi // 2, w_roi // 2))
        rois.append(roi[mask].flatten())
    return rois

def detectar_centro_phantom(img):
    """Detecta o centro do phantom circular usando transformada de Hough."""
    img8 = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    blur = cv2.medianBlur(img8, 5)
    circles = cv2.HoughCircles(
        blur,
        cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=100,
        param1=50,
        param2=30,
        minRadius=int(min(img.shape) / 6),
        maxRadius=int(min(img.shape) / 2)
    )
    if circles is not None:
        circles = np.uint16(np.around(circles))
        x, y, r = circles[0][0]
        return (x, y, r)
    else:
        h, w = img.shape
        return (w // 2, h // 2, min(h, w) // 3)

def extrair_info_dicom(ds):
    """Extrai informações principais do cabeçalho DICOM."""
    def get(tag):
        return getattr(ds, tag, "N/A")
    info = {
        "Paciente": str(get("PatientName")),
        "ID do Paciente": str(get("PatientID")),
        "Modalidade": str(get("Modality")),
        "Data do Estudo": str(get("StudyDate")),
        "Descrição da Série": str(get("SeriesDescription")),
        "kVp": str(get("KVP")),
        "mAs": str(get("Exposure")),
        "Slice Thickness (mm)": str(get("SliceThickness")),
        "Pixel Spacing (mm)": str(get("PixelSpacing")),
        "Dimensões (px)": f"{get('Rows')} x {get('Columns')}",
        "Fabricante": str(get("Manufacturer")),
        "Modelo do Equipamento": str(get("ManufacturerModelName")),
    }
    return pd.DataFrame(info.items(), columns=["Campo DICOM", "Valor"])

# ---------------- App Streamlit ----------------
def app():
    st.title("Teste Semanal de TC — Parâmetros segundo IN 93/2021 (ANVISA)")
    st.write("Carregue imagens DICOM para visualizar parâmetros e metadados.")

    uploads = st.file_uploader("Escolha imagens DICOM", accept_multiple_files=True)
    if not uploads:
        st.warning("Nenhuma imagem selecionada!")
        return

    imagens_dict = {}
    metadados_dict = {}

    for upload in uploads:
        try:
            ds = dicom.dcmread(upload, force=True)
            img = ds.pixel_array.astype(np.float32)

            # --- Conversão para HU ---
            if hasattr(ds, "RescaleSlope") and hasattr(ds, "RescaleIntercept"):
                img = img * float(ds.RescaleSlope) + float(ds.RescaleIntercept)

            imagens_dict[upload.name] = img
            metadados_dict[upload.name] = extrair_info_dicom(ds)

        except Exception as e:
            st.error(f"Erro ao ler {upload.name}: {e}")
            continue

    if not imagens_dict:
        st.warning("Nenhuma imagem válida foi carregada.")
        return

    nomes = list(imagens_dict.keys())
    if "img_index" not in st.session_state:
        st.session_state.img_index = 0

    col1, col2, col3 = st.columns([1, 6, 1])
    with col1:
        if st.button("⬅️"):
            st.session_state.img_index = max(0, st.session_state.img_index - 1)
    with col3:
        if st.button("➡️"):
            st.session_state.img_index = min(len(nomes) - 1, st.session_state.img_index + 1)

    nome_escolhido = nomes[st.session_state.img_index]
    img = imagens_dict[nome_escolhido]
    st.info(f"Imagem selecionada: {nome_escolhido}")

    # ---------- Exibe METADADOS DICOM ----------
    st.subheader("📋 Informações DICOM")
    st.dataframe(metadados_dict[nome_escolhido])

    # ---------- Localiza o centro do phantom ----------
    x_c, y_c, r_c = detectar_centro_phantom(img)

    # ---------- Ajuste manual ----------
    st.subheader("Ajuste opcional do raio externo (phantom)")
    fator_raio = st.slider(" ", 0.5, 1.5, 1.0, 0.01, label_visibility="collapsed")
    r_c_ajustado = int(r_c * fator_raio)

    # ---------- ROIs ----------
    desloc = int(r_c_ajustado * 0.75)
    radius_roi = int(25 * fator_raio)

    centers = [
        (x_c, y_c),            # Centro
        (x_c + desloc, y_c),   # 3h
        (x_c, y_c + desloc),   # 6h
        (x_c - desloc, y_c),   # 9h
        (x_c, y_c - desloc)    # 12h
    ]

    rois = crop_rois(img, centers, size=int(radius_roi * 2))

    # --- Exatidão individual ---
    nomes_rois = ["Centro", "3h", "6h", "9h", "12h"]
    ct_medios = [np.mean(r) for r in rois]  # média dos pixels (HU) de cada ROI
    limite_exatidao = 5
    exatidao_ok = all(abs(ct) <= limite_exatidao for ct in ct_medios)  # se todas estiverem dentro de ±5 HU

    # ✅ Uniformidade (única, comparando periferias ao centro)
    ct_central = ct_medios[0]
    delta_ct_perifericos = [ct_medios[i] - ct_central for i in range(1, 5)]
    uniformidade = max(abs(np.array(delta_ct_perifericos)))
    limite_uniformidade = 5
    uniformidade_ok = uniformidade <= limite_uniformidade

    # --- Ruído ---
    sigma_roi = np.std(rois[0])
    ruido_percent = (sigma_roi / 1000) * 100
    limite_ruido = 15
    ruido_ok = ruido_percent <= limite_ruido

    # ---------- Exibição ----------
    fig_img = plot_img(
        img,
        nome_escolhido,
        rois=centers,
        radius=radius_roi,
        phantom_circle=(x_c, y_c, r_c_ajustado)
    )
    fig_img.set_size_inches(5, 5)
    st.pyplot(fig_img)

    # ---------- Tabelas ----------
    resultados_exatidao = pd.DataFrame({
        "ROI": nomes_rois,
        "CT médio (HU)": ct_medios,
        "Limite (±HU)": [limite_exatidao] * 5,
        "Status": ["OK" if abs(ct) <= limite_exatidao else "Fora" for ct in ct_medios]
    })

    resultados_geral = pd.DataFrame({
        "Métrica": ["Uniformidade (HU)", "Ruído (%)"],
        "Valor": [uniformidade, ruido_percent],
        "Limite": [f"≤{limite_uniformidade} HU", f"≤{limite_ruido}%"],
        "Status": ["OK" if uniformidade_ok else "Fora",
                   "OK" if ruido_ok else "Fora"]
    })

    def highlight_status(row):
        color_map = {'OK': '#90ee90', 'Fora': '#f08080'}
        return [f'background-color: {color_map.get(row["Status"], "")}'] * len(row)

    st.subheader("Resultados de Exatidão (média dos pixels de cada ROI)")
    st.dataframe(resultados_exatidao.style.format({'CT médio (HU)': '{:.2f}'}).apply(highlight_status, axis=1))

    st.subheader("Resultados Gerais segundo a IN 93/2021 (ANVISA)")
    styled = resultados_geral.style.format({'Valor': '{:.2f}'}).apply(highlight_status, axis=1)
    st.dataframe(styled)

    if all([exatidao_ok, uniformidade_ok, ruido_ok]):
        st.success("✅ Equipamento conforme os limites da IN 93/2021.")
    else:
        st.error("❌ Equipamento fora de conformidade — verificar calibração e parâmetros de aquisição.")

if __name__ == "__main__":
    app()
