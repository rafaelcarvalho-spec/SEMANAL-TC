import numpy as np
import pydicom as dicom
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import cv2
import os
import datetime
from io import BytesIO

# ---------------- Funções ----------------

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
    return rois

def extrair_info_dicom(ds):
    """Extrai informações principais do cabeçalho DICOM e formata a data do estudo para DD/MM/YYYY."""
    def get(tag):
        return getattr(ds, tag, "N/A")
    
    # Formatar a data do estudo (StudyDate) para o formato DD/MM/YYYY
    study_date = get("StudyDate")
    if study_date != "N/A":
        try:
            # Converte de YYYYMMDD para DD/MM/YYYY
            study_date = datetime.datetime.strptime(study_date, "%Y%m%d").strftime("%d/%m/%Y")
        except ValueError:
            study_date = "Data inválida"  # Caso a conversão falhe, coloca um valor padrão
    
    info = {
        "Paciente": str(get("PatientName")),
        "ID do Paciente": str(get("PatientID")),
        "Modalidade": str(get("Modality")),
        "Data do Estudo": study_date,  # A data já estará no formato DD/MM/YYYY
        "Descrição da Série": str(get("SeriesDescription")),
        "kVp": str(get("KVP")),
        "mAs": str(get("Exposure")),
        "Fabricante": str(get("Manufacturer")),
        "Modelo do Equipamento": str(get("ManufacturerModelName")),
        "Tempo de Exposição": str(get("ExposureTime")),
        "CTDIvol": str(get("CTDIvol")),
        "DLP": str(get("DLP value")),
        
    }
    
    return pd.DataFrame(info.items(), columns=["Campo DICOM", "Valor"])

# Função de exportação para Excel
def app():
    st.title("Metadados DICOM: Acompanhamento de doses")
    st.write("Carregue uma imagem DICOM para visualizar os metadados.")

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

    nome_escolhido = nomes[st.session_state.img_index]
    img = imagens_dict[nome_escolhido]
    st.info(f"Imagem selecionada: {nome_escolhido}")

    # ---------- Exibe METADADOS DICOM ----------
    st.subheader("📋 Informações DICOM")
    st.dataframe(metadados_dict[nome_escolhido])

    # ---------------------------
    # Exportar / Atualizar Excel
    # ---------------------------

    st.subheader("💾 Exportar / Atualizar Excel")

    opcao = st.radio(
        "Escolha uma opção:",
        ["Baixar novo arquivo Excel", "Atualizar arquivo Excel existente"]
    )

    if opcao == "Baixar novo arquivo Excel":
        buffer_excel = BytesIO()
        with pd.ExcelWriter(buffer_excel, engine="openpyxl") as writer:
            # Antes de exportar, garantir que a data esteja formatada corretamente
            metadados = metadados_dict[nome_escolhido]
            # A data já está formatada no formato DD/MM/YYYY
            metadados.to_excel(writer, index=False, sheet_name="Metadados_DICOM")
        buffer_excel.seek(0)

        st.download_button(
            label="📊 Baixar nova tabela Excel",
            data=buffer_excel,
            file_name=f"metadados_dicom_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    elif opcao == "Atualizar arquivo Excel existente":
        uploaded_excel = st.file_uploader("Selecione o arquivo Excel existente", type=["xlsx"])
        if uploaded_excel:
            try:
                df_existente = pd.read_excel(uploaded_excel)

                # Encontrar colunas com a data atual
                data_teste = datetime.datetime.now().strftime("%d/%m/%Y")
                colunas_data = [c for c in df_existente.columns if data_teste in c]

                if not colunas_data:
                    # Primeira coluna do dia, sem sufixo
                    coluna_nova = f"Valor ({data_teste})"
                else:
                    # Gera o próximo índice incremental
                    indices_existentes = []
                    for c in colunas_data:
                        try:
                            parte = c.split("_")[-1].replace(")", "")
                            indice = int(parte) if parte.isdigit() else 0
                            indices_existentes.append(indice)
                        except ValueError:
                            indices_existentes.append(0)
                    proximo_indice = max(indices_existentes) + 1
                    coluna_nova = f"Valor ({data_teste}_{proximo_indice})"

                # Adiciona a nova coluna ao Excel
                df_atualizado = df_existente.merge(metadados_dict[nome_escolhido], on="Campo DICOM", how="outer")
                df_atualizado = df_atualizado.rename(columns={coluna_nova: coluna_nova})

                buffer_excel = BytesIO()
                with pd.ExcelWriter(buffer_excel, engine="openpyxl") as writer:
                    df_atualizado.to_excel(writer, index=False, sheet_name="Metadados_DICOM")
                buffer_excel.seek(0)

                st.success(f"✅ Excel atualizado")
                st.download_button(
                    label="📥 Baixar Excel atualizado",
                    data=buffer_excel,
                    file_name=f"{uploaded_excel.name.split('.')[0]}_atualizado.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

            except Exception as e:
                st.error(f"Erro ao atualizar o Excel: {e}")



if __name__ == "__main__":
    app()
