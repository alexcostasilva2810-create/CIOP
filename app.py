import streamlit as st
import requests
from datetime import datetime

# --- CONFIGURAÇÕES DO NOTION ---
NOTION_TOKEN = "ntn_KF635337593asvoK365BE8elugieK9vDsu88LJ2Xyk00yC"
DATABASE_ID = "2f9025de7b79802aa7d8e4711eff1ab6"

def enviar_ao_notion(dados):
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    payload = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "EM": {"title": [{"text": {"content": dados['em']}}]},
            "CMT": {"rich_text": [{"text": {"content": dados['cmt']}}]},
            "Origem": {"rich_text": [{"text": {"content": dados['origem']}}]},
            "Destino": {"rich_text": [{"text": {"content": dados['destino']}}]},
            "DHOS": {"rich_text": [{"text": {"content": dados['dhos']}}]},
            "Consumo Utilizado": {"number": dados['consumo']},
            "Data de Registro": {"date": {"start": datetime.now().isoformat()}}
        }
    }
    response = requests.post(url, json=payload, headers=headers)
    return response

# --- INTERFACE STREAMLIT ---
st.title("🚢 Registro de Viagem")

with st.form("form_viagem"):
    em = st.text_input("E/M", value="GD CUMARU")
    cmt = st.text_input("Comandante (CMT)")
    col1, col2 = st.columns(2)
    with col1:
        origem = st.text_input("Origem", value="PVH")
        dhos = st.text_input("DHOS", value="26/01 18:00")
    with col2:
        destino = st.text_input("Destino", value="NVR")
        consumo = st.number_input("Consumo Utilizado (L)", min_value=0.0, format="%.2f")
    
    submit = st.form_submit_button("Salvar na Tabela")

if submit:
    dados = {
        "em": em, "cmt": cmt, "origem": origem, 
        "destino": destino, "dhos": dhos, "consumo": consumo
    }
    res = enviar_ao_notion(dados)
    
    if res.status_code == 200:
        st.success("✅ Salvo no Notion com sucesso!")
    else:
        st.error(f"❌ Erro ao salvar: {res.text}")
