from openpyxl import Workbook
from openpyxl.styles import Font

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