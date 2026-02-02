import streamlit as st
import requests
from datetime import datetime
from fpdf import FPDF
import io

# --- CONFIGURAÇÕES ---
NOTION_TOKEN = "ntn_KF635337593asvoK365BE8elugieK9vDsu88LJ2Xyk00yC"
DATABASE_ID = "2f9025de7b79802aa7d8e4711eff1ab6"
MAKE_WEBHOOK_URL = "https://hook.us2.make.com/skp55xrn0n81u84ikog1czrvouj4f64l"

# --- FUNÇÃO PARA GERAR O PDF ---
def gerar_pdf_viagem(dados_mcp, dados_gerais, consumo_mca):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, "RELATORIO FINAL DE VIAGEM", ln=True, align='C')
    pdf.ln(5)
    
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 7, f"E/M: {dados_gerais['empurrador']} | BTs/BGs: {dados_gerais['balsas']}", ln=True)
    pdf.cell(0, 7, f"Comandante: {dados_gerais['cmt']}", ln=True)
    pdf.ln(3)
    
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 7, "DETALHAMENTO DE NAVEGACAO (MCP):", ln=True)
    pdf.set_font("Arial", size=9)
    for rpm, valor in dados_mcp.items():
        if valor['subtotal'] > 0:
            pdf.cell(0, 6, f"{rpm}: {valor['horas']}h x {valor['queima']}L/H = {valor['subtotal']:,.2f} L", ln=True)
    
    pdf.ln(3)
    pdf.cell(0, 7, f"CONSUMO MCA: {consumo_mca:,.2f} L", ln=True)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 7, f"CONSUMO TOTAL: {dados_gerais['consumo']:,.2f} L", ln=True)
    pdf.cell(0, 7, f"REMANESCENTE CHEGADA: {dados_gerais['saldo']:,.2f} L", ln=True)
    return pdf.output(dest='S').encode('latin-1')

st.set_page_config(page_title="Relatório de Viagem", layout="wide")
st.title("🚢 Relatório de Viagem - Lógica de Queima")

# --- ENTRADA DE DADOS GERAIS ---
with st.container():
    c1, c2 = st.columns(2)
    with c1:
        empurrador = st.selectbox("E/M", ["CUMARU", "SAMAUAMA", "JATOBA", "LUIZ FELIPE", "IPE", "AROEIRA", "ANGICO", "JACARANDA", "CAJERANA", "QUARUBA"])
        balsas = st.text_input("BT's/BG's", placeholder="Ex: GD XLI, GD XLII...")
    with c2:
        rem_saida = st.number_input("REMANESCENTE DE SAÍDA (L)", value=33761.25, format="%.2f")
        cmt = st.text_input("Comandante (CMT)")

st.divider()
st.subheader("📊 Navegação por RPM (MCP)")

# --- TABELA DE RPM COM CÁLCULO AUTOMÁTICO ---
rpms = ["1.200 RPM", "1.300 RPM", "1.400 RPM", "1.500 RPM", "1.600 RPM", "1.700 RPM", "1.800 RPM"]
dados_mcp = {}
consumo_total_mcp = 0.0

for rpm in rpms:
    # Criando as colunas conforme o seu desenho (Rótulo | Horas | Queima | Subtotal)
    col_label, col_h, col_q, col_res = st.columns([3, 2, 2, 2])
    
    col_label.write(f"**HORAS NAVEGADAS {rpm}:**")
    
    # Define valores padrão para teste
    def_h = 84.3 if "1.500" in rpm else (8.3 if "1.600" in rpm else 0.0)
    def_q = 231.0 if "1.500" in rpm else (270.5 if "1.600" in rpm else 0.0)
    
    # Campos de entrada (Retângulos para preencher)
    horas = col_h.number_input(f"H_{rpm}", min_value=0.0, value=def_h, format="%.1f", label_visibility="collapsed")
    queima = col_q.number_input(f"Q_{rpm}", min_value=0.0, value=def_q, format="%.1f", label_visibility="collapsed")
    
    # Cálculo automático (Aparece no último retângulo)
    subtotal = horas * queima
    consumo_total_mcp += subtotal
    col_res.info(f"Subtotal: {subtotal:,.2f} L")
    
    dados_mcp[rpm] = {"horas": horas, "queima": queima, "subtotal": subtotal}

st.divider()

# --- MOTORES AUXILIARES (MCA) ---
st.subheader("⚙️ Motores Auxiliares (MCA)")
cm1, cm2, cm3 = st.columns([3, 2, 4])
cm1.write("**TOTAL MCA:**")
mca_h = cm2.number_input("MCA Horas", value=92.8, format="%.1f")
mca_q = cm2.number_input("MCA Queima", value=6.5, format="%.1f")
consumo_mca = mca_h * mca_q
cm3.info(f"Consumo MCA: {consumo_mca:,.2f} L")

# --- RESULTADOS FINAIS ---
consumo_final = consumo_total_mcp + consumo_mca
saldo_final = rem_saida - consumo_final

res1, res2 = st.columns(2)
res1.metric("CONSUMO TOTAL", f"{consumo_final:,.2f} L")
res2.metric("REMANESCENTE CHEGADA", f"{saldo_final:,.2f} L")

# --- BOTÃO FINAL ---
if st.button("FINALIZAR, SALVAR E ENVIAR RELATÓRIO"):
    with st.spinner('Processando...'):
        # 1. Salvar no Notion
        payload = {
            "parent": {"database_id": DATABASE_ID},
            "properties": {
                "EM": {"title": [{"text": {"content": f"{empurrador} | {balsas}"}}]},
                "CMT": {"rich_text": [{"text": {"content": cmt}}]},
                "Consumo Utilizado": {"number": round(consumo_final, 2)},
                "DHOS": {"rich_text": [{"text": {"content": f"Saldo: {round(saldo_final, 2)}L"}}]},
                "Data de Registro": {"date": {"start": datetime.now().isoformat()}}
            }
        }
        res_notion = requests.post("https://api.notion.com/v1/pages", json=payload, 
                                   headers={"Authorization": f"Bearer {NOTION_TOKEN}", "Notion-Version": "2022-06-28", "Content-Type": "application/json"})
        
        # 2. Gerar PDF e enviar para Make (Gmail)
        dados_gerais = {'empurrador': empurrador, 'balsas': balsas, 'cmt': cmt, 'consumo': consumo_final, 'saldo': saldo_final}
        pdf_bytes = gerar_pdf_viagem(dados_mcp, dados_gerais, consumo_mca)
        
        res_make = requests.post(MAKE_WEBHOOK_URL, files={"file": ("relatorio.pdf", pdf_bytes, "application/pdf")})
        
        if res_notion.status_code == 200 and res_make.status_code == 200:
            st.success("✅ Salvo no Notion e Enviado com sucesso!")
            st.balloons()
