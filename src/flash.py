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
PATH_TO_INPUT_FILE = os.path.join(ROOT_DIR, 'in\\flash.txt')
PATH_TO_OUTPUT_FILE = os.path.join(ROOT_DIR, 'out\\flash.xlsx')

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
    
# Converter strings no formato dd/mmm para variáveis do tipo datetime no formato aaaa-mm-dd
def limpar_data(linha):
    dia = int(linha[0:2])
    mes = int(linha[3:5])
    ano = int(linha[6:10])

    data_datetime = datetime(ano, mes, dia).date()

    return data_datetime

# Converter strings no formato - R$xx,xx para variáveis do tipo float no formato xx,xx
def limpar_valor(linha):
    valor_float = "{:.2f}".format(-1 * float(linha[5:].replace(".","").replace(",",".")))
    valor_string = str(valor_float).replace(".",",")
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

# Carrega o arquivo de entrada com as transações de cartões do BTG
linhas_arquivo = files.ler_arquivo(PATH_TO_INPUT_FILE)

# Declara contador de linha e lista de registros
num_linha = 0
lista_de_registros = []

# Lê as linhas do arquivo para tratamento dos dados
for linha in linhas_arquivo:

    # [ ] Tornar a busca por data mais abrangente
    
    data = ''

    # Encontra uma linha de data em Outubro ou Novembro
    if linha.find("2023") != -1:
        
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
            
        novo_registro['valor'] = limpar_valor(linhas_arquivo[num_linha+2])

        # Armazenar o novo registro na lista de registros
        lista_de_registros.append(novo_registro)

    num_linha += 1

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