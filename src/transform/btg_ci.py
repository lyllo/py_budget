from datetime import datetime
import category
import load.files as files
import load.load as load
import os
import configparser

# Caminho do arquivo atual
current_file_path = os.path.abspath(__file__)

# Caminho da raiz do projeto
ROOT_DIR = os.path.abspath(os.path.join(current_file_path, "../../.."))

# Caminho para arquivo de configuração
PATH_TO_CONFIG_FILE = os.path.join(ROOT_DIR, 'config.ini')
PATH_TO_FINAL_OUTPUT_FILE = os.path.join(ROOT_DIR, 'out\\final.xlsx')

MEIO = "BTG Investimentos"



"""
  ______                /\/|                                _ _ _                     
 |  ____|              |/\/                 /\             (_) (_)                    
 | |__ _   _ _ __   ___ ___   ___  ___     /  \  _   ___  ___| |_  __ _ _ __ ___  ___ 
 |  __| | | | '_ \ / __/ _ \ / _ \/ __|   / /\ \| | | \ \/ / | | |/ _` | '__/ _ \/ __|
 | |  | |_| | | | | (_| (_) |  __/\__ \  / ____ \ |_| |>  <| | | | (_| | | |  __/\__ \
 |_|   \__,_|_| |_|\___\___/ \___||___/ /_/    \_\__,_/_/\_\_|_|_|\__,_|_|  \___||___/
                    )_)                                                               

"""

# Converter strings no formato dd/mmm para variáveis do tipo datetime no formato aaaa-mm-dd
def limpar_data(str_data):
    dia = int(str_data[0:2])
    mes = int(str_data[3:5])
    ano = int(str_data[6:10])

    data_datetime = datetime(ano, mes, dia).date()

    return data_datetime

# Converter strings no formato - R$xx,xx para variáveis do tipo float no formato xx,xx
def limpar_valor(str_tipo, str_valor):
    multiplicador = 0
    if str_tipo == 'Crédito':
        multiplicador = 1
    elif str_tipo == 'Débito':
        multiplicador = -1
    
    float_valor = "{:.2f}".format(multiplicador * float(str_valor.replace(".","").replace(",",".")))
    
    return float(float_valor)

# Encontrar posições de uma string dentro de outra string, armazenando os resultados em uma lista
def encontrar_todas_ocorrencias(s, sub):
    start = 0
    positions = []  # Lista para armazenar as posições
    while True:
        start = s.find(sub, start)
        if start == -1: 
            return positions  # Retorna a lista de posições
        positions.append(start)
        start += len(sub)  # use start += 1 to find overlapping matches

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

def init(input_file, output_file):

    # Carrega o arquivo de entrada com as transações de cartões do BTG
    linhas_arquivo = files.ler_arquivo(input_file)

    # Declara contador de linha e lista de registros
    num_linha = 0
    lista_de_registros = []

    # Lê as linhas do arquivo para tratamento dos dados
    for linha in linhas_arquivo:

        # Criar um novo registro com valores padrões
        novo_registro = {'data': '', 
                         'item': '',
                         'detalhe': '',
                         'ocorrencia_dia': '', 
                         'valor': '',  
                         'categoria': '',
                         'tag': '',
                         'categoria_fonte': ''}

        # Busca a posição do primeiro separador
        posicoes = encontrar_todas_ocorrencias(linha, '\t')

        # Armazena os caracteres que representam a data da tramsação no formato dd/mm/aaaa
        str_data = linha[:posicoes[0]]
        
        # Armazena os caracteres que representam a descrição da transação (= item)
        str_item = linha[posicoes[0]+1:posicoes[1]]
        
        # Armazena os caracteres que representam o tipo da transação (crédito ou débito)
        str_tipo = linha[posicoes[1]+1:posicoes[2]]

        # Armazena os caracteres que representam o valor da transação no formato xxx.xxx,xx
        str_valor = linha[posicoes[2]+1:posicoes[3]]

        # Transforma a data do tipo 'string' para o tipo 'date'
        date_data = limpar_data(str_data)

        # Armazena o valor da chave 'data' com a data já no tipo 'date'
        novo_registro['data'] = date_data

        # Armazena o valor da chave 'item' com o item já no tipo 'string'
        novo_registro['item'] = str_item

        # Transforma o valor do tipo 'string' para o tipo 'float'
        float_valor = limpar_valor(str_tipo, str_valor)  

        # Armazena o valor da chave 'valor' com o valor já no tipo 'float'
        novo_registro['valor'] = float_valor

        # Armazenar o novo registro na lista de registros
        lista_de_registros.append(novo_registro)

        num_linha += 1

    # Preenche as categorias das transações
    category.fill(lista_de_registros)

    # Carrega os dados em db e/ou arquivo
    load.init(input_file, lista_de_registros, MEIO, output_file, PATH_TO_FINAL_OUTPUT_FILE)