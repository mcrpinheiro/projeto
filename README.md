# Aplicação de Monitorização de Cicatrização

Esta aplicação permite acompanhar e analisar o processo de cicatrização de forma simples e eficiente.

## Como Executar a Aplicação

A aplicação é composta por duas partes:
- Servidor (backend) – responsável pelo processamento
- Interface (frontend) – onde o utilizador interage

---

## 1. Abrir o Servidor (O Cérebro)

1. Abre o terminal (ou VS Code) na pasta do projeto: 
2. Executa o seguinte comando: python -m uvicorn main:app --reload
3. Mantém esta janela aberta. Se a fechares, a aplicação deixa de funcionar.

## 2. Abrir a Interface (O Rosto)
1. Abre um segundo terminal (sem fechar o primeiro).
2. Garante que estás na mesma pasta (`\app`).
3. Executa o seguinte comando: python -m streamlit run app.py


