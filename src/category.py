from openpyxl import load_workbook
from fuzzywuzzy import fuzz
import pickle
import configparser
import os
import ai

# Configura os paths dos arquivos que serão utilizados
ROOT_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)
PATH_TO_CONFIG_FILE = os.path.join(ROOT_DIR, 'config.ini')
PATH_TO_HISTORY_FILE = os.path.join(ROOT_DIR, 'data\\history.xlsx')
PATH_TO_BIN_FILE = os.path.join(ROOT_DIR, 'data\\dados.bin')

# Le as feature toggles do arquivo de configuração
config = configparser.ConfigParser()
config.read(PATH_TO_CONFIG_FILE)
load_xlsx = config.get('Toggle', 'load_xlsx')

# 
# BUSCA SIMPLES (ANÁLISE LÉXICA)
#

# Carrega as colunas do Excel referentes a ITEM e CATEGORIA
def carrega_dicionario():

    # Cria um dicionário vazio
    dicionario = {}

    if(load_xlsx == "true"):

        # Carrega o arquivo Excel BUDGET_SET23 com transações até o mês passado
        workbook = load_workbook(PATH_TO_HISTORY_FILE)

        # Seleciona a planilha Summary desejada
        worksheet = workbook['Summary']

        # Percorre as células das colunas B e D iniciando pela linha 2, onde B = Item e C = Categoria.
        # Exemplo ["iFood" = "Alimentação"]
        for row in worksheet.iter_rows(min_row=2, values_only=True):
            chave = row[1]
            valor = row[3]
            dicionario[chave] = valor
        
        # Fecha o arquivo
        workbook.close()

        # Salvando os dados em um arquivo binário
        with open(PATH_TO_BIN_FILE, 'wb') as arquivo:
            pickle.dump(dicionario, arquivo)

    else:

        # Carrega os dados salvos em um arquivo binário
        with open(PATH_TO_BIN_FILE, 'rb') as arquivo:
            dicionario = pickle.load(arquivo)

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
    
# Retira pontos e deixa a palavra em maiúsculo
def limpa_resposta(resposta):
    # Remove o caractere da string
    resposta_limpa = resposta.replace('.', '')

    # Torna toda a string em maiúsculas
    resposta_limpa = resposta_limpa.upper()

    return resposta_limpa 

def busca_categoria_com_ai(lista_de_registros):

    for registro in lista_de_registros:
        if registro['categoria'] == 'minha_categoria':

            # [ ] Voltar a buscar chamar a LLM agrupada (que não funcionava bem) ao invés de unitariamente
            
            registro_para_ai = registro['item']
            prompt = ai.prepara_prompt(registro_para_ai)
            resposta = ai.interagir_com_llm(prompt)
            resposta_limpa = limpa_resposta(resposta)
            registro['categoria'] = resposta_limpa
            registro['source'] = "ai_gpt"
            print("[GPT] Encontrei a categoria " + resposta_limpa + " para o estabelecimento " + registro_para_ai)