import streamlit as st
import requests
from datetime import datetime
from fpdf import FPDF

# --- CONFIGURAÇÕES ---
NOTION_TOKEN = "ntn_KF635337593asvoK365BE8elugieK9vDsu88LJ2Xyk00yC"
DATABASE_ID = "2f9025de7b79802aa7d8e4711eff1ab6"
MAKE_WEBHOOK_URL = "https://hook.us2.make.com/skp55xrn0n81u84ikog1czrvouj4f64l"

st.set_page_config(page_title="Relatório de Viagem", layout="wide")

# CSS Ninja para forçar os campos a ficarem pequenos (3cm) e remover espaços
st.markdown("""
    <style>
    /* Remove o preenchimento entre colunas */
    [data-testid="column"] { 
        padding-left: 0px !important;
        padding-right: 5px !important;
        flex-grow: 0 !important;
        min-width: 0px !important;
    }
    /* Estiliza o campo numérico para ser quadrado/pequeno */
    .stNumberInput div div input {
        width: 100px !important;
        padding: 5px !important;
    }
    /* Ajusta a largura da caixa azul de subtotal */
    .stAlert {
        padding: 5px !important;
        width: 140px !important;
        min-height: 0px !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🚢 Relatório de Viagem - Lógica de Queima")

# --- CABEÇALHO ---
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
st.subheader("📊 Navegação por RPM (MCP)")

# --- TABELA DE RPM (POSIÇÃO CONFORME DESENHO) ---
rpms = ["1.200 RPM", "1.300 RPM", "1.400 RPM", "1.500 RPM", "1.600 RPM", "1.700 RPM", "1.800 RPM"]
dados_mcp = {}
total_mcp = 0.0

for rpm in rpms:
    # Ajuste milimétrico das proporções: Rótulo largo e inputs colados
    col_label, col_h, col_q, col_res = st.columns([2.5, 0.8, 0.8, 4])
    
    # Texto à esquerda
    col_label.write(f"**HORAS NAVEGADAS {rpm}:**")
    
    # Valores padrão
    def_h = 84.3 if "1.500" in rpm else (8.3 if "1.600" in rpm else 0.0)
    def_q = 231.0 if "1.500" in rpm else (270.5 if "1.600" in rpm else 0.0)
    
    # Inputs (Retângulos pequenos conforme desenho)
    h = col_h.number_input(f"h_{rpm}", min_value=0.0, value=def_h, format="%.1f", label_visibility="collapsed")
    q = col_q.number_input(f"q_{rpm}", min_value=0.0, value=def_q, format="%.1f", label_visibility="collapsed")
    
    # Subtotal (Logo após os inputs)
    sub = h * q
    total_mcp += sub
    col_res.info(f"Subtotal: {sub:,.2f} L")
    
    dados_mcp[rpm] = {"h": h, "q": q, "sub": sub}

st.divider()

# --- MCA ---
m1, m2, m3, m4 = st.columns([2.5, 0.8, 0.8, 4])
m1.write("**TOTAL MCA:**")
mca_h = m2.number_input("MCA_H", value=92.8, label_visibility="collapsed")
mca_q = m3.number_input("MCA_Q", value=6.5, label_visibility="collapsed")
cons_mca = mca_h * mca_q
m4.info(f"Consumo MCA: {cons_mca:,.2f} L")

# --- RESULTADOS FINAIS ---
cons_total = total_mcp + cons_mca
saldo_final = rem_saida - cons_total

res1, res2 = st.columns(2)
res1.metric("CONSUMO TOTAL", f"{cons_total:,.2f} L")
res2.metric("REMANESCENTE CHEGADA", f"{saldo_final:,.2f} L")

if st.button("FINALIZAR, SALVAR E ENVIAR RELATÓRIO"):
    # Gatilho para o Make (Gmail) enviando os dados finais
    requests.post(MAKE_WEBHOOK_URL, json={
        "empurrador": empurrador,
        "comandante": cmt,
        "consumo_total": cons_total,
        "saldo": saldo_final,
        "data": datetime.now().strftime("%d/%m/%Y %H:%M")
    })
    st.success("✅ Relatório enviado com sucesso!")
    st.balloons()
