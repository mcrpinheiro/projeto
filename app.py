import streamlit as st
import requests
from datetime import datetime
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
from fpdf import FPDF
from io import BytesIO
import functions


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

        if submitted:
            if uploaded_image is not None:
                st.image(uploaded_image, caption="Uploaded Image", width="stretch")
                st.success("Imagem submetida com sucesso!")
            else:
                st.warning("Por favor escolha uma imagem.")
    if st.button("Analisar ferida"):
        dados = {
            "area_px": area_px,
            "perimetro_px": perimetro_px,
            "dor": dor,
            "febre": febre
        }

        resposta = requests.post("http://127.0.0.1:8000/analisar-ferida", json=dados)
        resultado = resposta.json()

        st.subheader("Resultado")
        st.write(f"Evolução: **{resultado['evolucao']}**")
        st.write(f"Risco: **{resultado['risco']}**")
        st.write(f"Comentário: {resultado['comentario']}")
        # guardar no histórico
        registo = {
            "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "area": area_px,
            "perimetro": perimetro_px,
            "dor": dor,
            "febre": febre,
            "evolucao": resultado["evolucao"],
            "risco": resultado["risco"]
        }

        st.session_state.historico.append(registo)
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
            pdf = functions.gerar_pdf(reg)

            st.download_button(
            "📄 Exportar relatório em PDF",
            data=pdf,
            file_name="relatorio_ferida.pdf",
            mime="application/pdf"
            )
elif menu == "Análise Geral":
    if st.session_state.historico:
        st.write(functions.gerar_relatorio_geral(st.session_state.historico))
    else:
        st.write("Ainda não foram registados sintomas.")
elif menu == "Sobre":
    st.write("Aplicativo de exemplo para monitorização de feridas com Streamlit.")
elif menu == ("FAQ"):
    st.write("Respostas às perguntas mais comuns sobre a aplicação.")
    


# Num terminal separado, execute o servidor FastAPI com:
# uvicorn main:app --reload 


# Abrir no browser: http://127.0.0.1:8000/docs

# Abra o Streamlit num novo terminal:
# streamlit run app.py


#python -m uvicorn main:app --reload
#cd 'C:\Users\Utilizador\Desktop\PI\servidor_medgemma'
#python -m streamlit run app.py
