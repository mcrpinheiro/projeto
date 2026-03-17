from fpdf import FPDF
from io import BytesIO

def pLista(registos, parametro):
    pL = []
    for registo in registos:
        pL.append(registo[parametro])
    return pL

#para teste
registo1 = [{"data": '10-11',
                "area": 120,
                "perimetro": 120,
                "dor": 8,
                "febre": True,
                "evolucao": 'negativa',
                "risco": 'elevado'},
            {"data": '11-11',
                "area": 120,
                "perimetro": 120,
                "dor":9,
                "febre": True,
                "evolucao": 'positiva',
                "risco": 'baixo'},
            {"data": '12-11',
                "area": 120,
                "perimetro": 120,
                "dor":10,
                "febre": False,
                "evolucao": 'positiva',
                "risco": 'baixo'}]

#print(pLista(registo1, "data"))

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
            febreRegistada = " O paciente registou febre no dia" + diasFebre + "."
        else:
            febreRegistada = " O paciente registou febre nos dias " + listarValores(diasFebre)
        relatorio+= febreRegistada
    relatorio += avaliar(registos)
    return relatorio

#print(gerar_relatorio_geral(registo1))
def gerar_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Assuming 'data' is a pandas Series
    for col, value in data.items():
        pdf.cell(0, 10, f"{col}: {value}", ln=True)

    # Output PDF as bytes
    pdf_bytes = pdf.output(dest='S').encode('latin1')  # 'S' = return as string
    return pdf_bytes
