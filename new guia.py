import streamlit as st

def app():
    st.title("📘 Guia de Usuário – Teste Semanal de Tomografia")
    st.markdown("""
    Este guia tem como objetivo orientar passo a passo a realização do **teste semanal de tomografia computadorizada**, 
    garantindo a padronização e a qualidade dos procedimentos realizados e das medições de dose.
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

    # Estado da etapa atual
    if "etapa_atual" not in st.session_state:
        st.session_state.etapa_atual = 0

    etapa = st.session_state.etapa_atual
    st.divider()
    st.subheader(f"🔹 Passo {etapa + 1}: {etapas[etapa]}")

    # Layout com texto e imagem lado a lado
    col_texto, col_figura = st.columns([2, 1], vertical_alignment="center")

    # Etapa 1
    if etapa == 0:
        with col_texto:
            st.markdown("""
            **Objetivo:** Garantir que o equipamento e o ambiente estejam prontos para o teste.

            - Confirmar que o tomógrafo está ligado e em condições normais de operação.  
            - Verificar se o ambiente está livre de interferências e com as portas trancadas.  
            - Posicionar o fantoma sobre a mesa, no centro do plano tomográfico, com o auxílio dos lasers de posicionamento.  
            - Adquirir uma imagem no modo axial para verificar se o posicionamento está correto.  
              - NOTA: O centro da imagem do fantoma deve coincidir com o centro do plano tomográfico.  
            """)
        with col_figura:
            st.image("imagens/figura1.png", use_container_width=True)
            st.caption("Figura 1 – Posicionamento correto do fantoma no centro do plano tomográfico.")

    # Etapa 2
    elif etapa == 1:
        with col_texto:
            st.markdown("""
            **Objetivo:** Assegurar que o fantoma está limpo, completo e pronto para uso.

            - Verificar se o fantoma não apresenta rachaduras, bolhas ou sujeira nas superfícies.  
            - Conferir se todos os módulos estão presentes e montados corretamente.  
            - Certificar-se de que todos os acessórios necessários estão disponíveis 
              (anéis, adaptadores, suporte, fita de fixação etc.).  
            """)
        with col_figura:
            st.image("imagens/figura2.png", use_container_width=True)
            st.caption("Figura 2 – Inspeção e montagem correta do fantoma.")

    # Etapa 3
    elif etapa == 2:
        with col_texto:
            st.markdown("""
            **Objetivo:** Garantir que os protocolos de aquisição estejam configurados corretamente.

            - Selecionar os protocolos de Crânio Rotina e Abdômen Rotina no equipamento.  
            - Configurar o modo de aquisição para Axial.  
            - Realizar a exposição de cada módulo.  
              - Todas as medições devem ser realizadas no corte central, exceto na avaliação de artefatos, 
                em que todos os cortes obtidos devem ser analisados.  
            """)
        with col_figura:
            st.image("imagens/figura3.png", use_container_width=True)
            st.caption("Figura 3 – Configuração dos protocolos de aquisição no console do tomógrafo.")

    # Etapa 4
    elif etapa == 3:
        with col_texto:
            st.markdown("""
            **Objetivo:** Coletar as imagens de forma adequada para análise.

            - Verificar visualmente se não há artefatos significativos nas imagens.  
            - Caso haja artefatos que comprometam a imagem, interromper o teste e acionar o serviço de manutenção.  
            - Se não houver artefatos, salvar as imagens no PACS.  
            - Fazer o download das imagens no computador local para análise posterior.  
            """)
        with col_figura:
            st.image("imagens/figura4.png", use_container_width=True)
            st.caption("Figura 4 – Exemplo de artefato de imagem a ser identificado.")

    # Etapa 5
    elif etapa == 4:
        with col_texto:
            st.markdown("""
            **Objetivo:** Avaliar a qualidade das imagens obtidas.

            - Abrir o aplicativo **“Semanal TC”**. 
            - Entrar na opção "Qualidade da Imagem".
            - Selecionar as imagens adquiridas.  
            - Avaliar os parâmetros de Uniformidade, Ruído e Resolução ESpacial.
            - Se estiver todos "dentro", seignifica que o teste foi aprovado. 
            """)
        with col_figura:
            st.image("imagens/figura5.png", use_container_width=True)
            st.caption("Figura 5 – Distribuição das ROIs no módulo de uniformidade.")

    # Etapa 6
    elif etapa == 5:
        with col_texto:
            st.markdown("""
            **Objetivo:** Garantir a rastreabilidade dos resultados e acompanhar a estabilidade das doses.

            - Analisar os valores de CTDIvol e DLP para cada protocolo. 
            - Exportar os dados em formato Excel para geração de gráficos de acompanhamento.   
            - Comparar os resultados com os testes anteriores para verificar estabilidade.  
            """)
        with col_figura:
            st.image("imagens/figura6.png", use_container_width=True)
            st.caption("Figura 6 – Exemplo de gráfico de tendência de dose semanal.")

    # Etapa 7
    elif etapa == 6:
        with col_texto:
            st.markdown("""
            **Objetivo:** Encerrar o procedimento e organizar o material.

            - Confirmar que todas as informações e imagens foram salvas corretamente.   
            - Armazenar o fantoma e os acessórios em local adequado e protegido.   
            
            ✅ **Teste semanal finalizado com sucesso!**
            """)
        with col_figura:
            st.image("imagens/figura7.png", use_container_width=True)
            st.caption("Figura 7 – Armazenamento adequado do fantoma após o uso.")

    st.divider()

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
