import os
import tempfile
from io import BytesIO

import pandas as pd
import streamlit as st

from parser import parse_pdf_items

st.set_page_config(page_title="PDF -> Planilha (Perdas)", layout="wide")
st.title("Leitor de PDFs (Perdas por Departamento) -> Planilha")

st.write("Faça upload dos PDFs e informe Setor, Mês e Semana. O sistema extrai Produto/Quantidade/Valor e gera Excel.")

col1, col2, col3 = st.columns(3)
with col1:
    setor = st.text_input("Setor (fixo para todas as linhas)", value="")
with col2:
    mes = st.text_input("Mês (ex.: 2025-12 ou Dez/2025)", value="")
with col3:
    semana = st.text_input("Semana (ex.: 51 ou 17-23/12)", value="")

uploaded = st.file_uploader("Envie 1 ou mais PDFs", type=["pdf"], accept_multiple_files=True)

if uploaded:
    all_rows = []

    for f in uploaded:
        # salva o upload em arquivo temporário
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(f.getbuffer())
            tmp_path = tmp.name

        try:
            rows = parse_pdf_items(tmp_path)
            for r in rows:
                r["Setor"] = setor
                r["Mês"] = mes
                r["Semana"] = semana
            all_rows.extend(rows)
        finally:
            os.remove(tmp_path)

    if not all_rows:
        st.warning("Não encontrei linhas de itens no padrão esperado. Se quiser, me mande um PDF com formato diferente para ajustar o parser.")
    else:
        df = pd.DataFrame(all_rows, columns=["Produto", "Setor", "Mês", "Semana", "Quantidade", "Valor"])

        st.subheader("Prévia")
        st.dataframe(df, use_container_width=True, height=420)

        # Exporta para Excel
        out = BytesIO()
        with pd.ExcelWriter(out, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Perdas")

        st.download_button(
            "Baixar Excel",
            data=out.getvalue(),
            file_name="perdas.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
