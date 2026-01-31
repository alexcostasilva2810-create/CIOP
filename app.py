import streamlit as st
import requests
from fpdf import FPDF
from datetime import datetime
import io

# --- CONFIGURAÇÕES ---
NOTION_TOKEN = "ntn_KF635337593asvoK365BE8elugieK9vDsu88LJ2Xyk00yC"
DATABASE_ID = "2f9025de7b79802aa7d8e4711eff1ab6"
MAKE_WEBHOOK_URL = "SUA_URL_DO_MAKE_AQUI" # Para o WhatsApp

def gerar_pdf(dados):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    
    # Cabeçalho
    pdf.cell(200, 10, "⛵ RELATÓRIO FINAL DE VIAGEM", ln=True, align='L')
    pdf.set_font("Arial", "B", 10)
    
    line_height = 7
    pdf.cell(200, line_height, f"E/M: {dados['empurrador']}", ln=True)
    pdf.cell(200, line_height, f"BT's/BG'S: {dados['balsas']}", ln=True)
    pdf.cell(200, line_height, f"CMT: {dados['cmt']}", ln=True)
    pdf.cell(200, line_height, f"ORIGEM: {dados['origem']}", ln=True)
    pdf.cell(200, line_height, f"DESTINO: {dados['destino']}", ln=True)
    pdf.cell(200, line_height, f"DHOS: {dados['dhos']}", ln=True)
    
    # Seção de RPMs
    pdf.ln(5)
    for rpm, valor in dados['rpms'].items():
        if valor['horas'] > 0:
            pdf.cell(200, line_height, f"HORAS NAVEGADAS {rpm}: {valor['horas']} ({valor['queima']} L/H)", ln=True)
    
    # Totais
    pdf.ln(5)
    pdf.cell(200, line_height, f"REMANESCENTE DE SAÍDA (L): {dados['rem_saida']:,.2f}", ln=True)
    pdf.cell(200, line_height, f"CONSUMO UTILIZADO (L): {dados['consumo_total']:,.2f}", ln=True)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(200, line_height, f"REMANESCENTE DE CHEGADA (L): {dados['saldo_final']:,.2f}", ln=True)
    
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFACE (Mesma lógica de cálculo anterior) ---
st.title("🚢 Sistema de Despacho Marítimo")

# ... (Mantenha aqui os inputs de RPM e MCA que fizemos no passo anterior) ...
# [Simulando inputs para brevidade do exemplo]
rem_saida = st.number_input("REMANESCENTE SAÍDA", value=33761.25)
# ... campos de horas e queima ...

# Cálculo final (Exemplo simplificado para o botão)
consumo_total = 22321.65 # Resultado da sua lógica
saldo_final = rem_saida - consumo_total

if st.button("FINALIZAR, SALVAR E ENVIAR WHATSAPP"):
    dados_relatorio = {
        "empurrador": "GD CUMARU", "balsas": "GD XLI...", "cmt": "MAURO LOPES",
        "origem": "PVH", "destino": "NVR", "dhos": "26/01 18:00",
        "rem_saida": rem_saida, "consumo_total": consumo_total, "saldo_final": saldo_final,
        "rpms": {"1.500 RPM": {"horas": 84.3, "queima": 231.0}} # Exemplo
    }
    
    # 1. Gerar PDF
    pdf_bytes = gerar_pdf(dados_relatorio)
    
    # 2. Salvar no Notion (código que já fizemos)
    
    # 3. Enviar para o WhatsApp via Make.com
    # O Make recebe o PDF e envia para o grupo automaticamente
    requests.post(MAKE_WEBHOOK_URL, files={"file": ("relatorio.pdf", pdf_bytes)})
    
    st.success("✅ Processo Completo! PDF enviado para OPERAÇÕES & LOGÍSTICA.")
    st.download_button("Baixar Cópia do PDF", data=pdf_bytes, file_name="relatorio.pdf")
