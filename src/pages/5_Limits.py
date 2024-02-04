import streamlit as st
import pandas as pd
import load.db as db

st.set_page_config(layout="wide")

# Título da página
st.title('Limits')

data = db.fetch_limits()

df_limits = pd.DataFrame(data)

# Adicionar a última coluna para medir o progresso
df_limits['progress'] = df_limits['actual'] / df_limits['plan']

history = db.fetch_history()

df_history = pd.DataFrame(history)

# Mesclar DataFrames com base na categoria
merged_df = pd.merge(df_limits, df_history, on='categoria', how='left')

# Agrupar por categoria e criar uma lista de totais
grouped_df = merged_df.groupby('categoria')['total'].agg(list).reset_index()

# Mesclar novamente para adicionar a nova coluna ao DataFrame original
final_df = pd.merge(df_limits, grouped_df, on='categoria', how='left')

# Renomear a nova coluna
final_df = final_df.rename(columns={'total': 'history'})

# Adicione a última linha com a soma total
total_row = pd.DataFrame({
    'categoria': ['TOTAL'],
    'plan': [final_df['plan'].sum()],
    'actual': [final_df['actual'].sum()],
    'gap': [final_df['gap'].sum()]
})

final_df = pd.concat([final_df, total_row], ignore_index=True)

ColumnConfigMappingInput = {'categoria': 'Categoria', 
                            'plan': st.column_config.NumberColumn(
                                "Limite (R$)",
                                help="Limite de gastos da categoria em Reais",
                                format="%.2f"
                            ),
                            'actual': st.column_config.NumberColumn(
                                "Realizado (R$)",
                                help="Gastos realizados na categoria em Reais neste mês",
                                format="%.2f"
                            ),
                            'gap': st.column_config.NumberColumn(
                                "Gap (R$)",
                                help="Valor ainda livre na categoria em Reais neste mês",
                                format="%.2f"
                            ),
                            'progress': st.column_config.ProgressColumn(
                                "Progresso",
                                help="Progressão de gastos na categoria neste mês",
                                format="%.2f",
                                min_value=0,
                                max_value=1,
                            ),
                            'history': st.column_config.LineChartColumn(
                                "Histórico (6 meses)",
                                width="medium",
                                help="Gasto médio na categoria nos últimso 6 meses",
                            )}

# Apply your style to desired columns
final_df = final_df.style.format(
    {
        "plan": lambda x : '{:,.2f}'.format(x),
        "actual": lambda x : '{:,.2f}'.format(x),
        "gap": lambda x : '{:,.2f}'.format(x),
    },
    thousands='.',
    decimal=',',
)

st.dataframe(final_df, column_config=ColumnConfigMappingInput, height=702, hide_index=True)
