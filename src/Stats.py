import streamlit as st
import pandas as pd
import load.db as db

st.set_page_config(layout="centered")

# Título da página
st.title('Stats')

data = db.fetch_stats()

df = pd.DataFrame(data)

st.table(df)