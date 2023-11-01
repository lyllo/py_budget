from openpyxl import load_workbook
from fuzzywuzzy import fuzz

# 
# BUSCA SIMPLES (ANÁLISE LÉXICA)
#

# Carrega as colunas do Excel referentes a ITEM e CATEGORIA
def carrega_dicionario():

    # Carrega o arquivo Excel BUDGET_SET23 com transações até o mês passado
    workbook = load_workbook('BUDGET_SET23.xlsx')

    # Seleciona a planilha Summary desejada
    worksheet = workbook['Summary']

    # Cria um dicionário vazio
    dicionario = {}

    # Percorre as células das colunas B e D iniciando pela linha 2, onde B = Item e C = Categoria.
    # Exemplo ["iFood" = "Alimentação"]
    for row in worksheet.iter_rows(min_row=2, values_only=True):
        chave = row[1]
        valor = row[3]
        dicionario[chave] = valor
    
    # Fecha o arquivo
    workbook.close()

    # Retorna o dicionário
    return dicionario

#
# BUSCA POR SIMILARIDADE
#

def busca_palavras_parecidas(palavra, lista_palavras, limite):
    palavras_parecidas = []
    for palavra_lista in lista_palavras:
        similaridade = fuzz.ratio(palavra, palavra_lista)
        if similaridade >= limite:
            palavras_parecidas.append(palavra_lista)
    return palavras_parecidas

# lista_palavras = ["banana", "maçãzinha", "laranja", "abacaxi", "uva"]
# palavra_busca = "maça"
# limite_similaridade = 50

# resultados = busca_palavras_parecidas(palavra_busca, lista_palavras, limite_similaridade)

# print("Palavras parecidas encontradas:")
# for resultado in resultados:
#     print(resultado)