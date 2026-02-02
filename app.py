import streamlit as st
import requests
from datetime import datetime
from fpdf import FPDF
import io

# --- CONFIGURAÇÕES ---
NOTION_TOKEN = "ntn_KF635337593asvoK365BE8elugieK9vDsu88LJ2Xyk00yC"
DATABASE_ID = "2f9025de7b79802aa7d8e4711eff1ab6"
MAKE_WEBHOOK_URL = "https://hook.us2.make.com/skp55xrn0n81u84ikog1czrvouj4f64l"

# --- FUNÇÃO PDF ---
def gerar_pdf_viagem(dados_mcp, dados_gerais, consumo_mca):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, "RELATÓRIO FINAL DE VIAGEM", ln=True, align='C')
    pdf.ln(5)
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 7, f"E/M: {dados_gerais['empurrador']} | BTs/BGs: {dados_gerais['balsas']}", ln=True)
    pdf.cell(0, 7, f"Comandante: {dados_gerais['cmt']}", ln=True)
    pdf.ln(3)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 7, "DETALHAMENTO DE NAVEGAÇÃO (MCP):", ln=True)
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

# CSS para diminuir ainda mais o espaçamento entre colunas
st.markdown("""
    <style>
    [data-testid="column"] { padding: 0px 5px !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚢 Relatório de Viagem - Lógica de Queima")

# --- ENTRADA DE DADOS GERAIS ---
c1, c2, c3, c4 = st.columns([2, 2, 2, 2])
with c1:
    empurrador = st.selectbox("E/M", ["CUMARU", "SAMAUAMA", "JATOBA", "LUIZ FELIPE", "IPE", "AROEIRA", "ANGICO", "JACARANDA", "CAJERANA", "QUARUBA"])
with c2:
    balsas = st.text_input("BT's/BG's", placeholder="GD XLI...")
with c3:
    rem_saida = st.number_input("REM. SAÍDA (L)", value=33761.25, format="%.2f")
with c4:
    cmt = st.text_input("CMT (Comandante)")

st.divider()
st.subheader("📊 Navegação por RPM (MCP)")

# Cabeçalho da Tabela
h1, h2, h3, h4 = st.columns([3, 1.5, 1.5, 2.5])
h2.caption("Horas")
h3.caption("Queima")
h4.caption("Subtotal")

rpms = ["1.200 RPM", "1.300 RPM", "1.400 RPM", "1.500 RPM", "1.600 RPM", "1.700 RPM", "1.800 RPM"]
dados_mcp = {}
consumo_total_mcp = 0.0

for rpm in rpms:
    # Ajuste das proporções das colunas para aproximar os campos
    col_label, col_h, col_q, col_res = st.columns([3, 1.5, 1.5, 2.5])
    
    col_label.write(f"**HORAS NAVEGADAS {rpm}:**")
    
    def_h = 84.3 if "1.500" in rpm else (8.3 if "1.600" in rpm else 0.0)
    def_q = 231.0 if "1.500" in rpm else (270.5 if "1.600" in rpm else 0.0)
    
    horas = col_h.number_input(f"H_{rpm}", min_value=0.0, value=def_h, format="%.1f", label_visibility="collapsed")
    queima = col_q.number_input(f"Q_{rpm}", min_value=0.0, value=def_q, format="%.1f", label_visibility="collapsed")
    
    subtotal = horas * queima
    consumo_total_mcp += subtotal
    # Campo azul mais compacto
    col_res.info(f"{subtotal:,.2f} L")
    
    dados_mcp[rpm] = {"horas": horas, "queima": queima, "subtotal": subtotal}

st.divider()
# MCA mais compacto
cm1, cm2, cm3, cm4 = st.columns([3, 1.5, 1.5, 2.5])
cm1.write("**TOTAL MCA:**")
mca_h = cm2.number_input("MCA H", value=92.8, format="%.1f", label_visibility="collapsed")
mca_q = cm3.number_input("MCA Q", value=6.5, format="%.1f", label_visibility="collapsed")
consumo_mca = mca_h * mca_q
cm4.info(f"{consumo_mca:,.2f} L")

# Resultados Finais
consumo_final = consumo_total_mcp + consumo_mca
saldo_final = rem_saida - consumo_final

res1, res2 = st.columns(2)
res1.metric("CONSUMO TOTAL", f"{consumo_final:,.2f} L")
res2.metric("REMANESCENTE CHEGADA", f"{saldo_final:,.2f} L")

if st.button("FINALIZAR, SALVAR E ENVIAR RELATÓRIO"):
    pdf_bytes = gerar_pdf_viagem(dados_mcp, {'empurrador': empurrador, 'balsas': balsas, 'cmt': cmt, 'consumo': consumo_final, 'saldo': saldo_final}, consumo_mca)
    
    # Envio Notion
    payload = {"parent": {"database_id": DATABASE_ID}, "properties": {"EM": {"title": [{"text": {"content": f"{empurrador} | {balsas}"}}]}, "CMT": {"rich_text": [{"text": {"content": cmt}}]}, "Consumo Utilizado": {"number": round(consumo_final, 2)}, "DHOS": {"rich_text": [{"text": {"content": f"Saldo: {round(saldo_final, 2)}L"}}]}, "Data de Registro": {"date": {"start": datetime.now().isoformat()}}}}
    requests.post("https://api.notion.com/v1/pages", json=payload, headers={"Authorization": f"Bearer {NOTION_TOKEN}", "Notion-Version": "2022-06-28", "Content-Type": "application/json"})
    
    # Envio Make (Gmail)
    res_make = requests.post(MAKE_WEBHOOK_URL, files={"file": ("relatorio.pdf", pdf_bytes, "application/pdf")})
    
    if res_make.status_code == 200:
        st.success("✅ Relatório enviado!")
        st.balloons()
