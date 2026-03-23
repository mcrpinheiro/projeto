import streamlit as st
import requests
import torch
from transformers import pipeline, BitsAndBytesConfig # Garante que 'pipeline' está aqui
from PIL import Image
import time
from datetime import datetime
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
from fpdf import FPDF
from io import BytesIO
import functions

@st.cache_resource
def load_medgemma():
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
    )

    return pipeline(
        "image-text-to-text",
        model="unsloth/medgemma-4b-it-bnb-4bit",
        quantization_config=bnb_config,
        device_map="auto",
        model_kwargs={"attn_implementation": "eager"} # Adiciona isto se o erro continuar
    )

pipe = load_medgemma()


if "historico" not in st.session_state:
    st.session_state.historico = []

st.title("Monitorização da Cicatrização - Protótipo")
# Sidebar menu
menu = st.sidebar.radio(
    "Menu",
    ["Home", "Análise", "Histórico", "Análise Geral", "Sobre", "FAQ"]
)

if menu == "Home":
    st.write("Bem-vindo ao protótipo de monitorização de feridas.")

elif menu == "Análise":
    st.write("Aqui você pode analisar a ferida.")
    area_px = st.number_input("Área (px)", value=1200.0)
    perimetro_px = st.number_input("Perímetro (px)", value=200.0)
    dor = st.slider("Dor (0-10)", 0, 10, 3)
    febre = st.checkbox("Febre", value=False)
    with st.form("image_form"):
        uploaded_image = st.file_uploader(
            "Escolha uma Imagem",
            type=["png", "jpg", "jpeg"]
        )

        submitted = st.form_submit_button("Submeter uma Imagem")
if st.button("Analisar ferida"):
        if uploaded_image is not None:
            image = Image.open(uploaded_image)
            st.image(image, caption="Imagem para análise", width=400)
            
            with st.spinner("A IA MedGemma está a analisar a imagem..."):
                # --- LÓGICA DO MEDGEMMA ---
                prompt_ia = (
                "Analisa esta imagem de ferida detalhadamente em PORTUGUÊS DE PORTUGAL. "
                "Identifica: tipos de tecido (granulação, esfacelo, necrose), "
                "sinais de infeção, tipo de exsudado e a condição da pele perilesional."
            )
                messages = [
                {"role": "system", "content": [{"type": "text", "text": "És um Especialista em Tratamento de Feridas e Estomaterapia."}]},
                {"role": "user", "content": [
                    {"type": "text", "text": prompt_ia},
                    {"type": "image", "image": image}
                ]}
            ]
                
                out = pipe(text=messages, max_new_tokens=1024, generate_kwargs = {"max_length": None})
                analise_ia = out[0]["generated_text"][-1]["content"]
                
                # --- TUA LÓGICA DE API EXISTENTE ---
                dados = {"area_px": area_px, "perimetro_px": perimetro_px, "dor": dor, "febre": febre}
                try:
                    # Se a tua API local estiver ativa:
                    resposta = requests.post("http://127.0.0.1:8000/analisar-ferida", json=dados)
                    resultado = resposta.json()
                except:
                    # Fallback caso a API não esteja ligada (para teste)
                    resultado = {"evolucao": "Estável", "risco": "Baixo", "comentario": "Análise manual."}

                # Exibir Resultados
                st.subheader("Resultado da Análise IA")
                st.info(analise_ia)
                
                st.subheader("Métricas de Evolução")
                st.write(f"Evolução: **{resultado['evolucao']}** | Risco: **{resultado['risco']}**")

                # GUARDAR NO HISTÓRICO (Incluindo a análise da IA)
                registo = {
                    "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "area": area_px,
                    "perimetro": perimetro_px,
                    "dor": dor,
                    "febre": febre,
                    "evolucao": resultado["evolucao"],
                    "risco": resultado["risco"],
                    "analise_ia": analise_ia  # <--- Nova coluna
                }
                st.session_state.historico.append(registo)
                st.success("Análise completa e guardada no histórico!")
        else:
            st.warning("Por favor, carregue uma imagem para a IA poder analisar.")
elif menu == "Histórico":
    st.write("Aqui pode consultar o histórico da evolução da sua ferida.")

    st.title("Histórico da Ferida")

    if len(st.session_state.historico) == 0:
        st.info("Ainda não existem análises guardadas.")

    else:

        df = pd.DataFrame(st.session_state.historico)

        # renomear colunas para ficar mais bonito
        df = df.rename(columns={
            "data": "Data",
            "area": "Área (px)",
            "perimetro": "Perímetro (px)",
            "dor": "Dor",
            "febre": "Febre",
            "evolucao": "Evolução",
            "risco": "Risco"
        })

        gb = GridOptionsBuilder.from_dataframe(df)

        gb.configure_selection("single")  # permite selecionar linha
        gb.configure_pagination(paginationAutoPageSize=True)

        gridOptions = gb.build()

        grid_response = AgGrid(
            df,
            gridOptions=gridOptions,
            height=300,
            width="100%"
        )
        selected = grid_response["selected_rows"]
        if selected is not None and len(selected) > 0:

            reg = selected.iloc[0]

            st.subheader("Relatório da análise")

            st.write("Data:", reg["Data"])
            st.write("Área:", reg["Área (px)"])
            st.write("Perímetro:", reg["Perímetro (px)"])
            st.write("Dor:", reg["Dor"])
            st.write("Febre:", reg["Febre"])
            st.write("Evolução:", reg["Evolução"])
            st.write("Risco:", reg["Risco"])
            st.markdown("### 🤖 Descrição da IA (MedGemma)")
            st.write(reg.get("analise_ia", "Nenhuma análise de IA disponível."))
            pdf = functions.gerar_pdf(reg)

            st.download_button(
            "📄 Exportar relatório em PDF",
            data=pdf,
            file_name="relatorio_ferida.pdf",
            mime="application/pdf"
            )

            
elif menu == "Análise Geral":
    st.subheader("📊 Painel de Evolução Clínica")
    
    if st.session_state.historico:
        # Converter para DataFrame e ordenar por data
        df_grafico = pd.DataFrame(st.session_state.historico)
        df_grafico['data'] = pd.to_datetime(df_grafico['data'], dayfirst=True)
        df_grafico = df_grafico.sort_values('data')

        # Criar colunas para os gráficos ficarem lado a lado
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Área da Ferida")
            # Usar line_chart para ver a evolução da área
            st.line_chart(df_grafico.set_index('data')['area'])

        with col2:
            st.markdown("### Nível de Dor")
            # Usar bar_chart para destacar os picos de dor
            st.bar_chart(df_grafico.set_index('data')['dor'])

        st.divider()
        st.write(functions.gerar_relatorio_geral(st.session_state.historico))
    else:
        st.info("Ainda não existem dados para gerar gráficos.")

elif menu == "Sobre":
    st.write("Aplicativo de exemplo para monitorização de feridas com Streamlit.")
elif menu == ("FAQ"):
    st.write("Respostas às perguntas mais comuns sobre a aplicação.")
    


# Num terminal separado, execute o servidor FastAPI com:
# uvicorn main:app --reload 


# Abrir no browser: http://127.0.0.1:8000/docs

# Abra o Streamlit num novo terminal:
# streamlit run app.py

#.\venv\Scripts\activate
#python -m uvicorn main:app --reload
#cd 'C:\Users\Utilizador\Desktop\PI\servidor_medgemma'
#python -m streamlit run app.py
#Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
