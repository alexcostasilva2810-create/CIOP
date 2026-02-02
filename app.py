import streamlit as st
import requests
from datetime import datetime

# --- CONFIGURAÇÕES ---
MAKE_WEBHOOK_URL = "https://hook.us2.make.com/skp55xrn0n81u84ikog1czrvouj4f64l"

# DESATIVADO o layout="wide" para a tela não ficar larga
st.set_page_config(page_title="Relatório de Viagem", layout="centered")

# CSS para forçar os 2cm de espaço e 3cm de campo
st.markdown("""
    <style>
    /* 1. Trava a largura máxima do formulário para não espalhar */
    .block-container {
        max-width: 800px !important;
        padding-top: 2rem !important;
    }
    
    /* 2. Ajusta as colunas para ficarem grudadas (o espaço de 2cm) */
    [data-testid="column"] {
        flex: 0 1 auto !important;
        width: auto !important;
        min-width: 0px !important;
        padding-right: 20px !important; /* Aproximadamente 2cm */
    }
    
    /* 3. Trava os campos em 3cm (110px) */
    .stNumberInput input {
        width: 110px !important;
        height: 35px !important;
    }
    
    /* 4. Subtotal Azul compacto */
    .stAlert {
        padding: 5px 10px !important;
        width: 130px !important;
        min-height: 0px !important;
    }
    
    /* Alinhamento do texto */
    .stMarkdown p { margin-top: 5px !important; white-space: nowrap !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚢 Sistema de Despacho")

# --- CABEÇALHO COMPACTO ---
c1, c2 = st.columns(2)
with c1: 
    empurrador = st.selectbox("E/M", ["GD CUMARU", "SAMAUAMA", "JATOBA"])
    cmt = st.text_input("CMT (Comandante)")
with c2:
    rem_saida = st.number_input("REM. SAÍDA", value=33761.25)
    balsas = st.text_input("BALSAS")

st.divider()
st.subheader("📊 Navegação por RPM (MCP)")

rpms = ["1.200 RPM", "1.300 RPM", "1.400 RPM", "1.500 RPM", "1.600 RPM", "1.700 RPM", "1.800 RPM"]
total_mcp = 0.0

# Cabeçalho da tabela
h1, h2, h3, h4 = st.columns(4)
h2.caption("Horas")
h3.caption("Queima")

for rpm in rpms:
    # Colunas em linha, bem próximas
    col_txt, col_h, col_q, col_res = st.columns(4)
    
    col_txt.write(f"**HORAS {rpm}:**")
    
    def_h = 84.3 if "1.500" in rpm else (8.3 if "1.600" in rpm else 0.0)
    def_q = 231.0 if "1.500" in rpm else (270.5 if "1.600" in rpm else 0.0)
    
    h = col_h.number_input(f"h_{rpm}", value=def_h, format="%.1f", label_visibility="collapsed")
    q = col_q.number_input(f"q_{rpm}", value=def_q, format="%.1f", label_visibility="collapsed")
    
    sub = h * q
    total_mcp += sub
    col_res.info(f"{sub:,.2f} L")

st.divider()

# MCA
m1, m2, m3, m4 = st.columns(4)
m1.write("**TOTAL MCA:**")
mca_h = m2.number_input("MCA_H", value=92.8, label_visibility="collapsed")
mca_q = m3.number_input("MCA_Q", value=6.5, label_visibility="collapsed")
cons_mca = mca_h * mca_q
m4.info(f"{cons_mca:,.2f} L")

# Totais finais
cons_total = total_mcp + cons_mca
saldo = rem_saida - cons_total

st.metric("CONSUMO TOTAL", f"{cons_total:,.2f} L")
st.metric("REMANESCENTE CHEGADA", f"{saldo:,.2f} L")

if st.button("FINALIZAR E ENVIAR"):
    requests.post(MAKE_WEBHOOK_URL, json={"consumo": cons_total, "saldo": saldo, "empurrador": empurrador})
    st.success("✅ Relatório enviado!")
