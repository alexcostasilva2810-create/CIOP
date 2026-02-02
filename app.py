import streamlit as st
import requests
from datetime import datetime

# --- CONFIGURAÇÕES ---
MAKE_WEBHOOK_URL = "https://hook.us2.make.com/skp55xrn0n81u84ikog1czrvouj4f64l"

st.set_page_config(page_title="Relatório de Viagem", layout="wide")

# CSS para COLAR tudo na esquerda e deixar os campos pequenos (3cm)
st.markdown("""
    <style>
    /* 1. Remove o estiramento das colunas e cola na esquerda */
    [data-testid="column"] {
        flex: 0 1 auto !important;
        width: auto !important;
        min-width: 0px !important;
        padding-right: 15px !important;
    }
    /* 2. Trava os campos de entrada em ~3cm (100px) */
    .stNumberInput input {
        width: 100px !important;
        height: 35px !important;
    }
    /* 3. Ajusta a caixa azul de resultado */
    .stAlert {
        padding: 5px 10px !important;
        width: 150px !important;
        min-height: 0px !important;
        border: none !important;
    }
    /* 4. Alinha o texto verticalmente com as caixas */
    .stMarkdown p { margin-top: 5px !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚢 Sistema de Despacho Marítimo")

# --- CABEÇALHO ---
c1, c2, c3, c4 = st.columns(4)
with c1: empurrador = st.selectbox("E/M (Empurrador)", ["GD CUMARU", "SAMAUAMA", "JATOBA"])
with c2: balsas = st.text_input("BALSAS", placeholder="GD XLI...")
with c3: rem_saida = st.number_input("REMANESCENTE SAÍDA", value=33761.25)
with c4: cmt = st.text_input("CMT (Comandante)")

st.divider()
st.subheader("📊 Navegação por RPM (MCP)")

# --- TABELA COMPACTA (POSIÇÃO EXATA DO SEU DESENHO) ---
rpms = ["1.200 RPM", "1.300 RPM", "1.400 RPM", "1.500 RPM", "1.600 RPM", "1.700 RPM", "1.800 RPM"]
total_mcp = 0.0

# Títulos de cabeçalho
h1, h2, h3, h4 = st.columns(4)
h2.caption("Horas")
h3.caption("Queima")

for rpm in rpms:
    # Criamos as 4 colunas que agora ficarão "grudadas" à esquerda
    col_txt, col_h, col_q, col_res = st.columns(4)
    
    col_txt.write(f"**HORAS NAVEGADAS {rpm}:**")
    
    # Valores padrão para teste
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

# Resultados Finais
cons_total = total_mcp + cons_mca
saldo = rem_saida - cons_total

st.divider()
res1, res2 = st.columns(2)
res1.metric("CONSUMO TOTAL (Cálculo)", f"{cons_total:,.2f} L")
res2.metric("REMANESCENTE CHEGADA", f"{saldo:,.2f} L")

if st.button("FINALIZAR, SALVAR E ENVIAR E-MAIL"):
    # Envia os dados para o Make
    requests.post(MAKE_WEBHOOK_URL, json={
        "empurrador": empurrador,
        "consumo": cons_total,
        "saldo": saldo,
        "dhos": datetime.now().strftime("%d/%m/%Y %H:%M")
    })
    st.success("✅ Relatório enviado!")
