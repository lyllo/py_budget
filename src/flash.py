from datetime import datetime
import category
import files
import db
import os
import configparser

# Configura os paths dos arquivos que serão utilizados
ROOT_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

PATH_TO_CONFIG_FILE = os.path.join(ROOT_DIR, 'config.ini')

# Lê as feature toggles do arquivo de configuração
config = configparser.ConfigParser()
config.read(PATH_TO_CONFIG_FILE)

toggle_db = config.get('Toggle', 'toggle_db')

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
def limpar_data(linha):
    dia = int(linha[0:2])
    mes = int(linha[3:5])
    ano = int(linha[6:10])

    data_datetime = datetime(ano, mes, dia).date()

    return data_datetime

# Converter strings no formato - R$xx,xx para variáveis do tipo float no formato xx,xx
def limpar_valor(valor, item):
    multiplicador = -1
    if item == 'Depósito De Refeição E Alimentação':
        multiplicador = 1
    valor_float = "{:.2f}".format(multiplicador * float(valor[4:].replace(".","").replace(",",".")))
    return float(valor_float)

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

        # [x] Tornar a busca por data mais abrangente
        
        data = ''

        # Encontra uma linha de data
        if linha.find(" às ") != -1:
            
            # Armazenar o valor da última data encontrada
            data = linha[:10]

            # Criar um novo registro com valores padrões
            novo_registro = {'data': '', 
                            'item': '', 
                            'valor': '', 
                            'categoria': '',
                            'tag': '',
                            'source': ''}

            # Define o valor da chave 'data' com a última data encontrada
            novo_registro['data'] = limpar_data(data)

            # Define o valor da chave 'item' com o item encontrado (linha anterior)
            novo_registro['item'] = linhas_arquivo[num_linha-2]
                
            novo_registro['valor'] = limpar_valor(linhas_arquivo[num_linha+2], novo_registro['item'])

            # Armazenar o novo registro na lista de registros
            lista_de_registros.append(novo_registro)

        num_linha += 1

    # Preenche as categorias das transações
    category.fill(lista_de_registros)

    # Salva dados no banco
    if(toggle_db == "true"):
        db.salva(lista_de_registros, "Cartao_Flash")

    # Transforma a lista de dicionários em uma lista de listas, sem os nomes das chaves
    lista_de_listas = [list(item.values()) for item in lista_de_registros]

    # Adiciona o cabeçalho à lista de listas
    lista_de_listas.insert(0, ['DATA', 'ITEM', 'VALOR', 'CATEGORIA', 'TAG', 'SOURCE'])

    # Salva as informações em um arquivo Excel
    nome_arquivo = output_file		
    files.incluir_linhas_em_excel(nome_arquivo, lista_de_listas)