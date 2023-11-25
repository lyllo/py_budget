from datetime import datetime
import configparser
import os
import category
import files

# Configura os paths dos arquivos que serão utilizados
ROOT_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)
PATH_TO_CONFIG_FILE = os.path.join(ROOT_DIR, 'config.ini')
PATH_TO_INPUT_FILE = os.path.join(ROOT_DIR, 'in\\gpa.xls')
PATH_TO_OUTPUT_FILE = os.path.join(ROOT_DIR, 'out\\gpa.xlsx')
WORKSHEET_NAME = 'Lançamentos'

# Le as feature toggles do arquivo de configuração
config = configparser.ConfigParser()
config.read(PATH_TO_CONFIG_FILE)
simple_match = config.get('Toggle', 'simple_match')
similar_match = config.get('Toggle', 'similar_match')
ai_match = config.get('Toggle', 'ai_match')

"""
  ______                /\/|                                _ _ _                     
 |  ____|              |/\/                 /\             (_) (_)                    
 | |__ _   _ _ __   ___ ___   ___  ___     /  \  _   ___  ___| |_  __ _ _ __ ___  ___ 
 |  __| | | | '_ \ / __/ _ \ / _ \/ __|   / /\ \| | | \ \/ / | | |/ _` | '__/ _ \/ __|
 | |  | |_| | | | | (_| (_) |  __/\__ \  / ____ \ |_| |>  <| | | | (_| | | |  __/\__ \
 |_|   \__,_|_| |_|\___\___/ \___||___/ /_/    \_\__,_/_/\_\_|_|_|\__,_|_|  \___||___/
                    )_)                                                               

"""

# Converter strings no formato dd/mm/aaaa para variáveis do tipo datetime no formato aaaa-mm-dd
def limpar_data(str_data):
    dia = int(str_data[0:2])
    mes = int(str_data[3:5])
    ano = int(str_data[6:10])

    data_datetime = datetime(ano, mes, dia).date()

    return data_datetime

"""

  _____       __     _             _          _____           _       _   
 |_   _|     /_/    (_)           | |        / ____|         (_)     | |  
   | |  _ __  _  ___ _  ___     __| | ___   | (___   ___ _ __ _ _ __ | |_ 
   | | | '_ \| |/ __| |/ _ \   / _` |/ _ \   \___ \ / __| '__| | '_ \| __|
  _| |_| | | | | (__| | (_) | | (_| | (_) |  ____) | (__| |  | | |_) | |_ 
 |_____|_| |_|_|\___|_|\___/   \__,_|\___/  |_____/ \___|_|  |_| .__/ \__|
                                                               | |        
                                                               |_|        

"""

# Declara contador de linha e lista de registros
lista_de_registros = []
offset = False

# Lê as linhas do arquivo para tratamento dos dados
for linha in files.ler_arquivo_xls(PATH_TO_INPUT_FILE):

    if (offset == True) and (linha[3] != ''):

        # Cria um novo registro com valores nulos
        novo_registro = {'data': '', 
                            'item': '', 
                            'valor': '', 
                            'categoria': '',
                            'tag': '',
                            'source': ''}

        # Armazena os caracteres que representam a data da tramsação no formato dd/mm/aaaa [Coluna A]
        str_data = linha[0]
        
        # Armazena os caracteres que representam a descrição da transação (= item) [Coluna B]
        str_item = linha[1]
        
        # Armazena os caracteres que representam o valor da transação no formato xxx.xxx,xx [Coluna D]
        float_valor = linha[3]

        # Transforma a data do tipo 'string' para o tipo 'date'
        date_data = limpar_data(str_data)

        # Armazena o valor da chave 'data' com a data já no tipo 'date'
        novo_registro['data'] = date_data

        # Armazena o valor da chave 'item' com o item já no tipo 'string'
        novo_registro['item'] = str_item

        # Armazena o valor da chave 'valor' com o valor já no tipo 'float'
        novo_registro['valor'] = float_valor

        # Armazenar o novo registro na lista de registros
        lista_de_registros.append(novo_registro)

    # Encontra a linha que antecede as transações (Coluna D = 'valor')
    if (linha[3] == 'valor'):
        offset = True

    # Encontra a linha que procede as transações (Coluna D = '')
    if (offset == True) and (linha[3] == ''):
        offset = False

# Busca por categorias
if (simple_match == "true"):

    # Imprime timestamp do início do carregamento do dicionário de categorias
    print("[" + datetime.now().strftime("%H:%M:%S") +"] Iniciando carregamento do dicionário...")

    # Carrega dicionário de categorias
    lista_de_categorias = category.carrega_dicionario()

    # Imprime timestamp do término do carregamento do dicionário
    print("[" + datetime.now().strftime("%H:%M:%S") +"] Dicionário carregado em memória.")

    num_simple_matches = 0
    num_similar_matches = 0

    for registro in lista_de_registros:
        
        # Faz a busca exata
        if registro['item'] in lista_de_categorias:
            registro['categoria'] = lista_de_categorias[registro['item']]
            registro['source'] = 'history_exact'
            num_simple_matches += 1
        
        # Faz a busca por similaridade
        else:
            if(similar_match == "true"):
                
                # limite de similaridade, valor de 75 encontrado por inspeção manual
                limite = 75
                palavras_parecidas = category.busca_palavras_parecidas(registro['item'], lista_de_categorias.keys(), limite)
                
                # só estamos interessados quando a busca encontra apenas 1 elemento e não mais de 1
                if len(palavras_parecidas) == 1:
                    
                    # print("As palavras parecidas com " + registro['item'] + " são:")
                    # print(palavras_parecidas[0] + " : " + categorias[palavras_parecidas[0]])
                    registro['categoria'] = lista_de_categorias[palavras_parecidas[0]]
                    registro['source'] = 'history_similar'
                    num_similar_matches += 1

    if (simple_match == "true"):
        print(str(num_simple_matches) + " simple matches em " + str(len(lista_de_registros)) + " registros, eficiência de " + str(round(100*(num_simple_matches/len(lista_de_registros)),2)) + "%.")

    if (similar_match == "true"):
        print(str(num_similar_matches) + " similar matches quando limite = " + str(limite) + " em " + str(len(lista_de_registros)) + " registros, eficiência de " + str(round(100*(num_similar_matches/len(lista_de_registros)),2)) + "%.")

# Faz a busca com ai

if (ai_match == "true"):
    category.busca_categoria_com_ai(lista_de_registros)

# Transforma a lista de dicionários em uma lista de listas, sem os nomes das chaves
lista_de_listas = [list(item.values()) for item in lista_de_registros]

# Adiciona o cabeçalho à lista de listas
lista_de_listas.insert(0, ['DATA', 'ITEM', 'VALOR', 'CATEGORIA', 'TAG', 'SOURCE'])

# Salva as informações em um arquivo Excel
nome_arquivo = PATH_TO_OUTPUT_FILE		
files.incluir_linhas_em_excel(nome_arquivo, lista_de_listas)