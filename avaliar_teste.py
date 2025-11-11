import numpy as np
import pydicom as dicom
import matplotlib.pyplot as plt
import os
import pandas as pd
import cv2
from scipy.stats import skew, kurtosis
import streamlit as st
import datetime
from scipy.stats import skew, kurtosis

# =====================================================================
# Configuração para permitir leitura de imagens DICOM com JPEG Lossless
# =====================================================================

dicom.config.convert_wrong_length_to_UN = True

try:
    import gdcm
    dicom.config.image_handlers = [gdcm]
    print("✅ Suporte JPEG Lossless configurado com GDCM.")
except ImportError:
    try:
        import pylibjpeg
        import pylibjpeg_libjpeg
        import pylibjpeg_openjpeg
        print("✅ Suporte JPEG Lossless configurado com pylibjpeg.")
    except ImportError:
        print("⚠️ Não foi possível configurar JPEG Lossless. Instale 'gdcm' ou 'pylibjpeg'.")

# =====================================================================


from globais import *


def create_circular_mask(h, w, center=None, radius=None):
    if center is None:  # use the middle of the image
        center = (int(w/2), int(h/2))
    if radius is None:  # use the smallest distance between the center and image walls
        radius = min(center[0], center[1], w-center[0], h-center[1])

    Y, X = np.ogrid[:h, :w]
    dist_from_center = np.sqrt((X - center[0])**2 + (Y - center[1])**2)

    mask = dist_from_center <= radius
    return mask


def create_df_tags_dicom(imagem, imagem_dicom):
    lista_tags = []
    for tag_dicom in imagem:
        lista_tags.append(tag_dicom)

    valores = []
    atributos = []
    for i in range(0, len(lista_tags)):
        valores.append(str(lista_tags[i])[53:])
        # atributos.append(str(lista_tags[i])[:53])
        atributos.append(str(lista_tags[i].tag))

    data = pd.DataFrame(index=[(imagem_dicom.name)[:12]],
                        columns=atributos)

    data.iloc[0] = valores

    return data

# Função para plotar a imagem


def plot_image(img, nome, color_map):
    fig, ax = plt.subplots()
    w = ax.get_xaxis()
    z = ax.get_yaxis()
    w.set_visible(False)
    z.set_visible(False)
    ax.imshow(img, cmap=color_map)
    ax.set_title(f'{nome}', fontsize=8)
    return fig

def plot_image_draw(img, nome):
    fig, axes = plt.subplots()
    center_roi_mass = (500, 90)
    center_roi_bg = (400, 180)
    raio = 40
    # Desenhando as ROIs para cálculo da CNR
    draw_circle = plt.Circle(center_roi_mass, raio,fill=False,color='white')
    draw_circle2 = plt.Circle(center_roi_bg, raio,fill=False,color='white')
    axes.set_aspect(1)
    axes.add_artist(draw_circle)
    axes.add_artist(draw_circle2)
    plt.annotate('ROI', (570, 70), color='white')
    plt.annotate('BG', (450, 200), color='white')

    axes.get_xaxis().set_visible(False)
    axes.get_yaxis().set_visible(False)
    axes.imshow(img, cmap='gray')
    axes.set_title(f'{nome}', fontsize=8)
    return fig

# Função para cortar a ROI fixa das imagens Valentina
def crop_ROI(imagem):
    roi = imagem.pixel_array[740:1570, 920:1700]
    return roi


def roi_CNR(img):
    corte_subROI = img[0:250, 350:650]
    roi = np.uint8(corte_subROI)
    img_negativa = cv2.bitwise_not(roi)
    return corte_subROI


# Função para calcular histograma
def histogram(imagem_cortada):
    bins = 2 ** 16
    hist, edges = np.histogram(imagem_cortada, bins = bins)
    fig, ax = plt.subplots()
    ax.plot(hist, label='Imagem Teste')
    ax.set_xlabel('Intensidade')
    ax.set_ylabel('Número de pixels')
    return hist, fig


