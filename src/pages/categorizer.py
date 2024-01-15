import pandas as pd
import streamlit as st
import os, sys

# Caminho do arquivo atual
current_file_path = os.path.abspath(__file__)

# Caminho da raiz do projeto
ROOT_DIR = os.path.abspath(os.path.join(current_file_path, "../../.."))

sys.path.append(ROOT_DIR)

from imports import *

import load.db as db

st.set_page_config(layout="centered", page_title="Categorizer", page_icon="🧮")

st.title("✍️ Editar categorias")

data = db.fetch_uncategorized_transactions()

df = pd.DataFrame(data)
df.categoria = df.categoria.astype("category")
df.categoria = df.categoria.cat.set_categories(('ÁGUA', 'ALIMENTAÇÃO', 'ALUGUEL', 'BEBÊ', 'BEBÊ INVESTIMENTO', 'CARRO', 'CASA', 'COMPRAS', 'DOMÉSTICA', 
'GÁS', 'INTERNET', 'INVESTIMENTO', 'LAZER', 'LUZ', 'MERCADO', 'PET', 'PROVENTOS', 'SAÚDE', 'SERVIÇOS', 'STREAMING', 'TARIFA', 'TRANSPORTE'))

ColumnConfigMappingInput = {'data': 'DATA', 
                            'item': 'ITEM',
                            'detalhe': 'DETALHE',
                            'ocorrencia_dia': None, 
                            'valor': 'VALOR',  
                            'cartao': None,  
                            'parcela': 'PARCELA',
                            'categoria': 'CATEGORIA',
                            'tag': 'TAG',
                            'meio': 'MEIO'}

annotated = st.data_editor(df, hide_index=True, use_container_width=True, disabled=['data', 'item', 'valor', 'parcela', 'meio'], column_config=ColumnConfigMappingInput )

st.download_button(
    "⬇️ Download annotations as .csv", annotated.to_csv(), "annotated.csv", use_container_width=True
)