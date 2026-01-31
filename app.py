import streamlit as st
import requests
from datetime import datetime

# --- CONFIGURAÇÕES ---
NOTION_TOKEN = "ntn_KF635337593asvoK365BE8elugieK9vDsu88LJ2Xyk00yC"
DATABASE_ID = "2f9025de7b79802aa7d8e4711eff1ab6"

st.set_page_config(page_title="Controle de Comboio", layout="wide")

# Lista de Empurradores
lista_empurradores = ["CUMARU", "SAMAUAMA", "JATOBA", "LUIZ FELIPE", "IPE", "AROEIRA", "ANGICO", "JACARANDA", "CAJERANA", "QUARUBA", "OUTRO"]

st.title("🚢 Relatório de Consumo e Comboio")

with st.form("main_form"):
    col1, col2 = st.columns(2)
    with col1:
        emp_sel = st.selectbox("E/M (Empurrador)", options=lista_empurradores)
        empurrador = st.text_input("Nome do Empurrador (se 'OUTRO')") if emp_sel == "OUTRO" else emp_sel
        cmt = st.text_input("Comandante (CMT)")
        # Campo Importante: Listagem de Balsas
        balsas = st.text_area("BT's / BG's (Quais e quantas balsas?)", placeholder="Ex: GD XLI, GD XLII (02 Unidades)")
    
    with col2:
        origem_destino = st.text_input("Trecho (Origem/Destino)", value="PVH - NVR")
        rem_saida = st.number_input("REMANESCENTE DE SAÍDA (L)", value=33761.25, step=0.01, format="%.2f")
        st.write("---")
        st.info("Insira os horímetros para calcular o saldo final automaticamente.")

    st.subheader("⚙️ Horímetros dos Motores")
    c1, c2, c3, c4 = st.columns(4)
    # MCPs (231 L/H conforme imagem)
    h_mcp_bb_s = c1.number_input("MCP BB Saída", value=7520.7)
    h_mcp_bb_a = c1.number_input("MCP BB Atual", value=7612.0)
    
    h_mcp_be_s = c2.number_input("MCP BE Saída", value=7849.7)
    h_mcp_be_a = c2.number_input("MCP BE Atual", value=7941.7)
    
    # MCAs (6.5 L/H conforme imagem)
    h_mca1_s = c3.number_input("MCA 1 Saída", value=10278.1)
    h_mca1_a = c3.number_input("MCA 1 Atual", value=10304.1)
    
    h_mca2_s = c4.number_input("MCA 2 Saída", value=8113.5)
    h_mca2_a = c4.number_input("MCA 2 Atual", value=8169.5)

    # --- LÓGICA MATEMÁTICA ---
    dif_mcp = (h_mcp_bb_a - h_mcp_bb_s) + (h_mcp_be_a - h_mcp_be_s)
    dif_mca = (h_mca1_a - h_mca1_s) + (h_mca2_a - h_mca2_s)
    
    consumo_total = (dif_mcp * 231.0) + (dif_mca * 6.5)
    saldo_final = rem_saida - consumo_total

    st.divider()
    # EXIBIÇÃO DOS RESULTADOS CRÍTICOS
    res1, res2, res3 = st.columns(3)
    res1.metric("HORAS TOTAIS (Motores)", f"{dif_mcp + dif_mca:.1f} h")
    res2.metric("CONSUMO TOTAL (L)", f"{consumo_total:,.2f} L", delta_color="inverse")
    res3.metric("SALDO NO TANQUE (L)", f"{saldo_final:,.2f} L")

    if saldo_final < 0:
        st.error("⚠️ ALERTA: Saldo negativo! Verifique os horímetros ou o remanescente inicial.")
        bloqueio = True
    else:
        bloqueio = False

    submit = st.form_submit_button("SALVAR E GERAR COMPROVANTE")

if submit:
    if bloqueio:
        st.warning("Corrija o saldo negativo antes de prosseguir.")
    else:
        # Envio para o Notion (Ajustado para as suas colunas de foco)
        payload = {
            "parent": {"database_id": DATABASE_ID},
            "properties": {
                "EM": {"title": [{"text": {"content": empurrador}}]},
                "CMT": {"rich_text": [{"text": {"content": f"Balsas: {balsas}"}}]}, # Guardamos a info das balsas aqui por enquanto
                "Consumo Utilizado": {"number": round(consumo_total, 2)},
                "DHOS": {"rich_text": [{"text": {"content": f"Saldo Final: {round(saldo_final, 2)} L"}}]},
                "Data de Registro": {"date": {"start": datetime.now().isoformat()}}
            }
        }
        res = requests.post("https://api.notion.com/v1/pages", 
                            json=payload, 
                            headers={"Authorization": f"Bearer {NOTION_TOKEN}", 
                                     "Notion-Version": "2022-06-28", "Content-Type": "application/json"})
        
        if res.status_code == 200:
            st.success(f"✅ Relatório de {empurrador} salvo! Saldo final de {saldo_final:,.2f} L registrado.")
        else:
            st.error(f"Erro na comunicação: {res.text}")
