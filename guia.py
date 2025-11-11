import streamlit as st

def app():
    st.title("Guia Interativo – Teste Semanal de Tomografia")
    st.markdown("""
    Este guia tem como objetivo orientar passo a passo a realização do **teste semanal de tomografia computadorizada**, 
    garantindo a padronização e a qualidade dos procedimentos realizados.
    """)

    # Etapas do guia
    etapas = [
        "Preparação do ambiente e do equipamento",
        "Verificação do fantoma e acessórios",
        "Configuração dos parâmetros de aquisição",
        "Realização das imagens de teste",
        "Avaliação visual e quantitativa das imagens",
        "Registro dos resultados e análise das doses",
        "Conclusão e armazenamento dos dados"
    ]

    # Inicializa o estado da etapa atual
    if "etapa_atual" not in st.session_state:
        st.session_state.etapa_atual = 0

    etapa = st.session_state.etapa_atual

    st.subheader(f"Passo {etapa + 1}: {etapas[etapa]}")

    # Conteúdo de cada etapa (exemplo inicial)
    if etapa == 0:
        st.markdown("""
        - Certifique-se de que a sala está limpa e organizada.  
        - Verifique se o tomógrafo está ligado e pronto para uso.  
        - Confirme que não há alarmes ou erros no painel do equipamento.  
        """)
    elif etapa == 1:
        st.markdown("""
        - Pegue o **fantoma padrão de qualidade** e verifique se não há rachaduras ou sujeiras.  
        - Posicione o fantoma corretamente no suporte.  
        - Utilize os acessórios necessários conforme o protocolo do fabricante.  
        """)
    elif etapa == 2:
        st.markdown("""
        - Configure os parâmetros técnicos conforme o protocolo estabelecido:  
          - kV e mAs padrão;  
          - espessura de corte;  
          - modo de reconstrução;  
          - número de imagens.  
        - Garanta que o paciente simulado (fantoma) esteja centralizado.  
        """)
    elif etapa == 3:
        st.markdown("""
        - Realize a aquisição das imagens de teste.  
        - Verifique visualmente se não há artefatos.  
        - Salve as imagens no PACS ou diretório destinado à análise.  
        """)
    elif etapa == 4:
        st.markdown("""
        - Avalie a uniformidade, ruído e resolução das imagens.  
        - Compare os valores obtidos com os limites de aceitação.  
        - Documente eventuais desvios.  
        """)
    elif etapa == 5:
        st.markdown("""
        - Registre as doses medidas (CTDIvol e DLP) no sistema de controle de qualidade.  
        - Analise a consistência com os testes anteriores.  
        - Gere gráficos de acompanhamento se disponível.  
        """)
    elif etapa == 6:
        st.markdown("""
        - Confirme que todas as informações foram salvas corretamente.  
        - Assine digitalmente (se aplicável).  
        - Guarde o fantoma e acessórios adequadamente.  
        - Teste semanal finalizado com sucesso ✅  
        """)

    # Botões de navegação
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if etapa > 0:
            if st.button("⬅️ Voltar"):
                st.session_state.etapa_atual -= 1
    with col3:
        if etapa < len(etapas) - 1:
            if st.button("Próximo ➡️"):
                st.session_state.etapa_atual += 1
