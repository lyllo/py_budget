import os
import sys
import configparser
from datetime import datetime

# Caminho do arquivo atual
current_file_path = os.path.abspath(__file__)

# Caminho da raiz do projeto
ROOT_DIR = os.path.abspath(os.path.join(current_file_path, "../../.."))

sys.path.append(ROOT_DIR)

from imports import *
import category
import load.files as files
import load.db as db

# Caminho para arquivo de configuração
PATH_TO_CONFIG_FILE = os.path.join(ROOT_DIR, 'config.ini')

PATH_TO_FINAL_OUTPUT_FILE = os.path.join(ROOT_DIR, 'out\\final.xlsx')

MEIO = "Conta BTG"

# Lê as feature toggles do arquivo de configuração
config = configparser.ConfigParser()
config.read(PATH_TO_CONFIG_FILE)

toggle_db = config.get('Toggle', 'toggle_db')
toggle_temp_sheet = config.get('Toggle', 'toggle_temp_sheet')
toggle_final_sheet = config.get('Toggle', 'toggle_final_sheet')



"""
  ______                /\/|                                _ _ _                     
 |  ____|              |/\/                 /\             (_) (_)                    
 | |__ _   _ _ __   ___ ___   ___  ___     /  \  _   ___  ___| |_  __ _ _ __ ___  ___ 
 |  __| | | | '_ \ / __/ _ \ / _ \/ __|   / /\ \| | | \ \/ / | | |/ _` | '__/ _ \/ __|
 | |  | |_| | | | | (_| (_) |  __/\__ \  / ____ \ |_| |>  <| | | | (_| | | |  __/\__ \
 |_|   \__,_|_| |_|\___\___/ \___||___/ /_/    \_\__,_/_/\_\_|_|_|\__,_|_|  \___||___/
                    )_)                                                               

"""

# Substituir mes
def obter_numero_mes(mes):
    meses = {
        'jan': 1,
        'fev': 2,
        'mar': 3,
        'abr': 4,
        'mai': 5,
        'jun': 6,
        'jul': 7,
        'ago': 8,
        'set': 9,
        'out': 10,
        'nov': 11,
        'dez': 12
    }
    return meses.get(mes.lower(), None)

# Obter o número de parcelas de uma transação
def obter_numero_parcelas(linha):
    posicao_x = linha.find('x', 21)
    parcelas = linha[21:posicao_x]
    return parcelas
   
# Converter strings no formato dd/mmm para variáveis do tipo datetime no formato aaaa-mm-dd
def limpar_data(linha):

    data_string = linha

    # [x] Habilitar virada de 1 ano
    ano_atual = True
    if data_string.count('/') == 2:
        ano_atual = False

    if ano_atual:
        if len(data_string) != 6:
            data_string = linha[-6:]
        else:
            data_string = linha # 26/Dez
        
        ano = datetime.now().year
        mes = obter_numero_mes(data_string[3:].lower())
        dia = int(data_string[:2])

    else:
        if len(data_string) != 11:
            data_string = linha[-11:]
        else:
            data_string = linha # 26/Dez/2023

        ano = datetime.now().year - 1
        mes = obter_numero_mes(data_string[3:6].lower())   
        dia = int(data_string[:2])

    # [x] Permitir outros anos, além de 2023
    data_datetime = datetime(ano, mes, dia).date()

    return data_datetime

# Converter strings no formato - R$xx,xx para variáveis do tipo float no formato xx,xx
def limpar_valor(linha):
    valor_float = "{:.2f}".format(-1 * float(linha[5:].replace(".","").replace(",",".")))
    return float(valor_float)

def encontra_linha_de_data(linha):
    if linha.find("/Jan") != -1 or linha.find("/Fev") != -1 or linha.find("/Mar") != -1 or linha.find("/Abr") != -1 or linha.find("/Mai") != -1 or linha.find("/Jun") != -1 or linha.find("/Jul") != -1 or linha.find("/Ago") != -1 or linha.find("/Set") != -1 or linha.find("/Out") != -1 or linha.find("/Nov") != -1 or linha.find("/Dez") != -1:
        return True
    else:
        return False

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

    # Marcador para linhas de pagamento de fatura
    compra_buffer = False

    # Lê as linhas do arquivo para tratamento dos dados
    for linha in linhas_arquivo:
       
        # Encontra uma linha de data em Outubro ou Novembro
        if encontra_linha_de_data(linha):
            
            # Armazenar o valor da última data encontrada
            data = limpar_data(linha)

        # [ ] Evoluir para capturar transações de Conta
        # Encontra uma linha de transação de Cartão
        if linha.find("Pix ") != -1 or linha.find("Pagamento ") != -1:

            # Criar um novo registro com valores padrões
            novo_registro = {'data': '', 
                             'item': '',
                             'detalhe': '',
                             'ocorrencia_dia': '', 
                             'valor': '',  
                             'cartao': '',  
                             'parcela': '',
                             'categoria': '',
                             'tag': '',
                             'categoria_fonte': ''}

            # Define o valor da chave 'data' com a última data encontrada
            novo_registro['data'] = data

            # Define o valor da chave 'item' com o item encontrado (linha anterior)
            novo_registro['item'] = linhas_arquivo[num_linha-1]

            # Definir o valor da chave 'valor' com o valor encontrado (próxima linha)
            novo_registro['valor'] = limpar_valor(linhas_arquivo[num_linha+1])

            lista_de_registros.append(novo_registro)
            
        num_linha += 1

    # Preenche as categorias das transações
    category.fill(lista_de_registros)

    # Salva dados no banco
    if(toggle_db == "true"):
        print(f"\nIniciando 'load' do {MEIO} em db...")
        file_timestamp = files.get_modification_time(input_file)
        timestamp = db.salva_registros(lista_de_registros, MEIO, os.path.basename(input_file), file_timestamp)

    else:
        timestamp = int(datetime.timestamp(datetime.now()))

    # Salva as informações em um arquivo Excel temporário
    if(toggle_temp_sheet == "true"):

        nome_arquivo = output_file
        print(f"\nIniciando 'load' do {MEIO} em xlsx temporário...")
        files.salva_excel_temporario(nome_arquivo, MEIO, timestamp)

    # Salva as informações em um arquivo Excel final
    if(toggle_final_sheet == "true"):

        nome_arquivo = PATH_TO_FINAL_OUTPUT_FILE
        print(f"\nIniciando 'load' do {MEIO} em xlsx final...")
        files.salva_excel_final(nome_arquivo, MEIO, timestamp)