import streamlit as st
import pandas as pd
import os, sys

# Caminho do arquivo atual
current_file_path = os.path.abspath(__file__)

# Caminho da raiz do projeto
ROOT_DIR = os.path.abspath(os.path.join(current_file_path, "../../.."))

sys.path.append(ROOT_DIR)

# from imports import * (File missing)

import load.db as db

def save_categorized_transactions(df):

    dict = df.to_dict(orient='records')
    db.update_uncategorized_records(dict)

st.set_page_config(layout="wide", page_title="Categorizer",)

# Título da página
st.title('Categories')

data = db.fetch_uncategorized_transactions()

df = pd.DataFrame(data)

if df.size == 0:
    st.markdown("Sem transações para categorizar...")

# [ ] Fazer QUERY categories.name para popular dropdown box
    
else:
    df.categoria = df.categoria.astype("category")
    df.categoria = df.categoria.cat.set_categories(('ÁGUA', 'ALIMENTAÇÃO', 'ALUGUEL', 'BEBÊ', 'BEBÊ INVESTIMENTO', 'CARRO', 'CASA', 'COMPRAS', 'DOMÉSTICA', 
    'GÁS', 'INTERNET', 'INVESTIMENTO', 'LAZER', 'LUZ', 'MERCADO', 'OUTROS', 'PAGAMENTO', 'PET', 'PROVENTOS', 'PROVENTOS CMC', 'PROVENTOS PQR', 'REALOCAÇÃO', 
    'RENDIMENTO', 'SAÚDE', 'SERVIÇOS', 'STREAMING', 'TARIFA', 'TRANSFERÊNCIA', 'TRANSPORTE', 'VIAGENS'))

    ColumnConfigMappingInput = {'data': 'DATA', 
                                'item': 'ITEM',
                                'detalhe': 'DETALHE',
                                'ocorrencia_dia': None, 
                                'valor': 'VALOR',  
                                'cartao': None,  
                                'parcela': 'PARCELA',
                                'categoria': 'CATEGORIA',
                                'tag': 'TAG',
                                'meio': 'MEIO',
                                'hash': None}

    categorized_df = st.data_editor(df, hide_index=True, use_container_width=True, disabled=['data', 'item', 'valor', 'parcela', 'meio', 'hash'], column_config=ColumnConfigMappingInput, on_change=None)

    st.button(
        "Save", on_click=save_categorized_transactions, args=(categorized_df,), use_container_width=True
    )