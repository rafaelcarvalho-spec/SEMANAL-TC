import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO
import openpyxl

def app():
    st.title("Registro do Teste Semanal")

    # Inicializando tabela no session_state para persistência
    colunas = ["Data", "Horário", "Realizado por"]
    if "tabela_tomografia" not in st.session_state:
        st.session_state.tabela_tomografia = pd.DataFrame(columns=colunas)

    st.markdown("### Adicionar novo registro")

    # Formulário para entrada de dados
    with st.form("form_tomografia"):
        data = st.date_input("Data", value=datetime.today())
        horario = st.time_input("Horário", value=datetime.now().time())
        realizado_por = st.text_input("Realizado por")

        submitted = st.form_submit_button("Adicionar registro")

        if submitted:
            nova_linha = {
                "Data": data.strftime("%d/%m/%Y"),
                "Horário": horario.strftime("%H:%M:%S"),
                "Realizado por": realizado_por
            }
            st.session_state.tabela_tomografia = pd.concat(
                [st.session_state.tabela_tomografia, pd.DataFrame([nova_linha])],
                ignore_index=True
            )
            st.success("Registro adicionado!")

    # Exibir tabela de registros
    st.markdown("### Tabela de registros")
    st.dataframe(st.session_state.tabela_tomografia)

    # ---------------- OPÇÃO PARA CARREGAR OU CRIAR NOVO ARQUIVO ----------------
    st.markdown("### Abrir arquivo Excel existente ou criar um novo")

    uploaded_file = st.file_uploader("Escolha um arquivo Excel existente", type="xlsx")

    if uploaded_file is not None:
        # Carregar o arquivo Excel
        df_existing = pd.read_excel(uploaded_file, engine="openpyxl")

        # Atualizar com os novos registros
        if not st.session_state.tabela_tomografia.empty:
            df_updated = pd.concat([df_existing, st.session_state.tabela_tomografia], ignore_index=True)

            # Converter DataFrame atualizado em Excel
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                df_updated.to_excel(writer, index=False, sheet_name="Registros")
            buffer.seek(0)

            # Botão para salvar o arquivo atualizado
            st.download_button(
                label="💾 Baixar arquivo Excel atualizado",
                data=buffer,
                file_name=f"registro_teste_semanal_atualizado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.info("Nenhum novo registro disponível para atualizar.")

    else:
        st.info("Nenhum arquivo carregado. Criando um novo arquivo...")

        # Caso o usuário não tenha carregado um arquivo, criamos um novo arquivo Excel
        if not st.session_state.tabela_tomografia.empty:
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                st.session_state.tabela_tomografia.to_excel(writer, index=False, sheet_name="Registros")
            buffer.seek(0)

            # Botão para criar e salvar o novo arquivo Excel
            st.download_button(
                label="💾 Criar novo arquivo Excel",
                data=buffer,
                file_name=f"registro_teste_semanal_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
