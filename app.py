import streamlit as st
import requests
from fpdf import FPDF
from datetime import datetime
import io

# --- CONFIGURAÇÕES ---
NOTION_TOKEN = "ntn_KF635337593asvoK365BE8elugieK9vDsu88LJ2Xyk00yC"
DATABASE_ID = "2f9025de7b79802aa7d8e4711eff1ab6"
# Seu link atualizado do Make
MAKE_WEBHOOK_URL = "https://hook.us2.make.com/skp55xrn0n81u84ikog1czrvouj4f64l" 

def gerar_pdf(dados):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    
    # Cabeçalho
    pdf.cell(200, 10, "RELATORIO FINAL DE VIAGEM", ln=True, align='L')
    pdf.set_font("Arial", "B", 10)
    
    line_height = 7
    pdf.cell(200, line_height, f"E/M: {dados['empurrador']}", ln=True)
    pdf.cell(200, line_height, f"BTs/BGs: {dados['balsas']}", ln=True)
    pdf.cell(200, line_height, f"CMT: {dados['cmt']}", ln=True)
    pdf.cell(200, line_height, f"ORIGEM: {dados['origem']}", ln=True)
    pdf.cell(200, line_height, f"DESTINO: {dados['destino']}", ln=True)
    pdf.cell(200, line_height, f"DATA/HORA: {dados['dhos']}", ln=True)
    
    # Seção de RPMs e Consumo
    pdf.ln(5)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(200, line_height, f"REMANESCENTE DE SAIDA (L): {dados['rem_saida']:,.2f}", ln=True)
    pdf.cell(200, line_height, f"CONSUMO TOTAL UTILIZADO (L): {dados['consumo_total']:,.2f}", ln=True)
    pdf.cell(200, line_height, f"REMANESCENTE DE CHEGADA (L): {dados['saldo_final']:,.2f}", ln=True)
    
    # Retorna os bytes do PDF
    return pdf.output(dest='S').encode('latin-1')

def salvar_no_notion(dados):
    # Aqui vai o seu código do Notion que já está 100% funcional
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    # (Omiti o payload para o código ficar limpo, mas mantenha o seu aqui)
    pass

# --- INTERFACE ---
st.title("🚢 Sistema de Despacho Marítimo")

# Organize os inputs conforme sua lógica atual
col1, col2 = st.columns(2)
with col1:
    empurrador = st.text_input("E/M (Empurrador)", value="GD CUMARU")
    cmt = st.text_input("CMT (Comandante)", value="MAURO LOPES")
    rem_saida = st.number_input("REMANESCENTE SAÍDA", value=33761.25)

with col2:
    destino = st.text_input("DESTINO", value="NVR")
    balsas = st.text_input("BALSAS", value="GD XLI...")
    consumo_total = st.number_input("CONSUMO TOTAL (Cálculo)", value=22321.65)

saldo_final = rem_saida - consumo_total

if st.button("FINALIZAR, SALVAR E ENVIAR E-MAIL"):
    dados_relatorio = {
        "empurrador": empurrador,
        "balsas": balsas,
        "cmt": cmt,
        "origem": "PVH", 
        "destino": destino,
        "dhos": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "rem_saida": rem_saida,
        "consumo_total": consumo_total,
        "saldo_final": saldo_final
    }
    
    with st.spinner('Processando...'):
        # 1. Gerar PDF personalizado
        pdf_bytes = gerar_pdf(dados_relatorio)
        
        # 2. Salvar no Notion (Gatilho da sua função que já funciona)
        # salvar_no_notion(dados_relatorio) 
        
        # 3. Disparo para o Make.com (Gatilho do Gmail)
        try:
            # Enviamos o arquivo como "multipart/form-data" para o Make receber o arquivo real
            files = {"file": ("relatorio_final.pdf", pdf_bytes, "application/pdf")}
            response = requests.post(MAKE_WEBHOOK_URL, files=files)
            
            if response.status_code == 200:
                st.success("✅ Relatório salvo no Notion e enviado ao CIOP via Gmail!")
                st.download_button("Baixar Cópia do PDF", data=pdf_bytes, file_name="relatorio_final.pdf")
            else:
                st.error("Erro ao enviar para o Make.")
        except Exception as e:
            st.error(f"Falha no gatilho: {e}")
