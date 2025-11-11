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

    st.markdown("<h1 style='text-align: center; color: blue;'> Software SEMANAL TC </h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'> Avaliação da Qualidade de Imagens em Tomografia </h2>", unsafe_allow_html=True)
    
    st.write("*Desenvolvido por Rafael Borges de Carvalho*")
    st.write("*Orientado por Professora Doutora Thatiane Alves Pianoschi e Professora Doutora Viviane Rodrigues Botelho*")
    st.markdown('### Orientações para aquisição e armazenamento da imagem')
    
    st.write('''
    1) Posicione o phantom na mesa do tomógrafo, de forma que o seu centro coincida com o isocentro do equipamento (utilize os lasers para garantir o alinhamento correto nos eixos x, y e z);
    2) Certifique-se de que o phantom esteja estável e corretamente apoiado sobre a mesa, sem inclinações;
    3) Configure o exame no modo axial (não helicoidal) utilizando os parâmetros dos protocolos clínicos de rotina para cabeça ou abdômen;
    4) Realize um topograma para confirmar o alinhamento central do phantom no plano tomográfico;
    5) Efetue a aquisição da imagem no modo axial, garantindo que o corte passe pelo centro do módulo de uniformidade do phantom;
    6) Verifique a qualidade e o posicionamento da imagem adquirida — o phantom deve estar completamente visível, sem artefatos de movimento ou cortes incompletos;
    7) Exporte a imagem reconstruída no formato DICOM para uma estação de trabalho com o software "Semanal TC" instalado;
    8) Selecione o diretório de armazenamento onde serão arquivadas as imagens do controle de qualidade;
    9) Verifique se o ID do equipamento de TC avaliado está cadastrado no sistema (caso não esteja, realize o cadastro antes de prosseguir);
    10) Faça upload da imagem no módulo “Teste de Qualidade da Imagem".
    ''')

    st.write('---')

    st.write("**Diretório de armazenamento atual:**", pasta_raiz)
    
    st.info("Você pode alterar o diretório de armazenamento informando um novo caminho abaixo:")

    novo_dir = st.text_input("Digite ou cole o novo caminho do diretório:")

    if st.button('Alterar diretório de armazenamento'):
        if novo_dir.strip() != "":
            pasta_csv, pasta_indicadores, pasta_sala_equipamento, pasta_sala_imagens, pasta_raiz = muda_caminho_app(novo_dir)
            st.success(f"Diretório alterado com sucesso para: {novo_dir}")
        else:
            st.warning("Por favor, insira um caminho válido antes de prosseguir.")
