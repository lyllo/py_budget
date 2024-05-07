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
import installments

# Caminho para arquivo de configuração
PATH_TO_CONFIG_FILE = os.path.join(ROOT_DIR, 'config.ini')

PATH_TO_FINAL_OUTPUT_FILE = os.path.join(ROOT_DIR, 'out\\final.xlsx')

MEIO = "Cartão BTG"

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
    multiplicador = -1
    offset_valor = 4
    if linha.find("-") == -1:
        multiplicador = 1
        offset_valor = 3
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

        # [x] Evoluir para capturar transações de Conta
        # Encontra uma linha de transação de Cartão
        if linha.find("Compra ") != -1:

            compra_buffer = True

            if linha.find("não autorizada") == -1:
                unnautorized = True
            else:
                unnautorized = False

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

            # Define o valor da chave 'cartao' com o nome do portador (igual o da XP)
            if linha.find("CINTHIA") != -1:
                novo_registro['cartao'] = 'CINTHIA ROSA'
            else:
                novo_registro['cartao'] = 'PHILIPPE Q ROSA'

            # Armazena o número de parcelas da compra para posterior criação dos registros de forma separada
            if linha.find("Compra no crédito em ") != -1:
                parcelas = int(obter_numero_parcelas(linha))
            else:
                parcelas = 1
                novo_registro['parcela'] = "1/1"
            
        # Encontra uma linha de valor
        if linha.find("- R$ ", 0, 5) != -1 and compra_buffer == True:

            # Definir o valor da chave 'valor' com o valor encontrado
            novo_registro['valor'] = limpar_valor(linha)/parcelas

            # Verifica se valor é zerado e status é autorizado
            if novo_registro['valor'] != 0 and unnautorized != False:

                if parcelas == 1:
                    # Armazenar o novo registro de parcela única na lista de registros
                    lista_de_registros.append(novo_registro)
                    compra_buffer = False

                else:
                    # Armazena os registros referentes a todas as parcelas na lista de registros
                    for parcela in range (1, parcelas+1):
                        
                        # Armazena a data da primeira parcela
                        if (parcela == 1):
                            data_base = novo_registro['data']
                        
                        data_parcela = installments.calcula_data_parcela(data_base, parcela)
                        
                        nova_parcela = {'data': novo_registro['data'], 
                                        'item': novo_registro['item'],
                                        'detalhe': '',
                                        'ocorrencia_dia': '', 
                                        'valor': novo_registro['valor'],  
                                        'cartao': novo_registro['cartao'],  
                                        'parcela': '',
                                        'categoria': '',
                                        'tag': '',
                                        'categoria_fonte': ''}
                        
                        nova_parcela['data'] = data_parcela
                        nova_parcela['parcela'] = str(parcela) + "/" + str(parcelas)
                        lista_de_registros.append(nova_parcela)
                        compra_buffer = False

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
        files.salva_excel(nome_arquivo, MEIO, timestamp)

    # Salva as informações em um arquivo Excel final
    if(toggle_final_sheet == "true"):

        nome_arquivo = PATH_TO_FINAL_OUTPUT_FILE
        print(f"\nIniciando 'load' do {MEIO} em xlsx final...")
        files.salva_excel(nome_arquivo, "Summary", timestamp)