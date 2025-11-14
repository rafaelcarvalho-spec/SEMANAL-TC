import streamlit as st

def app():
    st.title("Cálculo e Avaliação Automática")
    st.subheader("Exame de Crânio - Testa para a água")

    # --- Espaçamento e caixa de fundo para entrada de dados ---
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style='background-color:#ffffff; padding:15px; border-radius:10px'>
    """, unsafe_allow_html=True
    )

    # --- Primeira tabela: Entrada de dados ---
    if "roi_valores" not in st.session_state:
        st.session_state.roi_valores = {
            "Valor medido": ["0.0"]*5,
            "Desvio padrão": ["0.0"]*5
        }

    # Cabeçalho da tabela
    cols = st.columns(6)
    cols[0].markdown(" ")
    for i, col in enumerate(cols[1:]):
        col.markdown(f"<p style='text-align: center; font-weight: bold;'>ROI {i+1}</p>", unsafe_allow_html=True)

    # Limites de tolerância
    limites_exat = 5      # Exatidão ±5
    limite_ruido = 15     # Ruído ≤15%
    limite_uniform = 5    # Uniformidade ±5

    # Entrada: Valor Medido
    cols = st.columns(6)
    cols[0].markdown("<b>Valor medido</b>", unsafe_allow_html=True)
    for i in range(5):
        val = cols[i+1].text_input(
            f"ROI {i+1} Valor Medido",
            value=st.session_state.roi_valores["Valor medido"][i],
            key=f"vm_{i}",
        )
        st.session_state.roi_valores["Valor medido"][i] = val

    # Entrada: Desvio Padrão
    cols = st.columns(6)
    cols[0].markdown("<b>Desvio padrão</b>", unsafe_allow_html=True)
    for i in range(5):
        val = cols[i+1].text_input(
            f"ROI {i+1} Desvio Padrão",
            value=st.session_state.roi_valores["Desvio padrão"][i],
            key=f"dp_{i}",
        )
        st.session_state.roi_valores["Desvio padrão"][i] = val

    st.markdown("</div>", unsafe_allow_html=True)  # Fechar div de fundo

    # --- Espaçamento antes dos resultados ---
    st.markdown("<br>", unsafe_allow_html=True)

    # --- Segunda tabela: Resultados calculados ---
    st.markdown(
        """
        <div style='background-color:#ffffff; padding:15px; border-radius:10px'>
    """, unsafe_allow_html=True
    )
    st.subheader("Resultados Calculados")
    nomes = ["Exatidão do Nº de TC", "Ruído (%)", "Uniformidade do Nº de TC"]

    # Convertendo valores para float
    try:
        valores_medidos = [float(v.replace(",", ".")) for v in st.session_state.roi_valores["Valor medido"]]
        desvios = [float(v.replace(",", ".")) for v in st.session_state.roi_valores["Desvio padrão"]]
    except:
        valores_medidos = [0.0]*5
        desvios = [0.0]*5

    # Calculando os valores
    exatidão = valores_medidos
    ruido = [(d / 1000) * 100 for d in desvios]

    # Uniformidade sequencial
    uniformidade = [0]  # ROI 1 sempre 0
    for i in range(1, 5):
        uniformidade.append(exatidão[i] - exatidão[i-1])

    # Função para feedback instantâneo (somente símbolos)
    def feedback(valor, limite, tipo="abs"):
        if tipo == "abs":
            if -limite <= valor <= limite:
                return "green", "✅"
            elif -limite*1.1 <= valor <= limite*1.1:
                return "orange", "⚠️"
            else:
                return "red", "❌"
        elif tipo == "max":
            if valor <= limite:
                return "green", "✅"
            elif valor <= limite*1.1:
                return "orange", "⚠️"
            else:
                return "red", "❌"

    # Exibir resultados com feedback (somente símbolos)
    for i, nome in enumerate(nomes):
        cols = st.columns(6)
        cols[0].markdown(f"<b>{nome}</b>", unsafe_allow_html=True)
        for j in range(5):
            if nome == "Exatidão do Nº de TC":
                val = exatidão[j]
                cor, simbolo = feedback(val, limites_exat, "abs")
                cols[j+1].markdown(f"<p style='text-align:center;'>{val:.3f} <span style='color:{cor}'>{simbolo}</span></p>", unsafe_allow_html=True)
            elif nome == "Ruído (%)":
                val = ruido[j]
                cor, simbolo = feedback(val, limite_ruido, "max")
                cols[j+1].markdown(f"<p style='text-align:center;'>{val:.3f} <span style='color:{cor}'>{simbolo}</span></p>", unsafe_allow_html=True)
            elif nome == "Uniformidade do Nº de TC":
                val = uniformidade[j]
                cor, simbolo = feedback(val, limite_uniform, "abs")
                cols[j+1].markdown(f"<p style='text-align:center;'>{val:.3f} <span style='color:{cor}'>{simbolo}</span></p>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)  # Fechar div de fundo

    # --- Espaçamento antes das observações ---
    st.markdown("<br>", unsafe_allow_html=True)

    # --- Seção de Observações ---
    st.markdown(
        """
        <div style='background-color:#ffffff; padding:15px; border-radius:10px'>
    """, unsafe_allow_html=True
    )
    st.subheader("Observações")
    st.text_area(
        "Imagem adquirida uniforme?",
        key="obs1_uniforme"
    )

    st.text_area(
        "Presença de Artefatos?",
        key="obs1_artefatos"
    )
    st.markdown("</div>", unsafe_allow_html=True)