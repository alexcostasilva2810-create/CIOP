import streamlit as st
import requests
from datetime import datetime
from fpdf import FPDF
import io

# --- CONFIGURAÇÕES ---
NOTION_TOKEN = "ntn_KF635337593asvoK365BE8elugieK9vDsu88LJ2Xyk00yC"
DATABASE_ID = "2f9025de7b79802aa7d8e4711eff1ab6"
MAKE_WEBHOOK_URL = "https://hook.us2.make.com/skp55xrn0n81u84ikog1czrvouj4f64l"

def gerar_pdf_viagem(dados_mcp, dados_gerais):
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
    
    pdf.ln(5)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 7, f"CONSUMO TOTAL: {dados_gerais['consumo']:,.2f} L", ln=True)
    pdf.cell(0, 7, f"REMANESCENTE CHEGADA: {dados_gerais['saldo']:,.2f} L", ln=True)
    return pdf.output(dest='S').encode('latin-1')

st.set_page_config(page_title="Cálculo de Consumo Marítimo", layout="wide")
st.title("🚢 Relatório de Viagem - Lógica de Queima")

# --- FORMULÁRIO PRINCIPAL ---
with st.form("main_form"):
    c1, c2 = st.columns(2)
    with c1:
        empurrador = st.selectbox("E/M", ["CUMARU", "SAMAUAMA", "JATOBA", "LUIZ FELIPE", "IPE", "AROEIRA", "ANGICO", "JACARANDA", "CAJERANA", "QUARUBA"])
        balsas = st.text_input("BT's/BG's", placeholder="Ex: GD XLI, GD XLII...")
    with c2:
        rem_saida = st.number_input("REMANESCENTE DE SAÍDA (L)", value=33761.25, format="%.2f")
        cmt = st.text_input("Comandante (CMT)")

    st.divider()
    st.subheader("📊 Navegação por RPM (MCP)")
    
    rpms = ["1.200 RPM", "1.300 RPM", "1.400 RPM", "1.500 RPM", "1.600 RPM", "1.700 RPM", "1.800 RPM"]
    dados_mcp = {}
    consumo_total_mcp = 0.0

    # Tabela compacta com rótulos de RPM ao lado
    for rpm in rpms:
        col_label, col_h, col_q, col_res = st.columns([3, 2, 2, 2])
        
        col_label.write(f"**HORAS NAVEGADAS {rpm}:**")
        
        # Valores padrão para exemplo
        default_h = 84.3 if "1.500" in rpm else (8.3 if "1.600" in rpm else 0.0)
        default_q = 231.0 if "1.500" in rpm else (270.5 if "1.600" in rpm else 0.0)
        
        horas = col_h.number_input(f"h_{rpm}", min_value=0.0, value=default_h, format="%.1f", label_visibility="collapsed")
        queima = col_q.number_input(f"q_{rpm}", min_value=0.0, value=default_q, format="%.1f", label_visibility="collapsed")
        
        subtotal = horas * queima
        consumo_total_mcp += subtotal
        col_res.write(f"Subtotal: **{subtotal:,.2f} L**")
        
        dados_mcp[rpm] = {"horas": horas, "queima": queima, "subtotal": subtotal}

    st.divider()
    
    # MCA
    col_m1, col_m2, col_m3 = st.columns([3, 2, 4])
    col_m1.write("**MOTORES AUXILIARES (MCA):**")
    mca_h = col_m2.number_input("MCA Horas", value=92.8, label_visibility="collapsed")
    mca_q = col_m2.number_input("MCA Queima", value=6.5, label_visibility="collapsed")
    consumo_mca = mca_h * mca_q
    
    consumo_final = consumo_total_mcp + consumo_mca
    saldo_final = rem_saida - consumo_final

    # Resultados automáticos
    r1, r2 = st.columns(2)
    r1.metric("CONSUMO TOTAL", f"{consumo_final:,.2f} L")
    r2.metric("REMANESCENTE CHEGADA", f"{saldo_final:,.2f} L")

    submit = st.form_submit_button("FINALIZAR, SALVAR E ENVIAR E-MAIL")

if submit:
    # 1. Envio para o Notion (Código Original)
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
    
    # 2. Geração de PDF e Envio para Gmail (Make)
    dados_gerais = {'empurrador': empurrador, 'balsas': balsas, 'cmt': cmt, 'consumo': consumo_final, 'saldo': saldo_final}
    pdf_bytes = gerar_pdf_viagem(dados_mcp, dados_gerais)
    
    res_make = requests.post(MAKE_WEBHOOK_URL, files={"file": ("relatorio.pdf", pdf_bytes, "application/pdf")})
    
    if res_notion.status_code == 200 and res_make.status_code == 200:
        st.success("✅ Salvo no Notion e Relatório enviado por e-mail!")
        st.balloons()
