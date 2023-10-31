from openpyxl import load_workbook

# Carrega o arquivo Excel
workbook = load_workbook('BUDGET_SET23.xlsx')

# Seleciona a planilha desejada
worksheet = workbook['Summary']

def carrega_dicionario():

    # Cria um dicionário vazio
    dicionario = {}

    # Percorre as células das colunas A e C
    for row in worksheet.iter_rows(min_row=2, values_only=True):
        chave = row[1]
        valor = row[3]
        dicionario[chave] = valor

    # Retorna o dicionário
    return dicionario

# Fecha o arquivo
workbook.close()