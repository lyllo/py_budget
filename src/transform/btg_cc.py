import os
import sys
import configparser
from datetime import datetime
import category
import load.files as files
import load.load as load

# Caminho do arquivo atual
current_file_path = os.path.abspath(__file__)

# Caminho da raiz do projeto
ROOT_DIR = os.path.abspath(os.path.join(current_file_path, "../../.."))

sys.path.append(ROOT_DIR)

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

verbose = config.get('Toggle', 'verbose')

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
    multiplicador = -1
    offset_valor = 4
    if linha.find("-") == -1:
        multiplicador = 1
        offset_valor = 4 # É igual a 3 quando faz copy/paste manual
    valor_float = "{:.2f}".format(multiplicador * float(linha[offset_valor:].replace(".","").replace(",",".")))
    return float(valor_float)

def encontra_linha_de_data(linha):
    linha_lower = linha.lower()
    if linha_lower.find("/jan") != -1 or linha_lower.find("/fev") != -1 or linha_lower.find("/mar") != -1 or linha_lower.find("/abr") != -1 or linha_lower.find("/mai") != -1 or linha_lower.find("/jun") != -1 or linha_lower.find("/jul") != -1 or linha_lower.find("/ago") != -1 or linha_lower.find("/set") != -1 or linha_lower.find("/out") != -1 or linha_lower.find("/nov") != -1 or linha_lower.find("/dez") != -1:
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

        # Encontra uma linha de transação de Conta
        if linha.find("Pix ") != -1 or linha.find("Pagamento ") != -1 or linha.find("Transferência ") != -1:

            if linha.find("Pix ") != -1:
                detalhe = "Pix"
            elif linha.find("Pagamento ") != -1:
                detalhe = "Pagamento"
            elif  linha.find("Transferência ") != -1:
                detalhe = "Transferência"

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

            # Define o detalhe com o tipo de operação (Transferência, Pagamento ou PIX)
            novo_registro['detalhe'] = detalhe

            lista_de_registros.append(novo_registro)
            
        num_linha += 1

    # Preenche as categorias das transações
    category.fill(lista_de_registros)
    
    # Carrega os dados em db e/ou arquivo
    load.init(input_file, lista_de_registros, MEIO, output_file, PATH_TO_FINAL_OUTPUT_FILE)