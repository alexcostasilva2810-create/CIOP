import streamlit as st
import requests
from datetime import datetime
from fpdf import FPDF

# --- CONFIGURAÇÕES ---
NOTION_TOKEN = "ntn_KF635337593asvoK365BE8elugieK9vDsu88LJ2Xyk00yC"
DATABASE_ID = "2f9025de7b79802aa7d8e4711eff1ab6"
MAKE_WEBHOOK_URL = "https://hook.us2.make.com/skp55xrn0n81u84ikog1czrvouj4f64l"

st.set_page_config(page_title="Relatório de Viagem", layout="wide")

# CSS para remover espaços vazios e forçar largura compacta
st.markdown("""
    <style>
    [data-testid="column"] { padding: 0px 2px !important; }
    .stNumberInput { width: 110px !important; } /* Força os ~3cm nos campos */
    div.stButton > button { width: 100%; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚢 Relatório de Viagem - Lógica de Queima")

# --- CABEÇALHO COMPACTO ---
c1, c2, c3, c4 = st.columns([2, 1.5, 1.5, 2])
with c1:
    empurrador = st.selectbox("E/M", ["CUMARU", "SAMAUAMA", "JATOBA", "LUIZ FELIPE", "IPE", "AROEIRA", "ANGICO", "JACARANDA", "CAJERANA", "QUARUBA"])
with c2:
    balsas = st.text_input("BT's/BG's", placeholder="GD XLI...")
with c3:
    rem_saida = st.number_input("REM. SAÍDA (L)", value=33761.25)
with c4:
    cmt = st.text_input("CMT (Comandante)")

st.divider()

# --- TABELA DE RPM (CAMPOS DE 3CM) ---
st.subheader("📊 Navegação por RPM (MCP)")

# Títulos das colunas
t1, t2, t3, t4 = st.columns([3, 1, 1, 1.5])
t2.caption("Horas")
t3.caption("Queima")
t4.caption("Subtotal")

rpms = ["1.200 RPM", "1.300 RPM", "1.400 RPM", "1.500 RPM", "1.600 RPM", "1.700 RPM", "1.800 RPM"]
dados_mcp = {}
total_mcp = 0.0

for rpm in rpms:
    # Proporção [3, 1, 1, 1.5] deixa os campos bem pequenos e próximos
    col_txt, col_h, col_q, col_res = st.columns([3, 1, 1, 1.5])
    
    col_txt.write(f"**HORAS NAVEGADAS {rpm}:**")
    
    def_h = 84.3 if "1.500" in rpm else (8.3 if "1.600" in rpm else 0.0)
    def_q = 231.0 if "1.500" in rpm else (270.5 if "1.600" in rpm else 0.0)
    
    h = col_h.number_input(f"h_{rpm}", min_value=0.0, value=def_h, label_visibility="collapsed")
    q = col_q.number_input(f"q_{rpm}", min_value=0.0, value=def_q, label_visibility="collapsed")
    
    sub = h * q
    total_mcp += sub
    col_res.info(f"{sub:,.2f} L")
    dados_mcp[rpm] = sub

st.divider()

# --- MCA COMPACTO ---
m1, m2, m3, m4 = st.columns([3, 1, 1, 1.5])
m1.write("**TOTAL MCA:**")
mca_h = m2.number_input("MCA_H", value=92.8, label_visibility="collapsed")
mca_q = m3.number_input("MCA_Q", value=6.5, label_visibility="collapsed")
cons_mca = mca_h * mca_q
m4.info(f"{cons_mca:,.2f} L")

# --- TOTAIS ---
cons_final = total_mcp + cons_mca
saldo = rem_saida - cons_final

res1, res2 = st.columns(2)
res1.metric("CONSUMO TOTAL", f"{cons_final:,.2f} L")
res2.metric("REMANESCENTE CHEGADA", f"{saldo:,.2f} L")

if st.button("FINALIZAR E ENVIAR"):
    # Envio para o Make (Gmail)
    requests.post(MAKE_WEBHOOK_URL, json={"consumo": cons_final, "saldo": saldo})
    st.success("Enviado!")
