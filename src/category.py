from openpyxl import load_workbook
from fuzzywuzzy import fuzz
import pickle
import configparser
import os
import ai
from datetime import datetime

# Configura os paths dos arquivos que serão utilizados
ROOT_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)
PATH_TO_CONFIG_FILE = os.path.join(ROOT_DIR, 'config.ini')
PATH_TO_HISTORY_FILE = os.path.join(ROOT_DIR, 'data\\history.xlsx')
PATH_TO_BIN_FILE = os.path.join(ROOT_DIR, 'data\\dados.bin')

# limite de similaridade, valor de 75 encontrado por inspeção manual
limite = 75

# Le as feature toggles do arquivo de configuração
config = configparser.ConfigParser()
config.read(PATH_TO_CONFIG_FILE)
load_xlsx = config.get('Toggle', 'load_xlsx')
simple_match = config.get('Toggle', 'simple_match')
similar_match = config.get('Toggle', 'similar_match')
ai_match = config.get('Toggle', 'ai_match')
verbose = config.get('Toggle', 'verbose')

# 
# BUSCA SIMPLES (ANÁLISE LÉXICA)
#

# Carrega as colunas do Excel referentes a ITEM e CATEGORIA
def carrega_dicionario():

    # Cria um dicionário vazio
    dicionario = {}

    if(load_xlsx == "true"): # [ ] Está sendo chamado para todas as fontes de dados que estejam com toggle ativo

        # Carrega o arquivo Excel history com transações até o mês passado
        workbook = load_workbook(PATH_TO_HISTORY_FILE)

        # Seleciona a planilha Summary desejada
        worksheet = workbook['Summary']

        # Percorre as células das colunas B e D iniciando pela linha 2, onde B = Item e D = Categoria.
        # Exemplo ["iFood" = "Alimentação"]
        for row in worksheet.iter_rows(min_row=2, values_only=True):
            chave = row[1]
            valor = row[7]
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
            registro['categoria_fonte'] = "ai_gpt"
            if(verbose == "true"):
                print("[GPT] Encontrei a categoria " + resposta_limpa + " para o estabelecimento " + registro_para_ai)

def fill(lista_de_registros):

    # Busca por categorias
    if (simple_match == "true"):

        # Imprime timestamp do início do carregamento do dicionário de categorias
        if(verbose == "true"):
            print("[" + datetime.now().strftime("%H:%M:%S") +"] Iniciando carregamento do dicionário...")

        # Carrega dicionário de categorias
        lista_de_categorias = carrega_dicionario()

        # Imprime timestamp do término do carregamento do dicionário
        if(verbose == "true"):
            print("[" + datetime.now().strftime("%H:%M:%S") +"] Dicionário carregado em memória.")

        num_simple_matches = 0
        num_similar_matches = 0

        for registro in lista_de_registros:

            registro['categoria_fonte'] = ''
            
            # Faz a busca exata
            if registro['item'] in lista_de_categorias:
                registro['categoria'] = lista_de_categorias[registro['item']]
                registro['categoria_fonte'] = 'history_exact'
                num_simple_matches += 1
            
            # Faz a busca por similaridade
            else:
                if(similar_match == "true"):
                    
                    palavras_parecidas = busca_palavras_parecidas(registro['item'], lista_de_categorias.keys(), limite)
                    
                    # só estamos interessados quando a busca encontra apenas 1 elemento e não mais de 1
                    if len(palavras_parecidas) == 1:
                        
                        registro['categoria'] = lista_de_categorias[palavras_parecidas[0]]
                        registro['categoria_fonte'] = 'history_similar'
                        num_similar_matches += 1

        if (simple_match == "true"):
            if(verbose == "true"):
                print(str(num_simple_matches) + " simple matches em " + str(len(lista_de_registros)) + " registros, eficiência de " + str(round(100*(num_simple_matches/len(lista_de_registros)),2)) + "%.")

        if (similar_match == "true"):
            if(verbose == "true"):
                print(str(num_similar_matches) + " similar matches quando limite = " + str(limite) + " em " + str(len(lista_de_registros)) + " registros, eficiência de " + str(round(100*(num_similar_matches/len(lista_de_registros)),2)) + "%.")

    # Faz a busca com ai

    if (ai_match == "true"):
        busca_categoria_com_ai(lista_de_registros)