import streamlit as st
import requests
from datetime import datetime

# --- CONFIGURAÇÕES ---
MAKE_WEBHOOK_URL = "https://hook.us2.make.com/skp55xrn0n81u84ikog1czrvouj4f64l"

st.set_page_config(page_title="Relatório de Viagem", layout="wide")

# CSS para trazer TUDO para a posição que você desenhou
st.markdown("""
    <style>
    /* 1. Remove o espaço vazio e traz as colunas para a esquerda */
    [data-testid="column"] {
        flex: 0 1 auto !important;
        width: auto !important;
        min-width: 0px !important;
        padding-right: 10px !important;
    }
    /* 2. Deixa os campos de entrada (Horas e Queima) pequenos e quadrados */
    .stNumberInput input {
        width: 85px !important;
        height: 35px !important;
    }
    /* 3. Ajusta o campo azul do Subtotal para ficar logo em seguida */
    .stAlert {
        padding: 5px 10px !important;
        width: 140px !important;
        min-height: 0px !important;
    }
    /* Alinhamento vertical do texto com os campos */
    .stMarkdown p { margin-top: 8px !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚢 Relatório de Viagem")

# --- CABEÇALHO ---
c1, c2, c3, c4 = st.columns(4)
with c1: empurrador = st.selectbox("E/M", ["CUMARU", "SAMAUAMA", "JATOBA"])
with c2: balsas = st.text_input("BT's/BG's")
with c3: rem_saida = st.number_input("REM. SAÍDA", value=33761.25)
with c4: cmt = st.text_input("CMT")

st.divider()

# --- ÁREA DE NAVEGAÇÃO (POSIÇÃO CORRIGIDA) ---
rpms = ["1.200 RPM", "1.300 RPM", "1.400 RPM", "1.500 RPM", "1.600 RPM", "1.700 RPM", "1.800 RPM"]
total_mcp = 0.0

# Títulos curtos
t1, t2, t3, t4 = st.columns([2.5, 1, 1, 2])
t2.caption("Horas")
t3.caption("Queima")

for rpm in rpms:
    # Definimos as colunas para ficarem grudadas
    col_txt, col_h, col_q, col_res = st.columns(4)
    
    col_txt.write(f"**HORAS NAVEGADAS {rpm}:**")
    
    # Valores padrão de exemplo
    def_h = 84.3 if "1.500" in rpm else (8.3 if "1.600" in rpm else 0.0)
    def_q = 231.0 if "1.500" in rpm else (270.5 if "1.600" in rpm else 0.0)
    
    h = col_h.number_input(f"h_{rpm}", value=def_h, label_visibility="collapsed")
    q = col_q.number_input(f"q_{rpm}", value=def_q, label_visibility="collapsed")
    
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

# Totais
cons_total = total_mcp + cons_mca
saldo = rem_saida - cons_total

r1, r2 = st.columns(2)
r1.metric("CONSUMO TOTAL", f"{cons_total:,.2f} L")
r2.metric("REMANESCENTE CHEGADA", f"{saldo:,.2f} L")

if st.button("FINALIZAR E ENVIAR RELATÓRIO"):
    requests.post(MAKE_WEBHOOK_URL, json={"consumo": cons_total, "saldo": saldo})
    st.success("Enviado!")
