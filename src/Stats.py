import streamlit as st
import pandas as pd
import load.db as db

st.set_page_config(layout="wide")

# Título da página
st.title('Stats')

data = db.fetch_stats()

df = pd.DataFrame(data)

# Adiciona uma linha ao final da tabela com a soma da última coluna
total_row = pd.DataFrame({'method': ['Total'], 'last_transaction': [''], 'last_update': [''], 'last_file_update': [''], 'total_transactions': [df['total_transactions'].sum()]})

# Concatena o DataFrame original com a linha de total
df = pd.concat([df, total_row])

# Exibe a tabela sem o índice
st.dataframe(df, hide_index=True)