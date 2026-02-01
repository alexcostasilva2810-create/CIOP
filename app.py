import streamlit as st
import requests
from datetime import datetime
from fpdf import FPDF # Nova biblioteca para o PDF
import io

# --- CONFIGURAÇÕES ---
NOTION_TOKEN = "ntn_KF635337593asvoK365BE8elugieK9vDsu88LJ2Xyk00yC"
DATABASE_ID = "2f9025de7b79802aa7d8e4711eff1ab6"
# Seu link do Make para o Gmail
MAKE_WEBHOOK_URL = "https://hook.us2.make.com/skp55xrn0n81u84ikog1czrvouj4f64l"

# --- FUNÇÃO PARA GERAR O PDF ---
def gerar_pdf_viagem(dados_mcp, dados_gerais):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "RELATORIO DE VIAGEM - LOGISTICA", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, f"E/M: {dados_gerais['empurrador']} | BTs/BGs: {dados_gerais['balsas']}", ln=True)
    pdf.cell(200, 10, f"Comandante: {dados_gerais['cmt']}", ln=True)
    pdf.cell(200, 10, f"Consumo Total: {dados_gerais['consumo']:,.2f} L", ln=True)
    pdf.cell(200, 10, f"Remanescente Chegada: {dados_gerais['saldo']:,.2f} L", ln=True)
    
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, "Detalhamento de Navegacao (MCP):", ln=True)
    pdf.set_font("Arial", size=10)
    
    for rpm, consumo in dados_mcp.items():
        if consumo > 0:
            pdf.cell(200, 8, f"- {rpm}: {consumo:,.2f} L", ln=True)
            
    return pdf.output(dest='S').encode('latin-1')

st.set_page_config(page_title="Cálculo de Consumo Marítimo", layout="wide")
st.title("🚢 Relatório de Viagem - Lógica de Queima")

with st.form("main_form"):
    # ... (Mantenha toda a sua lógica de inputs e cálculos exatamente como está) ...
    c1, c2 = st.columns(2)
    with c1:
        empurrador = st.selectbox("E/M", ["CUMARU", "SAMAUAMA", "JATOBA", "LUIZ FELIPE", "IPE", "AROEIRA", "ANGICO", "JACARANDA", "CAJERANA", "QUARUBA"])
        balsas = st.text_input("BT's/BG's", placeholder="Ex: GD XLI, GD XLII...")
    with c2:
        rem_saida = st.number_input("REMANESCENTE DE SAÍDA (L)", value=33761.25, format="%.2f")
        cmt = st.text_input("Comandante (CMT)")

    st.divider()
    st.subheader("📊 Navegação por RPM (MCP)")
    
    h_col, q_col, r_col = st.columns([2, 2, 2])
    h_col.write("**Horas Navegadas**")
    q_col.write("**Queima (L/H)**")
    r_col.write("**Subtotal Consumo**")

    rpms = ["1.200 RPM", "1.300 RPM", "1.400 RPM", "1.500 RPM", "1.600 RPM", "1.700 RPM", "1.800 RPM"]
    dados_mcp = {}

    for rpm in rpms:
        col_h, col_q, col_r = st.columns([2, 2, 2])
        default_h = 84.3 if "1.500" in rpm else (8.3 if "1.600" in rpm else 0.0)
        default_q = 231.0 if "1.500" in rpm else (270.5 if "1.600" in rpm else 0.0)
        horas = col_h.number_input(f"Horas {rpm}", min_value=0.0, value=default_h, format="%.1f", label_visibility="collapsed")
        queima = col_q.number_input(f"Queima {rpm}", min_value=0.0, value=default_q, format="%.1f", label_visibility="collapsed")
        subtotal = horas * queima
        col_r.write(f"**{subtotal:,.2f} L**")
        dados_mcp[rpm] = subtotal

    # ... (Seu cálculo de MCA e Finais) ...
    st.divider()
    mca_horas = st.number_input("MCA - Horas", value=92.8)
    mca_queima = st.number_input("MCA - Queima", value=6.5)
    consumo_mca = mca_horas * mca_queima
    consumo_final = sum(dados_mcp.values()) + consumo_mca
    saldo_final = rem_saida - consumo_final
    bloqueio = saldo_final < 0

    submit = st.form_submit_button("SALVAR E GERAR RELATÓRIO")

if submit:
    if bloqueio:
        st.error("Corrija os valores. O consumo não pode ser maior que o remanescente.")
    else:
        # 1. ENVIO NOTION (Seu código original)
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
        res_notion = requests.post("https://api.notion.com/v1/pages", 
                                   json=payload, 
                                   headers={"Authorization": f"Bearer {NOTION_TOKEN}", 
                                            "Notion-Version": "2022-06-28", "Content-Type": "application/json"})
        
        # 2. GERAÇÃO E ENVIO DO PDF PARA O GMAIL (MAKE)
        dados_gerais = {
            'empurrador': empurrador, 'balsas': balsas, 'cmt': cmt,
            'consumo': consumo_final, 'saldo': saldo_final
        }
        pdf_bytes = gerar_pdf_viagem(dados_mcp, dados_gerais)
        
        # Disparo para o Webhook com o arquivo PDF
        res_make = requests.post(MAKE_WEBHOOK_URL, files={"file": ("relatorio.pdf", pdf_bytes, "application/pdf")})
        
        if res_notion.status_code == 200 and res_make.status_code == 200:
            st.balloons()
            st.success("✅ Salvo no Notion e Relatório enviado por e-mail!")
        else:
            st.warning("Dados salvos, mas houve uma falha no envio do e-mail.")
