import streamlit as st
import requests
from datetime import datetime
from fpdf import FPDF
import io

# --- CONFIGURAÇÕES ---
NOTION_TOKEN = "ntn_KF635337593asvoK365BE8elugieK9vDsu88LJ2Xyk00yC"
DATABASE_ID = "2f9025de7b79802aa7d8e4711eff1ab6"
MAKE_WEBHOOK_URL = "https://hook.us2.make.com/skp55xrn0n81u84ikog1czrvouj4f64l"

st.set_page_config(page_title="Relatório de Viagem", layout="wide")

# CSS MÁGICO: Remove espaços, diminui os inputs e cola os campos no texto
st.markdown("""
    <style>
    /* Remove o espaço gigante entre as colunas */
    [data-testid="column"] {
        width: min-content !important;
        flex: unset !important;
        padding: 0px 5px !important;
        min-width: 0px !important;
    }
    /* Deixa a caixa de entrada (input) quadrada e com ~3cm */
    .stNumberInput input {
        width: 80px !important;
        height: 35px !important;
        padding: 2px !important;
    }
    /* Ajusta a largura da caixa azul do subtotal */
    .stAlert {
        padding: 5px !important;
        width: 130px !important;
        border: none !important;
    }
    /* Remove margem superior dos inputs para alinhar com o texto */
    .stNumberInput { margin-top: -10px !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚢 Relatório de Viagem - Lógica de Queima")

# --- CABEÇALHO ---
c1, c2, c3, c4 = st.columns([2, 1, 1, 2])
with c1: empurrador = st.selectbox("E/M", ["CUMARU", "SAMAUAMA", "JATOBA", "LUIZ FELIPE", "IPE", "AROEIRA", "ANGICO", "JACARANDA", "CAJERANA", "QUARUBA"])
with c2: balsas = st.text_input("BT's/BG's", placeholder="GD XLI...")
with c3: rem_saida = st.number_input("REM. SAÍDA", value=33761.25)
with c4: cmt = st.text_input("CMT (Comandante)")

st.divider()

# --- TABELA DE RPM (POSIÇÃO EXATA DO DESENHO) ---
rpms = ["1.200 RPM", "1.300 RPM", "1.400 RPM", "1.500 RPM", "1.600 RPM", "1.700 RPM", "1.800 RPM"]
dados_mcp = {}
total_mcp = 0.0

# Cabeçalhos
h1, h2, h3, h4 = st.columns([2.5, 0.5, 0.5, 3])
h2.caption("Horas")
h3.caption("Queima")

for rpm in rpms:
    # Definimos larguras fixas para "colar" os campos no texto
    col_txt, col_h, col_q, col_res = st.columns([2.5, 0.5, 0.5, 3])
    
    col_txt.write(f"**HORAS NAVEGADAS {rpm}:**")
    
    def_h = 84.3 if "1.500" in rpm else (8.3 if "1.600" in rpm else 0.0)
    def_q = 231.0 if "1.500" in rpm else (270.5 if "1.600" in rpm else 0.0)
    
    # Inputs quadrados (Retângulos do desenho)
    h = col_h.number_input(f"h_{rpm}", min_value=0.0, value=def_h, format="%.1f", label_visibility="collapsed")
    q = col_q.number_input(f"q_{rpm}", min_value=0.0, value=def_q, format="%.1f", label_visibility="collapsed")
    
    sub = h * q
    total_mcp += sub
    col_res.info(f"{sub:,.2f} L")
    dados_mcp[rpm] = {"h": h, "q": q, "sub": sub}

st.divider()

# --- MCA ---
m1, m2, m3, m4 = st.columns([2.5, 0.5, 0.5, 3])
m1.write("**TOTAL MCA:**")
mca_h = m2.number_input("MCA_H", value=92.8, label_visibility="collapsed")
mca_q = m3.number_input("MCA_Q", value=6.5, label_visibility="collapsed")
cons_mca = mca_h * mca_q
m4.info(f"{cons_mca:,.2f} L")

# --- RESULTADOS E BOTÃO ---
cons_total = total_mcp + cons_mca
saldo = rem_saida - cons_total

r1, r2 = st.columns(2)
r1.metric("CONSUMO TOTAL", f"{cons_total:,.2f} L")
r2.metric("REMANESCENTE CHEGADA", f"{saldo:,.2f} L")

if st.button("FINALIZAR E ENVIAR RELATÓRIO"):
    # Envio para o Make (Gmail)
    res = requests.post(MAKE_WEBHOOK_URL, json={
        "empurrador": empurrador,
        "consumo": cons_total,
        "saldo": saldo,
        "dhos": datetime.now().strftime("%d/%m/%Y %H:%M")
    })
    if res.status_code == 200:
        st.success("✅ Enviado!")
        st.balloons()