def app():

    pasta_csv, pasta_indicadores, pasta_sala_equipamento, pasta_sala_imagens, pasta_raiz = carrega_ini()
    cria_arquivos_resultados_analises(pasta_csv, pasta_sala_equipamento)

    st.title("Teste da qualidade da imagem")
    st.write('''
    Nessa página, será possível realizar o teste de qualidade da imagem para a mamografia, segundo a IN N° 92 da ANVISA.

    ''')

    df = pd.read_csv(pasta_csv + "/Header.csv", sep=";")
    list_respostas = list(df.id)
    list_respostas.insert(0, '')

    upload_image = st.file_uploader("Selecione a imagem a ser avaliada",
                                    key='1',
                                    help="Para inserir imagem, basta clicar em Browse Files ou arrastá-la.")

    if upload_image is None:
        st.warning('Imagem não selecionada!')
    else:
        st.info(
            f'Diretório de armazenamento do teste: {pasta_sala_equipamento}')
        nome_equipamento = st.selectbox('Selecione o ID do equipamento associado a imagem', list_respostas,
                                        format_func=lambda x: 'Selecione uma opção' if (isinstance(x, str) and x == '') else str(x))

        if nome_equipamento == '':
            st.write('')
        else:

            img_upload = dicom.dcmread(upload_image)

            # Criando o dataset para as tags DICOM
            valentina = create_df_tags_dicom(img_upload,upload_image)

            KVP = valentina['(0018,0060)']
            MAS = valentina['(0018,1152)']
            anodo = valentina['(0018,1191)']
            filtro = valentina['(0018,7050)']
            shape_fov = valentina['(0018,1147)']
            dimension_fov = valentina['(0018,1149)']
            organ_dose = valentina['(0040,0316)']
            distancia_paciente = valentina['(0018,1111)']
            distancia_detecttor = valentina['(0018,1110)']
            filter_type = valentina['(0018,1160)']
            focal_spot = valentina['(0018,1190)']
            body_part_thickness = valentina['(0018,11A0)']
            grid = valentina['(0018,1166)']
            AEC = valentina['(0018,7060)']
            data_aquisicao = valentina['(0008,0022)']

            kVp = [float(x.replace("'", "").strip()) for x in KVP]
            mAs = [float(x.replace("'", "").strip()) for x in MAS]

            # Arrumando a data
            data_str = data_aquisicao.values[0].replace("'", "").strip()
            ano = int(data_str[0:4])  # започва от 0
            mes = int(data_str[4:6])
            dia = int(data_str[6:8])
            date_aquisition = datetime(ano, mes, dia).date()
            # Arrumando AEC
            modo_aec = AEC.tolist()[0]

            roi_cortada = crop_ROI(img_upload)
            imagem_negativada_cnr = roi_CNR(roi_cortada)
            h, w = imagem_negativada_cnr.shape[:2]
            mask_massa = create_circular_mask(
                h, w, center=(150, 90), radius=40)
            mask_bg = create_circular_mask(h, w, center=(170, 200), radius=40)

            roi_massa_cortada = imagem_negativada_cnr[mask_massa]
            roi_bg_cortada = imagem_negativada_cnr[mask_bg]

            # Calculando as métricas estatísticas para as ROIs
            path_salvar_dados_indicadores = pasta_indicadores
            dados_hist, img_hist = histogram(roi_cortada)
            plt.savefig(path_salvar_dados_indicadores+f'\{upload_image.name}'+'.png')  # Salvando o histograma
            media = np.mean(img_upload.pixel_array)
            variancia = np.var(img_upload.pixel_array)
            pixel_values = img_upload.pixel_array.flatten()
            assimetria = skew(pixel_values)
            curtose = kurtosis(pixel_values)

            # st.write(f'Media: {media} e Variancia: {variancia}')
            SNR = np.mean(roi_massa_cortada) / np.std(roi_bg_cortada)
            CNR = np.absolute(np.mean(roi_bg_cortada) - np.mean(roi_massa_cortada)) / np.std(roi_bg_cortada)

            def clean_str(value):
                if isinstance(value, list):
                    return ', '.join(str(v).replace("'", "").replace("[", "").replace("]", "").strip() for v in value)
                elif isinstance(value, str):
                    return value.replace("'", "").strip()
                else:
                    return value

            data_tags = pd.DataFrame({
                "nome": upload_image.name,
                "Data": clean_str(data_aquisicao.values[0]),
                "kVp": kVp,
                "mAs": mAs,
                "AEC": clean_str(modo_aec),
                "anodo": clean_str(anodo.tolist()),
                "filtro": clean_str(filtro.tolist()),
                "dimensao_fov": clean_str(dimension_fov.tolist()),
                "shape_fov": clean_str(shape_fov.tolist()),
                "organ_dose": clean_str(organ_dose.tolist()),
                "distancia_paciente": clean_str(distancia_paciente.tolist()),
                "distancia_detector": clean_str(distancia_detecttor.tolist()),
                "filter_type": clean_str(filter_type.tolist()),
                "focal_spot": clean_str(focal_spot.tolist()),
                "body_part_thickness": clean_str(body_part_thickness.tolist()),
                "grid": clean_str(grid.tolist())
            })

            # data_tags['organ_dose'] = data_tags['organ_dose'].apply(lambda x: np.fromstring(x.replace('"',''), sep=' '))
            # data_tags['distancia_paciente'] = data_tags['distancia_paciente'].apply(lambda x: np.fromstring(x.replace('"',''), sep=' '))
            # data_tags['distancia_detector'] = data_tags['distancia_detector'].apply(lambda x: np.fromstring(x.replace('"',''), sep=' '))
            # data_tags['focal_spot'] = data_tags['focal_spot'].apply(lambda x: np.fromstring(x.replace('"',''), sep=' '))
            # data_tags['body_part_thickness'] = data_tags['body_part_thickness'].apply(lambda x: np.fromstring(x.replace('"',''), sep=' '))

            with st.container():
                # Criando colunas no Dashboard
                c1, c2 = st.columns(2)

                with c1:
                    ############################# Código para input da avaliação ##################################
                    form = st.form(key='my_form', clear_on_submit=True)
                    form.write(f'Data aquisição da imagem: {dia}/{mes}/{ano}')
                    form.write(
                        f'Controle automático de exposição (CAE): {modo_aec}')
                    n_fibras = form.number_input(
                        label='Número de fibras visualizadas', min_value=0, max_value=6, step=1)
                    n_specks = form.number_input(
                        label='Número de microcalcificações visualizadas', min_value=0, max_value=5, step=1)
                    n_massas = form.number_input(
                        label='Número de massas visualizadas', min_value=0, max_value=5, step=1)
                    submit_button = form.form_submit_button(label='Avaliar')

                ########################## Código para dataset Valentina ##################################
                with c2:
                    # Negativando a imagem
                    imagem_negativada = cv2.bitwise_not(roi_cortada)

                    st.write(plot_image(imagem_negativada,
                                        upload_image.name, 'gray'))

            expander = st.expander(
                "Parâmetros técnicos de aquisição da imagem")
            with expander:
                st.write(
                    f"Informações extraídas do cabeçalho DICOM da imagem {upload_image.name}.")
                a = data_tags.iloc[[0]]
                st.write(a)
            # ---------------------------------------------------------------------------------------------------------
            if submit_button:

                # Avaliando a imagem
                if n_fibras >= 4 and n_specks >= 3 and n_massas >= 3:
                    st.success(
                        "Avaliação conforme a legislação IN N° 92!")
                    v_resultado_avaliacao = "Conforme"
                else:
                    st.error(
                        "Avaliação não conforme a legislação IN N° 92!")
                    v_resultado_avaliacao = "Não Conforme"
                df = pd.DataFrame({
                    "Sala do equipamento": nome_equipamento,
                    "Nome da Imagem": upload_image.name,
                    "Data da avaliação": date_aquisition,
                    "Parecer": v_resultado_avaliacao,
                    "Fibras": n_fibras,
                    "Microcalcificações": n_specks,
                    "Massas": n_massas,
                    "kVp": data_tags.kVp.values,
                    "mAs": data_tags.mAs.values,
                    "AEC": data_tags.AEC.values,
                    "Dose (dGy)": data_tags.organ_dose.values,
                    "Material_anodo": data_tags.anodo.values,
                    "Material_filtro": data_tags.filtro.values,
                    "Dimensao_fov": data_tags.dimensao_fov.values,
                    "Distancia_phantom": data_tags.distancia_paciente.values,
                    "Distancia_detector": data_tags.distancia_detector.values,
                    "Tipo_filtro": data_tags.filter_type.values,
                    "Ponto_focal": data_tags.focal_spot.values,
                    "Espessura_phantom": data_tags.body_part_thickness.values,
                    "Grade": data_tags.grid.values,
                    "Media": media,
                    "Variancia": variancia,
                    "Assimetria": assimetria,
                    "Curtose": curtose,
                    "SNR": SNR,
                    "CNR": CNR,
                    "X_BG": np.mean(roi_bg_cortada),
                    "Sigma": np.std(roi_bg_cortada),
                    "X_ROI": np.mean(roi_massa_cortada)
                }
                )

                df1 = pd.read_csv(pasta_sala_equipamento +
                                  "\\" + str(nome_equipamento) + ".csv", sep=";")
                df2 = pd.concat([df, df1])
                df2.to_csv(pasta_sala_equipamento + "\\" + str(nome_equipamento) +
                           ".csv", sep=";", encoding='utf-8', index=False)

            path_sala = pasta_sala_equipamento

            roi_desenhada = plot_image_draw(imagem_negativada, upload_image.name)
            plt.savefig(path_salvar_dados_indicadores+f'\CNR_{upload_image.name}'+'.png')

            for item in list_respostas[1:]:
                id_sala = item
                name_pasta = f'{pasta_sala_imagens}\{id_sala}'
                try:
                    os.makedirs(name_pasta, exist_ok=True)
                except OSError as error:
                    st.write('Diretório não pode ser criado')

            # Salvando a imagem em PNG
            bb = plot_image(imagem_negativada, upload_image.name, 'gray')
            plt.savefig(f'{pasta_sala_imagens}\{nome_equipamento}\{upload_image.name[:-4]}.png')
