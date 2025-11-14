import streamlit as st

def app():
    st.title("Preparação e Avaliação dos Testes de Qualidade Semanal")
    st.markdown("""
    Este guia fornece instruções detalhadas sobre a execução dos testes semanais, assegurando a padronização dos procedimentos e a confiabilidade dos resultados.
    """)

    # Etapas do guia
    etapas = [
        "Posicionamento do Objeto Simulador",
        "Avaliação do Posicionamento",
        "Aquisição Crânio-Água",
        "Aquisição Abdômen-Água",
        "Aquisição - Ar",
        "Avaliação dos Resultados",
        "Conclusão e armazenamento dos dados"
    ]

    # Estado da etapa atual
    if "etapa_atual" not in st.session_state:
        st.session_state.etapa_atual = 0

    etapa = st.session_state.etapa_atual
    st.divider()
    st.subheader(f" Passo {etapa + 1}: {etapas[etapa]}")

    # Layout com texto e imagem lado a lado
    col_texto, col_figura = st.columns([2, 1], vertical_alignment="center")

    # Etapa 1
    if etapa == 0:
        with col_texto:
            st.markdown("""
            **Objetivo:** Garantir o posicionamento correto do fantoma antes de iniciar a coleta das imagens.

            1) Retire o suporte de crânio e insira o suporte do fantoma na mesa de tomografia.  
            2) Posicione o fantoma sobre o seu suporte, no centro do plano tomográfico, com o auxílio dos lasers de posicionamento. 
            3) Confirme que o fantoma está estável e fixo no suporte, evitando qualquer movimento durante a coleta das imagens. 
            4) Após inserir o fantoma no gantry, zere o sistema de posicionamento para marcar o ponto de início da irradiação.
                        
            """)
        with col_figura:
            st.image("01.png", use_container_width=True)
            st.caption("Figura 1: Alinhamento do fantoma com base nas indicações dos lasers.")

    # Etapa 2
    elif etapa == 1:
        with col_texto:
            st.markdown("""
            **Objetivo:** Confirmar que o fantoma está corretamente posicionado.

            1) Adquirir uma imagem no modo axial para verificar se o posicionamento está correto.  
            2) O centro da imagem do fantoma deve coincidir com o centro do plano tomográfico.  
            
            """)
        with col_figura:
            st.image("02.png", use_container_width=True)
            st.caption("Figura 2: Imagem obtida do fantoma irradiado.")

    # Etapa 3
    elif etapa == 2:
        with col_texto:
            st.markdown("""
            **Objetivo:** Garantir que o protocolo de aquisição esteja configurado para Crânio-Água.

            1) Selecionar o protocolo de Crânio Rotina.   
            2) Selecione o estudo na região de Crânio-Água.
            3) Configurar o modo de aquisição para Axial.
            4) Realizar a exposição.    
            """)
        with col_figura:
            st.image("03.png", use_container_width=True)
            st.caption("Figura 3: Região de interesse para a região de Crânio-Água.")

        # Etapa 4
    elif etapa == 3:
        with col_texto:
            st.markdown("""
            **Objetivo:** Garantir que os protocolos de aquisição estejam configurados para Abdômen-Água.

            1) Selecionar o protocolo de Abdômen Rotina.
            2) Selecione o estudo na região de Abdômen-Água.
            3) Configurar o modo de aquisição para Axial.
            4) Realizar a exposição.    
            """)
        with col_figura:
            st.image("04.png", use_container_width=True)
            st.caption("Figura 4: Região de interesse para a região de Abdômen-Água.")

    # Etapa 5
    elif etapa == 4:
        with col_texto:
            st.markdown("""
            **Objetivo:** Garantir que os protocolos de aquisição estejam configurados para o ar.

            1) Selecionar o protocolo de Crânio Rotina.   
            2) Selecione os estudos na região de Crânio-Ar.
            3) Selecionar o protocolo de Abdômen Rotina.
            4) Selecione os estudos na região de Abdômen-Ar.
            5) Perceba que as duas regiões se sobrepõem - Figura 4.
            5) Realizar a exposição dos estudos. 
            6) Finalizar o estudo e salvar as imagens no PACS. 
            """)
        with col_figura:
            st.image("05.png", use_container_width=True)
            st.caption("Figura 5: Regiões de interesse para a região de ar.")

    # Etapa 6
    elif etapa == 5:
        with col_texto:
            st.markdown("""
            **Objetivo:** Avaliar a qualidade das imagens obtidas.

            1) No menu lateral, selecione a opção "Qualidade da Imagem".
            2) Clique em "Browse files" para acessar os arquivos.
            3) Baixe as imagens adquiridas e escolha a imagem central das regiões analisadas.
            4) Avalie os parâmetros de Uniformidade, Ruído e Resolução Espacial.
            5) O sistema indicará, na parte inferior da tela, se a qualidade da imagem foi aprovada ou reprovada.
            6) Baixe o relatório do teste em PDF.

            """)
        with col_figura:
            st.image("06.png", use_container_width=True)
            st.caption("Figura 6: Selecione 'Browse files' e baixe as imagens para serem analisadas.")

    # Etapa 7
    elif etapa == 6:
        with col_texto:
            st.markdown("""
            **Objetivo:** Concluir o procedimento e organizar os itens utilizados.

            1) Verificar se todas as informações e imagens foram corretamente armazenadas.   
            2) Armazenar o fantoma e os acessórios em um local seguro e adequado.   
            
            """)
        with col_figura:
            st.image("07.png", use_container_width=True)
            st.caption("")


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
