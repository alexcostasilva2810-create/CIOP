import streamlit as st
import requests
from datetime import datetime

# --- CONFIGURAÇÕES ---
MAKE_WEBHOOK_URL = "https://hook.us2.make.com/skp55xrn0n81u84ikog1czrvouj4f64l"

st.set_page_config(page_title="Relatório de Viagem", layout="centered")

# CSS Mantendo o padrão de 2cm e 3cm
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
    /* Estilização para as caixas de alerta de porcentagem */
    .perc-box {
        padding: 10px;
        border-radius: 5px;
        font-weight: bold;
        text-align: center;
        width: 250px;
    }
    .stAlert { padding: 5px 10px !important; width: 140px !important; }
    .stMarkdown p { margin-top: 5px !important; white-space: nowrap !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚢 Relatório de Viagem Completo")

# --- CABEÇALHO ---
c1, c2, c3, c4 = st.columns(4)
with c1: empurrador = st.selectbox("E/M", ["GD CUMARU", "SAMAUAMA", "JATOBA"])
with c2: cmt = st.text_input("CMT")
with c3: rem_saida = st.number_input("REM. SAÍDA", value=33761.25)
with c4: balsas = st.text_input("BALSAS")

st.divider()

# --- INFORMAÇÕES DA VIAGEM ---
st.subheader("📋 Informações da Viagem")
nc1, nc2, nc3, nc4 = st.columns(4)
chm = nc1.text_input("CHM")
origem = nc2.text_input("ORIGEM")
destino = nc3.text_input("DESTINO")
rpm_aut = nc4.text_input("RPM AUTORIZADO")

nc5, nc6 = st.columns(2)
dhos = nc5.text_input("DHOS (Saída)", value=datetime.now().strftime("%d/%m/%Y %H:%M"))
dhoc = nc6.text_input("DHOC (Chegada)")

# Horímetros
st.write("**Horímetros MCP e MCA:**")
h_col1, h_col2, h_col3, h_col4 = st.columns(4)
h_saida_bb = h_col1.number_input("SAÍDA BB", format="%.1f")
h_atual_bb = h_col2.number_input("ATUAL BB", format="%.1f")
h_saida_mca1 = h_col3.number_input("SAÍDA MCA 1", format="%.1f")
h_atual_mca1 = h_col4.number_input("ATUAL MCA 1", format="%.1f")

st.divider()

# --- TABELA DE RPM ---
st.subheader("📊 Navegação por RPM (MCP)")
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

# MCA
st.divider()
m1, m2, m3, m4 = st.columns(4)
m1.write("**TOTAL MCA:**")
mca_h = m2.number_input("MCA_H", value=92.8, label_visibility="collapsed")
mca_q = m3.number_input("MCA_Q", value=6.5, label_visibility="collapsed")
cons_mca = mca_h * mca_q
m4.info(f"{cons_mca:,.2f} L")

# --- CÁLCULOS FINAIS E PORCENTAGEM ---
cons_total = total_mcp + cons_mca
saldo_chegada = rem_saida - cons_total

# Cálculo da Porcentagem
if rem_saida > 0:
    porcentagem_consumo = (cons_total / rem_saida) * 100
else:
    porcentagem_consumo = 0

# Definição de Cores
cor_fundo = "#f0f2f6" # Cor padrão
cor_texto = "black"

if porcentagem_consumo >= 50:
    cor_fundo = "red"
    cor_texto = "white"
elif porcentagem_consumo >= 35:
    cor_fundo = "orange"
    cor_texto = "white"
elif porcentagem_consumo >= 25:
    cor_fundo = "yellow"
    cor_texto = "black"

st.divider()
res_col1, res_col2, res_col3 = st.columns([2, 3, 2])

with res_col1:
    st.metric("CONSUMO TOTAL", f"{cons_total:,.2f} L")

with res_col2:
    # Mensagem personalizada com cor dinâmica
    st.markdown(f"""
        <div style="background-color:{cor_fundo}; color:{cor_texto}; padding:15px; border-radius:10px; border: 1px solid #ccc;">
            O consumo nessa viagem equivale a <b>{porcentagem_consumo:.1f}%</b> em referência ao remanescente de saída.
        </div>
    """, unsafe_allow_html=True)

with res_col3:
    st.metric("REM. CHEGADA", f"{saldo_chegada:,.2f} L")

if st.button("FINALIZAR E ENVIAR RELATÓRIO"):
    dados = {
        "empurrador": empurrador, "consumo": cons_total, 
        "porcentagem": f"{porcentagem_consumo:.1f}%", "saldo": saldo_chegada
    }
    requests.post(MAKE_WEBHOOK_URL, json=dados)
    st.success("✅ Relatório enviado!")
