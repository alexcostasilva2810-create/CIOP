import streamlit as st
import requests
from datetime import datetime

# --- CONFIGURAÇÕES ---
MAKE_WEBHOOK_URL = "https://hook.us2.make.com/skp55xrn0n81u84ikog1czrvouj4f64l"

# Layout centralizado para manter o formulário estreito e colado
st.set_page_config(page_title="Relatório de Viagem", layout="centered")

# CSS para manter as medidas de 2cm e 3cm que você aprovou
st.markdown("""
    <style>
    .block-container { max-width: 900px !important; }
    [data-testid="column"] {
        flex: 0 1 auto !important;
        width: auto !important;
        min-width: 0px !important;
        padding-right: 20px !important;
    }
    .stNumberInput input, .stTextInput input {
        width: 110px !important;
        height: 35px !important;
    }
    .stAlert { padding: 5px 10px !important; width: 140px !important; }
    .stMarkdown p { margin-top: 5px !important; white-space: nowrap !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("Relatório de Viagem Completo")

# --- CABEÇALHO (O que você já tinha) ---
c1, c2, c3, c4 = st.columns(4)
with c1: empurrador = st.selectbox("E/M", ["GD CUMARU", "SAMAUAMA", "JATOBA"])
with c2: cmt = st.text_input("CMT")
with c3: rem_saida = st.number_input("REM. SAÍDA", value=33761.25)
with c4: balsas = st.text_input("BALSAS")

st.divider()

# --- NOVOS CAMPOS (ACIMA DO RPM) ---
st.subheader("Informações da Viagem")

# Linha 1: CHM, Origem, Destino, RPM Autorizado
nc1, nc2, nc3, nc4 = st.columns(4)
chm = nc1.text_input("CHM")
origem = nc2.text_input("ORIGEM")
destino = nc3.text_input("DESTINO")
rpm_aut = nc4.text_input("RPM AUTORIZADO")

# Linha 2: Datas e Horas (DHOS e DHOC)
nc5, nc6 = st.columns(2)
dhos = nc5.text_input("DHOS (Data/Hora Saída)", value=datetime.now().strftime("%d/%m/%Y %H:%M"))
dhoc = nc6.text_input("DHOC (Data/Hora Chegada)")

st.write("**Horímetros MCP (BB e BE):**")
# Linha 3: Horímetros MCP
nc7, nc8, nc9, nc10 = st.columns(4)
h_saida_bb = nc7.number_input("SAÍDA BB", format="%.1f")
h_atual_bb = nc8.number_input("ATUAL BB", format="%.1f")
h_saida_be = nc9.number_input("SAÍDA BE", format="%.1f")
h_atual_be = nc10.number_input("ATUAL BE", format="%.1f")

st.write("**Horímetros MCA (1 e 2):**")
# Linha 4: Horímetros MCA
nc11, nc12, nc13, nc14 = st.columns(4)
h_saida_mca1 = nc11.number_input("SAÍDA MCA 1", format="%.1f")
h_atual_mca1 = nc12.number_input("ATUAL MCA 1", format="%.1f")
h_saida_mca2 = nc13.number_input("SAÍDA MCA 2", format="%.1f")
h_atual_mca2 = nc14.number_input("ATUAL MCA 2", format="%.1f")

st.divider()

# --- TABELA DE RPM (Sua lógica de cálculo automática) ---
st.subheader("Navegação por RPM (MCP)")
rpms = ["1.200 RPM", "1.300 RPM", "1.400 RPM", "1.500 RPM", "1.600 RPM", "1.700 RPM", "1.800 RPM"]
total_mcp = 0.0

for rpm in rpms:
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

# MCA Final
m1, m2, m3, m4 = st.columns(4)
m1.write("**TOTAL MCA:**")
mca_h = m2.number_input("MCA_H", value=92.8, label_visibility="collapsed")
mca_q = m3.number_input("MCA_Q", value=6.5, label_visibility="collapsed")
cons_mca = mca_h * mca_q
m4.info(f"{cons_mca:,.2f} L")

# Totais
cons_total = total_mcp + cons_mca
saldo = rem_saida - cons_total

st.metric("CONSUMO TOTAL", f"{cons_total:,.2f} L")
st.metric("REMANESCENTE CHEGADA", f"{saldo:,.2f} L")

if st.button("FINALIZAR E ENVIAR RELATÓRIO"):
    # Enviando todos os novos campos para o Make
    dados_completos = {
        "empurrador": empurrador, "cmt": cmt, "chm": chm,
        "origem": origem, "destino": destino, "rpm_aut": rpm_aut,
        "dhos": dhos, "dhoc": dhoc, "consumo": cons_total, "saldo": saldo
    }
    requests.post(MAKE_WEBHOOK_URL, json=dados_completos)
    st.success("✅ Relatório completo enviado para o Gmail!")
