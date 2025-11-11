import os
import pandas as pd
import streamlit as st
from configparser import ConfigParser
from datetime import datetime


def verifica_pastas():
    config = ConfigParser()
    config.read("parametros.ini")

    # Remove espaços acidentais em chaves e valores
    for section in config.sections():
        for key, value in config.items(section):
            config.set(section, key.strip(), value.strip())

    # Cria todas as pastas, se necessário
    pasta_raiz = config['path']['pasta_raiz']
    subpastas = [
        config['path']['pasta_csv'],
        config['path']['pasta_indicadores'],
        config['path']['pasta_sala_equipamento'],
        config['path']['pasta_sala_imagens']
    ]

    for subpasta in subpastas:
        caminho = os.path.join(pasta_raiz, subpasta)
        os.makedirs(caminho, exist_ok=True)


def carrega_ini():
    config = ConfigParser()
    config.read("parametros.ini")

    # Garante limpeza de espaços
    for section in config.sections():
        for key, value in config.items(section):
            config.set(section, key.strip(), value.strip())

    pasta_raiz = config['path']['pasta_raiz']
    pasta_csv = os.path.join(pasta_raiz, config['path']['pasta_csv'])
    pasta_indicadores = os.path.join(pasta_raiz, config['path']['pasta_indicadores'])
    pasta_sala_equipamento = os.path.join(pasta_raiz, config['path']['pasta_sala_equipamento'])
    pasta_sala_imagens = os.path.join(pasta_raiz, config['path']['pasta_sala_imagens'])

    return pasta_csv, pasta_indicadores, pasta_sala_equipamento, pasta_sala_imagens, pasta_raiz


def verifica_csv(pasta_csv):
    arquivo = os.path.join(pasta_csv, "Header.csv")
    if not os.path.isfile(arquivo):
        with open(arquivo, "w", encoding="utf-8") as file:
            file.write("id\n")


def atualiza_ini(section, key, value):
    config = ConfigParser()
    config.read("parametros.ini")
    config.set(section, key, value)
    with open("parametros.ini", 'w', encoding="utf-8") as cfgfile:
        config.write(cfgfile, space_around_delimiters=False)


def arruma_path(dirname):
    return dirname.replace("/", "\\")


def cria_arquivos_resultados_analises(pasta_csv, pasta_sala_equipamento):
    df = pd.read_csv(os.path.join(pasta_csv, "Header.csv"), sep=";")
    for i in df["id"]:
        arquivo_csv = os.path.join(pasta_sala_equipamento, f"{i}.csv")
        if not os.path.isfile(arquivo_csv):
            colunas = [
                "Sala do equipamento", "Nome da Imagem", "Data da avaliação",
                "Parecer", "Fibras", "Microcalcificações", "Massas", "kVp", "mAs",
                "AEC", "Dose (dGy)", "Material_anodo", "Material_filtro",
                "Dimensao_fov", "Distancia_phantom", "Distancia_detector",
                "Tipo_filtro", "Ponto_focal", "Espessura_phantom", "Grade",
                "Media", "Variancia", "SNR", "CNR", "X_BG", "Sigma", "X_ROI"
            ]
            pd.DataFrame(columns=colunas).to_csv(arquivo_csv, sep=";", index=False, encoding="utf-8")


def retorna_agora():
    data = datetime.now()
    return "_" + data.strftime("%Y%m%d-%H%M%S")


def criar_pasta_raiz():
    # No Streamlit Cloud, cria na pasta local do app
    pasta = "dados_local"
    try:
        os.makedirs(pasta, exist_ok=True)
        st.info(f"Pasta criada/verificada: `{pasta}`")
    except OSError:
        st.error("❌ Diretório não pôde ser criado")
