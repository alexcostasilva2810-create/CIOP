import streamlit as st
import requests
from fpdf import FPDF
from datetime import datetime
import io

# --- CONFIGURAÇÕES ---
NOTION_TOKEN = "ntn_KF635337593asvoK365BE8elugieK9vDsu88LJ2Xyk00yC"
DATABASE_ID = "2f9025de7b79802aa7d8e4711eff1ab6"
MAKE_WEBHOOK_URL = "https://hook.us2.make.com/s8hhow6yr7dxk7pzx4ivo74zatyjhktb"

st.set_page_config(page_title="Sistema de Despacho Marítimo", layout="wide")

# --- FUNÇÃO GERADORA DE PDF ---
def gerar_pdf(dados):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)
    
    # Cabeçalho baseado na imagem do usuário
    pdf.cell(200, 8, "⛵ RELATÓRIO FINAL DE VIAGEM", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(200, 7, f"E/M: {dados['empurrador']}", ln=True)
    pdf.cell(200, 7, f"BT's/BG'S: {dados['balsas']}", ln=True)
    pdf.cell(200, 7, f"CMT: {dados['cmt']}", ln=True)
    pdf.cell(200, 7, f"CHM: {dados['chm']}", ln=True)
    pdf.cell(200, 7, f"ORIGEM: {dados['origem']} | DESTINO: {dados['destino']}", ln=True)
    pdf.cell(200, 7, f"DHOS: {dados['dhos']} | DHOC: {dados['dhoc']}", ln=True)
    
    pdf.ln(5)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(200, 7, "DETALHAMENTO DE NAVEGAÇÃO E CONSUMO:", ln=True)
    pdf.set_font("Arial", "", 10)
    
    # Listagem de RPMs
    for rpm, info in dados['rpms'].items():
        if info['horas'] > 0:
            pdf.cell(200, 6, f"HORAS NAVEGADAS {rpm}: {info['horas']}h (Queima: {info['queima']} L/H)", ln=True)
    
    pdf.cell(200, 6, f"MCA: {dados['mca_h']}h (Queima: {dados['mca_q']} L/H)", ln=True)
    
    pdf.ln(5)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(200, 7, f"REMANESCENTE DE SAÍDA (L): {dados['rem_saida']:,.2f}", ln=True)
    pdf.cell(200, 7, f"CONSUMO UTILIZADO (L): {dados['consumo_total']:,.2f}", ln=True)
    pdf.cell(200, 7, f"REMANESCENTE DE CHEGADA (L): {dados['saldo_final']:,.2f}", ln=True)
    
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFACE STREAMLIT ---
st.title("🚢 Registro de Viagem e Consumo")

with st.form("form_viagem"):
    col1, col2 = st.columns(2)
    with col1:
        # Dropdown conforme solicitado
        empurrador = st.selectbox("E/M (Empurrador)", ["CUMARU", "SAMAUAMA", "JATOBA", "LUIZ FELIPE", "IPE", "AROEIRA", "ANGICO", "JACARANDA", "CAJERANA", "QUARUBA"])
        balsas = st.text_area("BT's/BG'S", value="GD XLI, GD XLII, GD XVII...")
        cmt = st.text_input("CMT", value="MAURO LOPES")
        chm = st.text_input("CHM", value="RAPHAEL DE JESUS")
        origem = st.text_input("Origem", value="PVH")
        destino = st.text_input("Destino", value="NVR")
        dhos = st.text_input("DHOS (Saída)", value="26/01 18:00")
        dhoc = st.text_input("DHOC (Chegada)", value="30/01 13:30")
    
    with col2:
        rem_saida = st.number_input("REMANESCENTE DE SAÍDA (L)", value=33761.25, format="%.2f")
        st.subheader("📊 Horas e Queima por RPM")
        
        rpms_input = {}
        for rpm in ["1.200", "1.300", "1.400", "1.500", "1.600", "1.700", "1.800"]:
            c_h, c_q = st.columns(2)
            h = c_h.number_input(f"Horas {rpm} RPM", min_value=0.0, step=0.1, key=f"h_{rpm}")
            q = c_q.number_input(f"Queima {rpm} L/H", min_value=0.0, step=0.1, key=f"q_{rpm}")
            rpms_input[f"{rpm} RPM"] = {"horas": h, "queima": q}
        
        st.subheader("⚙️ MCA")
        cmca1, cmca2 = st.columns(2)
        mca_h = cmca1.number_input("MCA Total Horas", value=92.8)
        mca_q = cmca2.number_input("MCA Queima L/H", value=6.5)

    # Lógica Matemática de Consumo
    consumo_mcp = sum([v['horas'] * v['queima'] for v in rpms_input.values()])
    consumo_total = consumo_mcp + (mca_h * mca_q)
    saldo_final = rem_saida - consumo_total
    
    st.divider()
    st.metric("SALDO FINAL (REMANESCENTE CHEGADA)", f"{saldo_final:,.2f} L", delta=f"Consumo: {consumo_total:,.2f} L", delta_color="inverse")

    # Trava de Segurança
    if saldo_final < 0:
        st.error("❌ Atenção: O saldo não pode ser maior que o remanescente de saída!")
        bloqueio = True
    else:
        bloqueio = False

    enviar = st.form_submit_button("FINALIZAR, SALVAR NO NOTION E ENVIAR PDF")

if enviar:
    if bloqueio:
        st.warning("Corrija os valores de consumo antes de prosseguir.")
    else:
        dados = {
            "empurrador": empurrador, "balsas": balsas, "cmt": cmt, "chm": chm, "origem": origem, "destino": destino, 
            "dhos": dhos, "dhoc": dhoc, "rem_saida": rem_saida, "consumo_total": consumo_total, "saldo_final": saldo_final,
            "rpms": rpms_input, "mca_h": mca_h, "mca_q": mca_q
        }
        
        # 1. Gerar PDF
        pdf_bytes = gerar_pdf(dados)
        
        # 2. Enviar para o Notion
        payload = {
            "parent": {"database_id": DATABASE_ID},
            "properties": {
                "EM": {"title": [{"text": {"content": empurrador}}]},
                "CMT": {"rich_text": [{"text": {"content": cmt}}]},
                "Consumo Utilizado": {"number": round(consumo_total, 2)},
                "Data de Registro": {"date": {"start": datetime.now().isoformat()}}
            }
        }
        requests.post("https://api.notion.com/v1/pages", json=payload, headers={"Authorization": f"Bearer {NOTION_TOKEN}", "Notion-Version": "2022-06-28", "Content-Type": "application/json"})
        
        # 3. Enviar para o Make.com
        res = requests.post(MAKE_WEBHOOK_URL, files={"file": ("relatorio_viagem.pdf", pdf_bytes)})
        
        if res.status_code == 200:
            st.success("✅ Relatório salvo e enviado para o WhatsApp (Make)!")
            st.download_button("Clique aqui para baixar o PDF gerado", data=pdf_bytes, file_name=f"Relatorio_{empurrador}.pdf")
        else:
            st.error("Erro ao enviar PDF para o Make.")
