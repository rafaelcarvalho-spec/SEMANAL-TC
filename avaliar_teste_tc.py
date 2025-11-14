import numpy as np
import pydicom as dicom
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import cv2
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from datetime import datetime
import tempfile  # Tempfile para gerar um diretório temporário compatível com qualquer sistema operacional

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
    
    # Adicionando números nas ROIs
    roi_labels = ['1', '2', '3', '4', '5']  # Números para cada ROI: Centro, 3h, 6h, 9h, 12h
    if rois:
        for i, c in enumerate(rois):
            ax.add_artist(plt.Circle(c, radius, color='red', fill=False, linewidth=1.5))
            ax.text(c[0], c[1], roi_labels[i], color='white', fontsize=12, ha='center', va='center')
    
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

# ---------------- App Streamlit ----------------
def app():
    st.title("Avaliação da Qualidade das Imagens")
    st.write("Carregue as imagens DICOM e use as setas para navegar entre elas e escolher a imagem central do objeto simulador. Depois, selecione o material em análise: Água ou Ar.")

    uploads = st.file_uploader("Escolha imagens DICOM", accept_multiple_files=True)
    if not uploads:
        st.warning("Nenhuma imagem selecionada!")
        return

    imagens_dict = {}

    for upload in uploads:
        try:
            ds = dicom.dcmread(upload, force=True)
            img = ds.pixel_array.astype(np.float32)

            # --- Conversão para HU ---
            if hasattr(ds, "RescaleSlope") and hasattr(ds, "RescaleIntercept"):
                img = img * float(ds.RescaleSlope) + float(ds.RescaleIntercept)

            imagens_dict[upload.name] = img

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

    # ---------- Localiza o centro do phantom ----------
    x_c, y_c, r_c = detectar_centro_phantom(img)

    # ---------- Ajuste manual ----------
    st.subheader("Ajuste opcional do raio externo (azul)")
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

    # --- Exatidão individual (média dos pixels de cada ROI) ---
    nomes_rois = ["1", "2", "3", "4", "5"]
    ct_medios = [np.mean(r) for r in rois]  # média dos pixels (HU) de cada ROI

    # --- Ruído individual (desvio padrão dividido por 1000, multiplicado por 100) ---
    desvios = [np.std(r) for r in rois]
    ruido_percent = [(d / 1000) * 100 for d in desvios]

    # --- Uniformidade (diferença do valor médio entre o centro e as periferias) ---
    ct_central = ct_medios[0]
    delta_ct_perifericos = [ct_medios[i] - ct_central for i in range(1, 5)]
    uniformidade = max(abs(np.array(delta_ct_perifericos)))

    # Seleção do material (Água ou Ar) para ajustar os limites de exatidão
    material = st.selectbox("Selecione o material:", ["Água", "Ar"])

    if material == "Água":
        limite_exatidao = 5
        ct_medio_ref = 0  # Para Água, o CT médio de referência é 0 (e intervalo de ±5)
    else:  # Quando for "Ar"
        limite_exatidao = 10  # Limite de exatidão é ±10
        ct_medio_ref = 1000  # Para Ar, o CT médio de referência será 1000 (e intervalo de ±10)

    # Limites de tolerância
    limite_ruido = 15
    limite_uniformidade = 5

    # Avaliações de conformidade para exatidão (verificando se o CT médio está dentro do intervalo permitido)
    # Para "Água", verifica-se o intervalo de -5 a +5 (referência 0)
    # Para "Ar", verifica-se o intervalo de 990 a 1010 (referência 1000)
    exatidao_ok = all(ct_medio_ref - limite_exatidao <= ct <= ct_medio_ref + limite_exatidao for ct in ct_medios)

    ruido_ok = all(r <= limite_ruido for r in ruido_percent)
    uniformidade_ok = uniformidade <= limite_uniformidade



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

    resultados_ruido = pd.DataFrame({
        "ROI": nomes_rois,
        "Ruído (%)": ruido_percent,
        "Limite (%)": [limite_ruido] * 5,
        "Status": ["OK" if r <= limite_ruido else "Fora" for r in ruido_percent]
    })

    resultados_uniformidade = pd.DataFrame({
        "ROI": nomes_rois[1:],  # Não inclui o centro na tabela de uniformidade
        "Uniformidade (HU)": delta_ct_perifericos,
        "Limite (±HU)": [limite_uniformidade] * 4,
        "Status": ["OK" if abs(u) <= limite_uniformidade else "Fora" for u in delta_ct_perifericos]
    })

    resultados_geral = pd.DataFrame({
        "Métrica": ["Uniformidade (HU)", "Ruído (%)"],
        "Valor": [uniformidade, max(ruido_percent)],
        "Limite": [f"≤{limite_uniformidade} HU", f"≤{limite_ruido}%"],
        "Status": ["OK" if uniformidade_ok else "Fora",
                   "OK" if ruido_ok else "Fora"]
    })

    def highlight_status(row):
        color_map = {'OK': '#90ee90', 'Fora': '#f08080'}
        return [f'background-color: {color_map.get(row["Status"], "")}'] * len(row)

    st.subheader("Exatidão")
    st.dataframe(resultados_exatidao.style.format({'CT médio (HU)': '{:.2f}'}).apply(highlight_status, axis=1))
    
    st.subheader("Ruído")
    st.dataframe(resultados_ruido.style.format({'Ruído (%)': '{:.2f}'}).apply(highlight_status, axis=1))

    st.subheader("Uniformidade")
    st.dataframe(resultados_uniformidade.style.format({'Uniformidade (HU)': '{:.2f}'}).apply(highlight_status, axis=1))

    if all([exatidao_ok, uniformidade_ok, ruido_ok]):
        st.success("✅ Equipamento conforme os limites da IN 93/2021.")
    else:
        st.error("❌ Equipamento fora de conformidade — verificar calibração e parâmetros de aquisição.")

    # ---------- Baixar PDF com as tabelas ----------------
    if st.button("💾 Baixar PDF com as tabelas e a imagem"):
        # Criar o PDF em memória
        buffer_pdf = BytesIO()
        c = canvas.Canvas(buffer_pdf, pagesize=letter)

        # Cabeçalho e data
        c.setFont("Helvetica-Bold", 13)
        c.drawString(30, 760, "Relatório do Teste Semanal de Tomografia Computadorizada")
        c.setFont("Helvetica", 10)
        c.drawString(30, 745, f"Data e hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        c.line(30, 740, 580, 740)

        # Salvar imagem temporária e inserir no PDF
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_img_file:
            fig_img.savefig(tmp_img_file.name)
            c.drawImage(tmp_img_file.name, 60, 420, width=300, height=300)

                # --- Função auxiliar para desenhar tabelas ---
        def desenhar_tabela(c, df, titulo, y_pos):
            """Desenha uma tabela formatada a partir de um DataFrame."""
            from reportlab.lib import colors
            from reportlab.platypus import Table, TableStyle

            c.setFont("Helvetica-Bold", 11)
            c.drawString(30, y_pos + 20, titulo)
            c.setFont("Helvetica", 9)

            # Formatar os valores para garantir que apareçam com 2 casas decimais
            # Verificar se o valor é numérico antes de aplicar a formatação
            data = [df.columns.tolist()] + [
                [f'{value:.2f}' if isinstance(value, (int, float)) else value for value in row] 
                for row in df.values.tolist()
            ]

            tabela = Table(data, colWidths=[80, 100, 100, 80])

            tabela.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONT', (0, 1), (-1, -1), 'Helvetica'),
                ('TEXTCOLOR', (-1, 1), (-1, -1), colors.black),
            ]))

            tabela.wrapOn(c, 30, y_pos)
            tabela.drawOn(c, 30, y_pos)


        # --- Inserir tabelas no PDF ---
        y_pos = 260
        desenhar_tabela(c, resultados_exatidao, "", y_pos + 30)

        y_pos -= 120
        desenhar_tabela(c, resultados_ruido, "", y_pos + 30)

        y_pos -= 100
        desenhar_tabela(c, resultados_uniformidade, "", y_pos + 30)

        # Rodapé
        c.setFont("Helvetica-Oblique", 8)
        c.drawString(30, 30, "Gerado automaticamente pelo aplicativo SEMANAL TC")

        # Salvar o PDF em memória
        c.save()
        buffer_pdf.seek(0)

        # Botão de download do PDF
        st.download_button(
            label="📄 Baixar relatório em PDF",
            data=buffer_pdf,
            file_name=f"relatorio_teste_TC_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf"
        )

if __name__ == "__main__":
    app()
