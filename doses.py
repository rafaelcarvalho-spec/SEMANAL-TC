import streamlit as st
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

def app():
    st.title("Registro do Teste Semanal")

    # Inicializando tabela no session_state para persistência
    colunas = ["Data", "Horário", "Protocolo", "mAs", "kV", "CDTIvol (mGy)", "DLP (mGy*cm)", "Realizado por"]
    if "tabela_tomografia" not in st.session_state:
        st.session_state.tabela_tomografia = pd.DataFrame(columns=colunas)

    st.markdown("### Adicionar novo registro")

    # Formulário para entrada de dados
    with st.form("form_tomografia"):
        data = st.date_input("Data", value=datetime.today())
        horario = st.time_input("Horário", value=datetime.now().time())
        protocolo = st.text_input("Protocolo")
        mas = st.number_input("mAs", min_value=0.0, format="%.1f")
        kv = st.number_input("kV", min_value=0.0, format="%.1f")
        cdti_vol = st.number_input("CDTIvol (mGy)", min_value=0.0, format="%.3f")
        dlp = st.number_input("DLP (mGy*cm)", min_value=0.0, format="%.3f")
        realizado_por = st.text_input("Realizado por")

        submitted = st.form_submit_button("Adicionar registro")

        if submitted:
            nova_linha = {
                "Data": data.strftime("%d/%m/%Y"),
                "Horário": horario.strftime("%H:%M:%S"),
                "Protocolo": protocolo,
                "mAs": mas,
                "kV": kv,
                "CDTIvol (mGy)": cdti_vol,
                "DLP (mGy*cm)": dlp,
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

    # --- Gráficos de acompanhamento ---
    if not st.session_state.tabela_tomografia.empty:
        st.markdown("### Acompanhamento das doses ao longo do tempo")

        df = st.session_state.tabela_tomografia.copy()
        df["Data_plot"] = pd.to_datetime(df["Data"], format="%d/%m/%Y", errors="coerce")
        df = df.sort_values("Data_plot")

        col1, col2 = st.columns(2)

        # --- Gráfico 1: CTDIvol ---
        with col1:
            fig, ax = plt.subplots(figsize=(4, 3))
            ax.plot(df["Data_plot"], df["CDTIvol (mGy)"],
                    marker='o', markersize=4, linewidth=2, color='#1f77b4', label='CTDIvol')
            ax.set_ylabel("CTDIvol (mGy)", fontsize=7)
            ax.set_xticks(df["Data_plot"])
            ax.set_xticklabels(df["Data_plot"].dt.strftime("%d/%m"), rotation=45, fontsize=6)
            ax.tick_params(axis='y', labelsize=6)
            ax.grid(True, linestyle='--', alpha=0.5)
            ax.set_ylim(bottom=0)
            ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15),
                      fontsize=7, frameon=False, ncol=1, labelcolor='#1f77b4')
            st.pyplot(fig)

        # --- Gráfico 2: DLP ---
        with col2:
            fig, ax = plt.subplots(figsize=(4, 3))
            ax.plot(df["Data_plot"], df["DLP (mGy*cm)"],
                    marker='o', markersize=4, linewidth=2, color='#ff7f0e', label='DLP')
            ax.set_ylabel("DLP (mGy·cm)", fontsize=7)
            ax.set_xticks(df["Data_plot"])
            ax.set_xticklabels(df["Data_plot"].dt.strftime("%d/%m"), rotation=45, fontsize=6)
            ax.tick_params(axis='y', labelsize=6)
            ax.grid(True, linestyle='--', alpha=0.5)
            ax.set_ylim(bottom=0)
            ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15),
                      fontsize=7, frameon=False, ncol=1, labelcolor='#ff7f0e')
            st.pyplot(fig)
