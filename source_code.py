import homepage
import avaliar_teste_tc
import guia
#import paineis
import dicom
import registro
import streamlit as st
from globais import *
from configparser import ConfigParser

config = ConfigParser()
config.read("parametros.ini")


PAGES = {"Página Inicial": homepage,
         "Guia de Usuário": guia,
         "Qualidade da Imagem": avaliar_teste_tc,
         "Registros dos Testes": registro,
         "Acompanhamento das Doses": dicom,
         }

criar_pasta_raiz()
verifica_pastas()
pasta_csv, pasta_indicadores, pasta_sala_equipamento, pasta_sala_imagens, pasta_raiz = carrega_ini()

#Centralizando as imagens
col1, col2, col3 = st.sidebar.columns([1,5,1])

with col1:
    st.write("")

with col2:
    logo_image = "semanaltc.png"
    st.image(logo_image, width = 1600)

with col3:
    st.write("")

st.sidebar.header("Navegação")

selection = st.sidebar.radio("", list(PAGES.keys()))
st.sidebar.write("---")


c1, c2, c3 = st.sidebar.columns([1,2,1])
with c1:
    st.write("")
with c2:
    logo_ufcspa = "ufcspa.png"
    st.image(logo_ufcspa, width = 150)
with c3:
    st.write("")

page = PAGES[selection]
page.app()