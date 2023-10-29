from openpyxl import Workbook

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

def ler_arquivo(nome_arquivo):
    linhas = []
    with open(nome_arquivo, 'r', -1, 'utf-8') as arquivo:
        for linha in arquivo:
            linhas.append(linha.strip())
    return linhas

def limpar_data(linha):
    if len(linha) != 6:
        return linha[-6:]
    else:
        return linha

# Exemplo de uso
# nome_arquivo = 'C:\\Users\\lyllo\\Workspaces\\Python\\BTG\\arquivo.xlsx'			
# linhas = [
#     ['DATA', 'ITEM', 'VALOR', 'CARTÃO', 'PARCELA', 'CATEGORIA', 'TAG'],
#     ['01/01/2023', 'Antonio Manoel Tiago', '-R$ 19,99', 'PHILIPPE', '1/1', 'MERCADO', '']
# ]

# incluir_linhas_em_excel(nome_arquivo, linhas)

# Exemplo de uso
nome_arquivo = 'C:\\Users\\lyllo\\Workspaces\\Python\\BTG\\banking.txt'
linhas_arquivo = ler_arquivo(nome_arquivo)

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
        novo_registro = {'data': 'minha_data', 'item': 'meu_item', 'valor': 'meu_valor'}

        # Definir o valor da chave 'data' com a última data encontrada
        novo_registro['data'] = data

        # Definir o valor da chave 'item' com o item encontrado
        novo_registro['item'] = linhas_arquivo[num_linha-1]

    # Encontrar uma linha de valor
    if linha.find("- R$", 0, 4) != -1:

        # Definir o valor da chave 'valor' com o valor encontrado
        novo_registro['valor'] =linha

        # Armazenar o novo registro na lista de registros
        lista_de_registros.append(novo_registro)

    num_linha += 1

print(lista_de_registros)