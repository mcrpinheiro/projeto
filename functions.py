from fpdf import FPDF
from io import BytesIO

def pLista(registos, parametro):
    pL = []
    for registo in registos:
        pL.append(registo[parametro])
    return pL


def getDiaInt (registos, valor, parametro):
    for registo in registos:
        if registo[parametro] == valor:
            return registo["data"]
    print("Erro. Esse valor não foi encontrado na base de dados.")

#para parametros com mais de um valor
def getDiaStr (registos, valor, parametro):
    lista = []
    for registo in registos:
        if registo[parametro] == valor:
            lista.append(registo["data"])
    return lista

def listarValores(lista):
    if len(lista) == 0:
        return "."
    return ", ".join(str(x) for x in lista) + "."

def avaliar (registos):
        counterEv = 0
        listaEvolucao = pLista(registos, "evolucao")
        for parametro in listaEvolucao:
            if parametro == "positiva":
                counterEv+=1
        if counterEv >= len(listaEvolucao)/2:
            avaliacaoEv = "positiva"
        else:
            avaliacaoEv = "negativa"
        counterRi = 0
        listaRisco = pLista(registos, "risco")
        for parametro in listaRisco:
            if parametro == "baixo":
                counterRi+=1
        if counterRi >= len(listaRisco)/2:
            avaliacaoRi = "baixo"
        else:
            avaliacaoRi = "elevado"
        return " A evolução do paciente é, de uma forma geral, " + avaliacaoEv + " e existe um risco de complicações " + avaliacaoRi + "."


def gerar_relatorio_geral(registos):
    dorMax = (max(pLista(registos, "dor")))
    dorMin = (min(pLista(registos, "dor")))
    relatorio = "O paciente registou uma dor entre " + str(dorMin) + " e " + str(dorMax) + ", tendo atingido o máximo de dor no dia " + getDiaInt(registos,dorMax,"dor") + " e o mínimo no dia " + getDiaInt(registos,dorMin,"dor") + "."
    if pLista(registos, "febre") == []:
        relatorio.append("O paciente não registou febre.")
    else:
        diasFebre = getDiaStr(registos, True, "febre")
        if len(diasFebre) == 1:
            # Usamos [0] para pegar no primeiro item da lista e transformá-lo em texto
            febreRegistada = " O paciente registou febre no dia " + str(diasFebre[0]) + "."
        else:
            # Usamos a função listarValores para formatar várias datas
            febreRegistada = " O paciente registou febre nos dias " + listarValores(diasFebre)
        relatorio += febreRegistada
    relatorio += avaliar(registos)
    return relatorio

def gerar_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Adicionar um logótipo (se tiveres um ficheiro logo.png na pasta)
    pdf.image('logo.jpg', 10, 8, 33) 
    
    
    # Mudar a cor do título (RGB: Azul escuro médico)
    pdf.set_text_color(0, 51, 102)
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Relatório de Monitorização de Ferida", ln=True, align='C')
    
    pdf.ln(20) # Isto salta 20mm (2cm) para baixo, livrando o espaço do logo

    # Linha divisória
    pdf.line(10, 30, 200, 30)
    
    # Voltar à cor preta para o texto
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", size=12)

    # Assuming 'data' is a pandas Series
    for col, value in data.items():
        pdf.cell(0, 10, f"{col}: {value}", ln=True)

    # Output PDF as bytes
    pdf_bytes = pdf.output(dest='S').encode('latin1')  # 'S' = return as string
    return pdf_bytes
