# o main.py é o servidor FastAPI que processa os pedidos da app Streamlit (app.py).
# Ele tem um endpoint "/analisar-ferida" que recebe os dados da app, chama a função "medgemma_analisa" (que é uma simulação do modelo MedGemma) e devolve a resposta estruturada.

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Modelo dos dados que a app vai enviar (podes ajustar depois)
class PedidoAnalise(BaseModel):
    area_px: float
    perimetro_px: float
    dor: int          # 0 a 10
    febre: bool       # True / False


# --- FASE 3: função "falsa" que representa o MedGemma ---
def medgemma_analisa(area_px: float, perimetro_px: float, dor: int, febre: bool) -> str:
    """
    Por enquanto esta função NÃO usa IA.
    Apenas devolve um texto de exemplo, com base em regras simples.
    Mais tarde vamos trocar o interior desta função pelo modelo MedGemma real.
    """
    if febre or dor >= 7:
        return "A evolução parece negativa, com risco elevado de complicações."
    else:
        return "A evolução parece positiva, com risco baixo de complicações."


# --- Funções para extrair evolução, risco e comentário do texto ---
def extrair_evolucao(texto: str) -> str:
    if "negativa" in texto:
        return "negativa"
    return "positiva"


def extrair_risco(texto: str) -> str:
    if "elevado" in texto:
        return "elevado"
    return "baixo"


def extrair_comentario(texto: str) -> str:
    # Por agora o comentário é simplesmente o próprio texto
    return texto


# Endpoint (já com as 4 fases simplificadas)
@app.post("/analisar-ferida")
def analisar_ferida(pedido: PedidoAnalise):
    # Fase 1: receção dos dados
    dados = pedido

    # Fase 2 + 3: preparar e chamar o "MedGemma"
    texto_resposta = medgemma_analisa(
        area_px=dados.area_px,
        perimetro_px=dados.perimetro_px,
        dor=dados.dor,
        febre=dados.febre,
    )

    # Fase 4: transformar a resposta em campos estruturados
    evolucao = extrair_evolucao(texto_resposta)
    risco = extrair_risco(texto_resposta)
    comentario = extrair_comentario(texto_resposta)

    return {
        "evolucao": evolucao,
        "risco": risco,
        "comentario": comentario,
    }

