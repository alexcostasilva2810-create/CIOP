import streamlit as st
import requests
from datetime import datetime

# --- CONFIGURAÇÕES ---
MAKE_WEBHOOK_URL = "https://hook.us2.make.com/skp55xrn0n81u84ikog1czrvouj4f64l"

st.set_page_config(page_title="Relatório de Viagem", layout="wide")

# CSS para aplicar as medidas exatas do seu desenho (2cm e 3cm)
st.markdown("""
    <style>
    /* 1. Controla o espaço de 2cm após o texto 'Horas Navegadas' */
    [data-testid="column"] {
        flex: 0 1 auto !important;
        width: auto !important;
        min-width: 0px !important;
        padding-right: 25px !important; /* Espaço de ~2cm */
    }
    
    /* 2. Trava a largura dos campos de preenchimento em ~3cm */
    .stNumberInput input {
        width: 110px !important; /* Aproximadamente 3cm na tela */
        height: 35px !important;
    }
    
    /* 3. Estiliza a caixa azul de Subtotal */
    .stAlert {
        padding: 5px 10px !important;
        width: 150px !important;
        min-height: 0px !important;
        background-color: #e8f0fe !important;
        color: #1967d2 !important;
        border: none !important;
    }

    /* Alinha o texto das labels com as caixas */
    .stMarkdown p { 
        margin-top: 5px !important; 
        white-space: nowrap !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🚢 Sistema de Despacho Marítimo")

# --- CABEÇALHO ---
col1, col2, col3, col4 = st.columns(4)
with col1: empurrador = st.selectbox("E/M", ["GD CUMARU", "SAMAUAMA", "JATOBA"])
with col2: balsas = st.text_input("BALSAS")
with col3: rem_saida = st.number_input("REM. SAÍDA", value=33761.25)
with col4: cmt = st.text_input("CMT")

st.divider()
st.subheader("📊 Navegação por RPM (MCP)")

# --- TABELA COM AS POSIÇÕES DO DESENHO ---
rpms = ["1.200 RPM", "1.300 RPM", "1.400 RPM", "1.500 RPM", "1.600 RPM", "1.700 RPM", "1.800 RPM"]
total_mcp = 0.0

# Cabeçalhos alinhados
h1, h2, h3, h4 = st.columns(4)
h2.caption("Horas")
h3.caption("Queima")

for rpm in rpms:
    # Cria as colunas que ficarão compactas à esquerda
    col_txt, col_h, col_q, col_res = st.columns(4)
    
    # Texto à esquerda
    col_txt.write(f"**HORAS NAVEGADAS {rpm}:**")
    
    # Define valores iniciais (exemplo)
    val_h = 84.3 if "1.500" in rpm else (8.3 if "1.600" in rpm else 0.0)
    val_q = 231.0 if "1.500" in rpm else (270.5 if "1.600" in rpm else 0.0)
    
    # Campos de preenchimento (Os retângulos de 3cm)
    h = col_h.number_input(f"h_{rpm}", value=val_h, format="%.1f", label_visibility="collapsed")
    q = col_q.number_input(f"q_{rpm}", value=val_q, format="%.1f", label_visibility="collapsed")
    
    # Subtotal matemático automático
    sub = h * q
    total_mcp += sub
    col_res.info(f"{sub:,.2f} L")

st.divider()

# --- MCA ---
m1, m2, m3, m4 = st.columns(4)
m1.write("**TOTAL MCA:**")
mca_h = m2.number_input("MCA_H", value=92.8, label_visibility="collapsed")
mca_q = m3.number_input("MCA_Q", value=6.5, label_visibility="collapsed")
cons_mca = mca_h * mca_q
m4.info(f"{cons_mca:,.2f} L")

# --- TOTAIS ---
cons_total = total_mcp + cons_mca
saldo = rem_saida - cons_total

r1, r2 = st.columns(2)
r1.metric("CONSUMO TOTAL", f"{cons_total:,.2f} L")
r2.metric("REMANESCENTE CHEGADA", f"{saldo:,.2f} L")

if st.button("FINALIZAR E ENVIAR RELATÓRIO"):
    requests.post(MAKE_WEBHOOK_URL, json={"consumo": cons_total, "saldo": saldo})
    st.success("✅ Relatório enviado com sucesso!")
