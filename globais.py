import os
import pandas as pd
import streamlit as st

from configparser import ConfigParser
from datetime import datetime


def verifica_pastas():
    config = ConfigParser()
    config.read("parametros.ini")
    if not os.path.isdir(config['path']['pasta_raiz']):
        os.makedirs(config['path']['pasta_raiz'],  exist_ok=True)
        os.makedirs(config['path']['pasta_raiz'] +
                    config['path']['pasta_csv'],  exist_ok=True)
        os.makedirs(config['path']['pasta_raiz'] +
                    config['path']['pasta_indicadores'],  exist_ok=True)
        os.makedirs(config['path']['pasta_raiz'] + config['path']
                    ['pasta_sala_equipamento'],  exist_ok=True)
        os.makedirs(config['path']['pasta_raiz'] + config['path']
                    ['pasta_sala_imagens '],  exist_ok=True)
    elif not os.path.isdir(config['path']['pasta_raiz'] + config['path']['pasta_csv']):
        os.makedirs(config['path']['pasta_raiz'] +
                    config['path']['pasta_csv'],  exist_ok=True)
        os.makedirs(config['path']['pasta_raiz'] +
                    config['path']['pasta_indicadores'],  exist_ok=True)
        os.makedirs(config['path']['pasta_raiz'] + config['path']
                    ['pasta_sala_equipamento'],  exist_ok=True)
        os.makedirs(config['path']['pasta_raiz'] +
                    config['path']['pasta_sala_imagens'],  exist_ok=True)
    elif not os.path.isdir(config['path']['pasta_raiz'] + config['path']['pasta_indicadores']):
        os.makedirs(config['path']['pasta_raiz'] +
                    config['path']['pasta_indicadores'],  exist_ok=True)
        os.makedirs(config['path']['pasta_raiz'] + config['path']
                    ['pasta_sala_equipamento'],  exist_ok=True)
        os.makedirs(config['path']['pasta_raiz'] +
                    config['path']['pasta_sala_imagens'],  exist_ok=True)
    elif not os.path.isdir(config['path']['pasta_raiz'] + config['path']['pasta_sala_equipamento']):
        os.makedirs(config['path']['pasta_raiz'] + config['path']
                    ['pasta_sala_equipamento'],  exist_ok=True)
        os.makedirs(config['path']['pasta_raiz'] +
                    config['path']['pasta_sala_imagens'],  exist_ok=True)


def carrega_ini():
    config = ConfigParser()
    config.read("parametros.ini")

    pasta_csv = config['path']['pasta_raiz'] + config['path']['pasta_csv']
    pasta_indicadores = config['path']['pasta_raiz'] + \
        config['path']['pasta_indicadores']
    pasta_sala_equipamento = config['path']['pasta_raiz'] + \
        config['path']['pasta_sala_equipamento']
    pasta_sala_imagens = config['path']['pasta_raiz'] + \
        config['path']['pasta_sala_imagens']
    pasta_raiz = config['path']['pasta_raiz']
    return(pasta_csv, pasta_indicadores, pasta_sala_equipamento, pasta_sala_imagens, pasta_raiz)


def verifica_csv(pasta_csv):
    arquivo = pasta_csv + "/Header.csv"
    if not os.path.isfile(arquivo):
        with open(arquivo, "w") as file:
            file.write("id\n")
            file.close()


def atualiza_ini(section, key, value):
    config = ConfigParser()
    config.read("parametros.ini")
    config.set(section, key, value)
    cfgfile = open("parametros.ini", 'w')
    # use flag in case case you need to avoid white space.
    config.write(cfgfile, space_around_delimiters=False)
    cfgfile.close()


def arruma_path(dirname):
    return dirname.replace("/", "\\")


def cria_arquivos_resultados_analises(pasta_csv, pasta_sala_equipamento):
    df = pd.read_csv(pasta_csv + "/Header.csv", sep=";")
    itens = list(df.id)
    for i in itens:
        if not os.path.isfile(pasta_sala_equipamento + "/" + str(i) + ".csv"):
            resultados = pd.DataFrame(columns=[
                "Sala do equipamento",
                "Nome da Imagem",
                "Data da avaliação",
                "Parecer",
                "Fibras",
                "Microcalcificações",
                "Massas",
                "kVp",
                "mAs",
                "AEC",
                "Dose (dGy)",
                "Material_anodo",
                "Material_filtro",
                "Dimensao_fov",
                "Distancia_phantom",
                "Distancia_detector",
                "Tipo_filtro",
                "Ponto_focal",
                "Espessura_phantom",
                "Grade",
                "Media",
                "Variancia",
                "SNR",
                "CNR",
                "X_BG",
                "Sigma",
                "X_ROI"
            ])
            resultados.to_csv(pasta_sala_equipamento + "/" + str(i) +
                              ".csv", sep=";", index=False, encoding="utf-8")


def retorna_agora():
    data = datetime.now()
    mnow = str(data.year) + '{:0>2}'.format(str(data.month)) + '{:0>2}'.format(
        str(data.day)) + "-" + str(data.hour) + str(data.minute) + str(data.second)
    return "_" + mnow

def criar_pasta_raiz():
    try:
        os.makedirs(r"C:\CQMAMO",  exist_ok=True)
    except OSError as error:
        st.write('Diretório não pode ser criado')
        