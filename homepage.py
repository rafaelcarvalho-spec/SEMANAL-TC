import pandas as pd
from scipy.stats import skew, kurtosis
import streamlit as st
import time
from globais import *

# Layout
st.set_page_config(layout="wide")

def form_callback():
    pass    

def muda_caminho_app(dirname):
    atualiza_ini("path", "pasta_raiz", dirname + "/")
    pasta_csv, pasta_indicadores, pasta_sala_equipamento, pasta_sala_imagens, pasta_raiz = carrega_ini()
    verifica_pastas()
    verifica_csv(pasta_csv)
    return pasta_csv, pasta_indicadores, pasta_sala_equipamento, pasta_sala_imagens, pasta_raiz

def app():

    verifica_pastas()
    pasta_csv, pasta_indicadores, pasta_sala_equipamento, pasta_sala_imagens, pasta_raiz = carrega_ini()
    verifica_csv(pasta_csv)

    st.markdown("<h1 style='text-align: center; color: blue;'> SEMANAL TC </h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'> Avaliação da Qualidade das Imagems em Testes Semanais de Tomografia Computadorizada </h2>", unsafe_allow_html=True)
    
    #st.markdown("<br><br>", unsafe_allow_html=True)  # Espaço maior entre os parágrafos

    st.write('---')
    
    st.markdown('### Sobre o Aplicativo:')
    
    st.markdown("""

    Este ambiente virtual foi desenvolvido como uma proposta para padronizar a execução e a análise dos resultados dos testes semanais de tomografia computadorizada (TC).
    A partir da seleção de imagens DICOM pelo usuário, o aplicativo calcula e avalia automaticamente a Unifomidade do Número de TC, Exatidão do Número de TC e Ruído. 
    
    Além disso, há funcionalidades extras, como: Visualização das Métricas DICOM, Avaliação da Dose e Download dos Dados Analisados.

    O qualidade das imagens são avaliadas em relação aos limites estabelecidos pela Instrução Normativa (IN) Nº 93 da ANVISA.
    """)

    st.markdown("<br><br>", unsafe_allow_html=True)  # Espaço maior entre os parágrafos

    st.markdown(
    """
    <div style="text-align: center; font-size: 14px;">
        Desenvolvido por Rafael Borges de Carvalho<br>
        Orientado por Professora Doutora Thatiane Alves Pianoschi e Professora Doutora Viviane Rodrigues Botelho
    </div>
    """, unsafe_allow_html=True
)


    st.write('---')

    #st.write("**Diretório de armazenamento atual:**", pasta_raiz)
    
    #st.info("Você pode alterar o diretório de armazenamento informando um novo caminho abaixo:")

    #novo_dir = st.text_input("Digite ou cole o novo caminho do diretório:")

    #if st.button('Alterar diretório de armazenamento'):
        #if novo_dir.strip() != "":
            #pasta_csv, pasta_indicadores, pasta_sala_equipamento, pasta_sala_imagens, pasta_raiz = muda_caminho_app(novo_dir)
            #st.success(f"Diretório alterado com sucesso para: {novo_dir}")
        #else:
            #st.warning("Por favor, insira um caminho válido antes de prosseguir.")