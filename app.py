import streamlit as st

import requests

from datetime import datetime



# --- CONFIGURAÇÕES DO NOTION ---

NOTION_TOKEN = "ntn_KF635337593asvoK365BE8elugieK9vDsu88LJ2Xyk00yC"

DATABASE_ID = "2f9025de7b79802aa7d8e4711eff1ab6"



st.set_page_config(page_title="Cálculo de Consumo Marítimo", layout="wide")



st.title("🚢 Relatório de Viagem - Lógica de Queima")



with st.form("main_form"):

    # --- DADOS INICIAIS ---

    c1, c2 = st.columns(2)

    with c1:

        empurrador = st.selectbox("E/M", ["CUMARU", "SAMAUAMA", "JATOBA", "LUIZ FELIPE", "IPE", "AROEIRA", "ANGICO", "JACARANDA", "CAJERANA", "QUARUBA"])

        balsas = st.text_input("BT's/BG's", placeholder="Ex: GD XLI, GD XLII...")

    with c2:

        rem_saida = st.number_input("REMANESCENTE DE SAÍDA (L)", value=33761.25, format="%.2f")

        cmt = st.text_input("Comandante (CMT)")



    st.divider()



    # --- MATRIZ DE RPM E QUEIMA ---

    st.subheader("📊 Navegação por RPM (MCP)")

    st.write("Informe as Horas e a Taxa de Queima (L/H) para cada faixa:")

    

    # Cabeçalho da tabela de cálculo

    h_col, q_col, r_col = st.columns([2, 2, 2])

    h_col.write("**Horas Navegadas**")

    q_col.write("**Queima (L/H)**")

    r_col.write("**Subtotal Consumo**")



    rpms = ["1.200 RPM", "1.300 RPM", "1.400 RPM", "1.500 RPM", "1.600 RPM", "1.700 RPM", "1.800 RPM"]

    dados_mcp = {}



    for rpm in rpms:

        col_h, col_q, col_r = st.columns([2, 2, 2])

        # Define valores padrão conforme sua imagem anterior para teste

        default_h = 84.3 if "1.500" in rpm else (8.3 if "1.600" in rpm else 0.0)

        default_q = 231.0 if "1.500" in rpm else (270.5 if "1.600" in rpm else 0.0)

        

        horas = col_h.number_input(f"Horas {rpm}", min_value=0.0, value=default_h, format="%.1f", label_visibility="collapsed")

        queima = col_q.number_input(f"Queima {rpm}", min_value=0.0, value=default_q, format="%.1f", label_visibility="collapsed")

        subtotal = horas * queima

        col_r.write(f"**{subtotal:,.2f} L**")

        dados_mcp[rpm] = subtotal



    st.divider()



    # --- MOTORES AUXILIARES (MCA) ---

    st.subheader("⚙️ Motores Auxiliares (MCA)")

    col_mca_h, col_mca_q, col_mca_res = st.columns([2, 2, 2])

    

    mca_horas = col_mca_h.number_input("MCA - Total de Horas", min_value=0.0, value=92.8, format="%.1f")

    mca_queima = col_mca_q.number_input("MCA - Queima (L/H)", min_value=0.0, value=6.5, format="%.1f")

    consumo_mca = mca_horas * mca_queima

    col_mca_res.write(f"**Consumo MCA: {consumo_mca:,.2f} L**")



    # --- CÁLCULO FINAL ---

    consumo_total_mcp = sum(dados_mcp.values())

    consumo_final = consumo_total_mcp + consumo_mca

    saldo_final = rem_saida - consumo_final



    st.divider()

    

    # --- RESULTADOS NA TELA ---

    res1, res2, res3 = st.columns(3)

    res1.metric("CONSUMO TOTAL", f"{consumo_final:,.2f} L")

    res2.metric("REMANESCENTE CHEGADA", f"{saldo_final:,.2f} L")

    

    if saldo_final < 0:

        st.error(f"⚠️ ERRO: O consumo ({consumo_final:,.2f} L) excede o Remanescente de Saída!")

        bloqueio = True

    else:

        st.success("✅ Saldo Positivo")

        bloqueio = False



    submit = st.form_submit_button("SALVAR E GERAR RELATÓRIO")



if submit:

    if bloqueio:

        st.error("Corrija os valores. O consumo não pode ser maior que o remanescente.")

    else:

        # Envio para o Notion

        payload = {

            "parent": {"database_id": DATABASE_ID},

            "properties": {

                "EM": {"title": [{"text": {"content": f"{empurrador} | {balsas}"}}]},

                "CMT": {"rich_text": [{"text": {"content": cmt}}]},

                "Consumo Utilizado": {"number": round(consumo_final, 2)},

                "DHOS": {"rich_text": [{"text": {"content": f"Saldo: {round(saldo_final, 2)}L"}}]},

                "Data de Registro": {"date": {"start": datetime.now().isoformat()}}

            }

        }

        res = requests.post("https://api.notion.com/v1/pages", 

                            json=payload, 

                            headers={"Authorization": f"Bearer {NOTION_TOKEN}", 

                                     "Notion-Version": "2022-06-28", "Content-Type": "application/json"})

        

        if res.status_code == 200:

            st.balloons()

            st.success("Dados salvos no Notion!")
