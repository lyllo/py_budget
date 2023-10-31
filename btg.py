from openpyxl import Workbook
from datetime import datetime

def incluir_linhas_em_excel(nome_arquivo, linhas):
    # Cria um novo arquivo do Excel
    workbook = Workbook()
    
    # Seleciona a planilha ativa
    sheet = workbook.active

    # Inclui as linhas no arquivo do Excel
    for linha in linhas:
        sheet.append(linha)

    # Salva o arquivo do Excel
    workbook.save(nome_arquivo)

# Carregar arquivo de texto
def ler_arquivo(nome_arquivo):
    linhas = []
    with open(nome_arquivo, 'r', -1, 'utf-8') as arquivo:
        for linha in arquivo:
            linhas.append(linha.strip())
    return linhas

# Converter strings no formato dd/Out para variáveis do tipo datetime no formato aaaa-mm-dd
def limpar_data(linha):
    data_string = linha
    if len(data_string) != 6:
        data_string = linha[-6:]
    else:
        data_string = linha
        
    data_datetime = datetime(2023, 10, int(data_string[:2])).date()

    return data_datetime


# Converter strings no formato - R$xx,xx para variáveis do tipo float no formato xx,xx
def limpar_valor(linha):
    valor_float = "{:.2f}".format(-1 * float(linha[5:].replace(".","").replace(",",".")))
    valor_string = str(valor_float).replace(".",",")
    return valor_string

# Carregar o arquivo banking.txt com as transações de cartões do BTG
nome_arquivo = 'C:\\Users\\lyllo\\Workspaces\\Python\\BTG\\banking.txt'
linhas_arquivo = ler_arquivo(nome_arquivo)

# Declarar contador de linha e lista de registros
num_linha = 0
lista_de_registros = []

for linha in linhas_arquivo:

    # Encontrar uma linha de data em Outubro
    if linha.find("/Out") != -1:
        
        # Armazenar o valor da última data encontrada
        data = limpar_data(linha)

    # Encontrar uma linha de status
    if linha.find("Compra ") != -1:

        # Criar um novo registro com valores padrões
        novo_registro = {'data': 'minha_data', 
                         'item': 'meu_item', 
                         'valor': 'meu_valor', 
                         'cartao': 'meu_cartao', 
                         'parcelas': 'minhas_parcelas'}

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
            novo_registro['parcelas'] = "1/" + linha[-2]
        else:
            novo_registro['parcelas'] = "1/1"
        
    # Encontrar uma linha de valor
    if linha.find("- R$", 0, 4) != -1:

        # Definir o valor da chave 'valor' com o valor encontrado
        novo_registro['valor'] = limpar_valor(linha)

        # Armazenar o novo registro na lista de registros
        lista_de_registros.append(novo_registro)

    num_linha += 1

# print(lista_de_registros)

# Transformar a lista de dicionários em uma lista de listas, sem os nomes das chaves
lista_de_listas = [list(item.values()) for item in lista_de_registros]

# print(lista_de_listas)

# Adicionar cabeçalho a lista de listas
lista_de_listas.insert(0, ['DATA', 'ITEM', 'VALOR', 'CARTAO', 'PARCELAS', 'CATEGORIA', 'TAG'])

# Salvar as informações em um arquivo Excel
nome_arquivo = 'C:\\Users\\lyllo\\Workspaces\\Python\\BTG\\arquivo.xlsx'			
incluir_linhas_em_excel(nome_arquivo, lista_de_listas)

# TO-DO:
# [ ] 1. Transformar tipo da Coluna A de texto em data
        # Não tive sucesso com a NumberFormat de numbers de opepyxl
# [ ] 2. Transformar tipo da Coluna C de texto em moeda
# [X] 3. Preencher campos de CARTAO
# [X] 4. Preencher campos de PARCELAS
        # Consigo determinar o número de parcelas da compra, mas ainda não a qual parcela se refere aquela transação.
        # Estou tratando apenas 1 dígito de parcelas, ou seja, compras em 10x por exemplo, aparecerão com 0 parcelas.
        # Eu deveria estar dividindo o valor da compra pelo número de parcelas.
# [ ] 5. Preencher campos de CATEGORIA