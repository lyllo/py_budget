from openpyxl import Workbook
from datetime import datetime
from openpyxl.styles import Font
from openpyxl.styles import numbers
import category
import configparser
import os

# Configura os paths dos arquivos que serão utilizados
ROOT_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)
PATH_TO_CONFIG_FILE = os.path.join(ROOT_DIR, 'config.ini')
PATH_TO_INPUT_FILE = os.path.join(ROOT_DIR, 'in\\btg.txt')
PATH_TO_OUTPUT_FILE = os.path.join(ROOT_DIR, 'out\\btg.xlsx')

# Le as feature toggles do arquivo de configuração
config = configparser.ConfigParser()
config.read(PATH_TO_CONFIG_FILE)
simple_match = config.get('Toggle', 'simple_match')
similar_match = config.get('Toggle', 'similar_match')
ai_match = config.get('Toggle', 'ai_match')

# Inclui linhas em arquivo Excel
def incluir_linhas_em_excel(nome_arquivo, linhas):
    # Cria um novo arquivo do Excel
    workbook = Workbook()
    
    # Seleciona a planilha ativa
    sheet = workbook.active

    # Inicializa o contador de linhas da planilha
    num_linha_excel = 1

    # Inclui as linhas no arquivo do Excel
    for linha in linhas:
        sheet.append(linha)
        
        # Formata como moeda em BRL a coluna C (3) do VALOR
        for cell in sheet[num_linha_excel]:
            if cell.column == 3:
                cell.number_format = 'R$ #,##0.00'

        # Pintar de vermelho a fonte das células das categorias preenchidas por AI
        if 'ai_gpt' in linha:
            for cell in sheet[num_linha_excel]:
                # A coluna F (6) é da CATEGORIA
                if cell.column == 6:
                    # print("Vou pintar a célula da linha " + str(num_linha_excel) + " e coluna " + str(cell.column))
                    cell.font = Font(color='FF0000')

        num_linha_excel += 1

    # Salva o arquivo do Excel
    workbook.save(nome_arquivo)

# Carregar arquivo de texto
def ler_arquivo(nome_arquivo):
    linhas = []
    with open(nome_arquivo, 'r', -1, 'utf-8') as arquivo:
        for linha in arquivo:
            linhas.append(linha.strip())
    return linhas

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
    
# Converter strings no formato dd/mmm para variáveis do tipo datetime no formato aaaa-mm-dd
def limpar_data(linha):
    data_string = linha
    if len(data_string) != 6:
        data_string = linha[-6:]
    else:
        data_string = linha

    mes = obter_numero_mes(data_string[-3:].lower())

    # TODO: Permitir outros anos, além de 2023
    data_datetime = datetime(2023, mes, int(data_string[:2])).date()

    return data_datetime

# Converter strings no formato - R$xx,xx para variáveis do tipo float no formato xx,xx
def limpar_valor(linha):
    valor_float = "{:.2f}".format(-1 * float(linha[5:].replace(".","").replace(",",".")))
    valor_string = str(valor_float).replace(".",",")
    return float(valor_float)

# Carregar o arquivo banking.txt com as transações de cartões do BTG
linhas_arquivo = ler_arquivo(PATH_TO_INPUT_FILE)

# Declarar contador de linha e lista de registros
num_linha = 0
lista_de_registros = []

for linha in linhas_arquivo:

    # TODO: Tornar a busca por data mais abrangente
    # Encontrar uma linha de data em Outubro ou Novembro
    if (linha.find("/Out") != -1 or linha.find("/Nov") != -1):
        
        # Armazenar o valor da última data encontrada
        data = limpar_data(linha)

    # Encontrar uma linha de status
    if linha.find("Compra ") != -1:

        # Criar um novo registro com valores padrões
        novo_registro = {'data': 'minha_data', 
                         'item': 'meu_item', 
                         'valor': 'meu_valor', 
                         'cartao': 'meu_cartao', 
                         'parcelas': 'minhas_parcelas',
                         'categoria': 'minha_categoria',
                         'tag': 'minha_tag',
                         'source': 'minha_fonte'}

        # Definir o valor da chave 'data' com a última data encontrada
        novo_registro['data'] = data

        # Definir o valor da chave 'item' com o item encontrado (linha anterior)
        novo_registro['item'] = linhas_arquivo[num_linha-1]

        # Definir o valor da chave 'cartao' com o nome do portador
        if linha.find("CINTHIA") != -1:
            novo_registro['cartao'] = 'CINTHIA'
        else:
            novo_registro['cartao'] = 'PHILIPPE'

        # Definir o valor da chave 'parcelas' com o número de parcelas da compra
        if linha.find("Compra no crédito em ") != -1:
            novo_registro['parcelas'] = "1/" + linha[21]
        else:
            novo_registro['parcelas'] = "1/1"
        
    # Encontrar uma linha de valor
    if linha.find("- R$", 0, 4) != -1:

        # Definir o valor da chave 'valor' com o valor encontrado
        novo_registro['valor'] = limpar_valor(linha)

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
        # busca exata
        if registro['item'] in lista_de_categorias:
            registro['categoria'] = lista_de_categorias[registro['item']]
            registro['source'] = 'history_exact'
            num_simple_matches += 1
        
        # busca por similaridade
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

# busca com ai

if (ai_match == "true"):
    category.busca_categoria_com_ai(lista_de_registros)

# Transformar a lista de dicionários em uma lista de listas, sem os nomes das chaves
lista_de_listas = [list(item.values()) for item in lista_de_registros]

# Adicionar cabeçalho a lista de listas
lista_de_listas.insert(0, ['DATA', 'ITEM', 'VALOR', 'CARTAO', 'PARCELAS', 'CATEGORIA', 'TAG', 'SOURCE'])

# Salvar as informações em um arquivo Excel
nome_arquivo = PATH_TO_OUTPUT_FILE		
incluir_linhas_em_excel(nome_arquivo, lista_de_listas)