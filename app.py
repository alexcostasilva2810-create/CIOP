import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Relatório de Viagem", layout="wide")

st.title("🚢 Relatório Final de Viagem")

# Organizando os campos em colunas para não ficar uma lista infinita
with st.form("form_viagem"):
    col1, col2 = st.columns(2)
    
    with col1:
        vessel = st.text_input("E/M", value="GD CUMARU")
        bts_bgs = st.text_area("BT's/BG'S", value="GD XLI, GD XLII, GD XVII, GD XVIII, GD XXXIV, GD XXXVII, GD IX, GD XL, GD XLIII - CGDAS")
        cmt = st.text_input("CMT (Comandante)")
        chm = st.text_input("CHM (Chefe de Máquinas)")
        
    with col2:
        origem = st.text_input("ORIGEM", value="PVH")
        destino = st.text_input("DESTINO", value="NVR")
        dhos = st.text_input("DHOS (Data/Hora Saída)", value="26/01 18:00 (H BEL)")
        dhoc = st.text_input("DHOC (Data/Hora Chegada)", value="30/01 13:30 (H BEL)")

    st.divider()
    st.subheader("⚙️ Horímetros e Consumo")
    
    c3, c4, c5 = st.columns(3)
    with c3:
        h_saida_bb = st.number_input("Horímetro Saída MCP BB", format="%.1f")
        h_atual_bb = st.number_input("Horímetro Atual MCP BB", format="%.1f")
    with c4:
        h_saida_be = st.number_input("Horímetro Saída MCP BE", format="%.1f")
        h_atual_be = st.number_input("Horímetro Atual MCP BE", format="%.1f")
    with c5:
        mca1_saida = st.number_input("Horímetro Saída MCA 1", format="%.1f")
        mca1_atual = st.number_input("Horímetro Atual MCA 1", format="%.1f")

    st.divider()
    st.subheader("📊 Navegação e Queima")
    
    col_nav1, col_nav2 = st.columns(2)
    with col_nav1:
        horas_nav = st.number_input("HORAS NAVEGADAS TOTAL", format="%.1f")
        h_1500_rpm = st.number_input("HORAS EM 1.500 RPM", format="%.1f")
        h_1600_rpm = st.number_input("HORAS EM 1.600 RPM", format="%.1f")
        
    with col_nav2:
        rem_saida = st.number_input("REMANESCENTE SAÍDA (L)", format="%.2f")
        consumo = st.number_input("CONSUMO UTILIZADO (L)", format="%.2f")
        rem_chegada = rem_saida - consumo
        st.info(f"Remanescente Chegada: {rem_chegada:.2f} L")

    obs = st.text_area("OBSERVAÇÕES", placeholder="Ex: QUEIMA 1500 231 L/H...")

    # Botão de submissão
    btn_salvar = st.form_submit_button("GERAR RELATÓRIO E SALVAR NO NOTION")

if btn_salvar:
    # Aqui entrarão as funções de PDF e Notion nos próximos passos
    st.success("Dados capturados! Preparando envio...")
