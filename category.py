from openpyxl import load_workbook
from fuzzywuzzy import fuzz
import openai

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

#
# BUSCA POR AI (SW 3.0)
#

# Definir chave de API do OpenAI
openai.api_key = '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'

# Função para fazer a chamada à API e obter a resposta da LLM
def interagir_com_llm(prompt):
    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=prompt,
        max_tokens=100,
        temperature=0.7,
        n=1,
        stop=None,
        timeout=10
    )
    return response.choices[0].text.strip()

def carrega_categorias():
    categorias = ["ÁGUA",
                "ALIMENTAÇÃO",
                "ALUGUEL",
                "BEBÊ",
                "CARRO",
                "CASA",
                # "COMPRAS",
                "DOMÉSTICA",
                "GÁS",
                "INTERNET",
                "LUZ",
                "MERCADO",
                "OUTROS",
                "PET",
                "SAÚDE",
                "SERVIÇOS",
                "STREAMING",
                "TRANSPORTE",
                "VIAGENS"]
    return(", ".join(categorias))

# Preparar o prompt para um registro
def prepara_prompt(estabelecimento):
    prompt = "Dentre as seguintes categorias \"" + carrega_categorias() + "\", quais seriam as mais adequadas para classificar as compras em um cartão, cujos estabelecimentos comerciais se chamam, respectivamente \"" + estabelecimento + "\"?"
    print("Prompt: " + prompt)
    return prompt

prompt = prepara_prompt("AIRBNB, PÃO DE AÇÚCAR, UBER")
resposta = interagir_com_llm(prompt)
print("Response: " + resposta.upper())