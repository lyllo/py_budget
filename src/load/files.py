from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl import load_workbook
from openpyxl.styles import Alignment
from openpyxl.styles import PatternFill
from datetime import datetime
from datetime import date
import xlrd
import load.db as db
import os, platform
import configparser

# Caminho do arquivo atual
current_file_path = os.path.abspath(__file__)

# Caminho da raiz do projeto
ROOT_DIR = os.path.abspath(os.path.join(current_file_path, "../../.."))
PATH_TO_FINAL_OUTPUT_FILE = os.path.join(ROOT_DIR, 'out\\final.xlsx')

# Caminho para arquivo de configuração
PATH_TO_CONFIG_FILE = os.path.join(ROOT_DIR, 'config.ini')

# Lê as feature toggles do arquivo de configuração
config = configparser.ConfigParser()
config.read(PATH_TO_CONFIG_FILE)
verbose = config['default']['verbose']

# Inclui linhas em arquivo Excel
def incluir_linhas_em_excel(nome_arquivo, nome_planilha, linhas):

    new_file = True

    try:
        # Tenta carregar o arquivo existente
        wb = load_workbook(nome_arquivo)
        new_file = False

    except FileNotFoundError:
        # Se o arquivo não existe, cria um novo
        wb = Workbook()

        # Se o arquivo não existe, vamos precisar de um cabeçalho
        linhas.insert(0, ['DATA', 'ITEM', 'DETALHE', 'OCORRÊNCIA', 'VALOR', 'CARTÃO', 'PARCELA', 'CATEGORIA', 'TAG', 'MEIO'])

    try:
        ws = wb[nome_planilha]

    except KeyError:
        # Cria a sheet 'Summary'
        ws = wb.create_sheet(nome_planilha)

    # Inicializa o contador de linhas da planilha
    if new_file == True:
        num_linha_excel = 1
    else:
        num_linha_excel = ws.max_row + 1

    # Inclui as linhas no arquivo do Excel
    for linha in linhas:
        ws.append(linha)
        
        # Pinta a fonte das linhas que contêm transações no futuro de cinza
        if isinstance(linha[0], date):
            data_linha = linha[0]
            data_hoje = datetime.now().date()
            if data_linha > data_hoje:
                for cell in ws[num_linha_excel]:
                    cell.font = Font(color="808080")

        # Formata como moeda em BRL a coluna E (5) do VALOR
        for cell in ws[num_linha_excel]:
            if cell.column == 5:
                cell.number_format = 'R$ #,##0.00'

        # Pintar de vermelho a fonte das células das categorias preenchidas por AI
        if 'ai_gpt' in linha:
            for cell in ws[num_linha_excel]:
                # A coluna F (6) é da CATEGORIA
                if cell.column == 6:
                    # print("Vou pintar a célula da linha " + str(num_linha_excel) + " e coluna " + str(cell.column))
                    cell.font = Font(color='FF0000')

        num_linha_excel += 1

    formata_planilha(ws)

    # Salva os stats
    # save_stats(wb)

    # Salva o arquivo do Excel
    wb.save(nome_arquivo)

# Substituir linhas em arquivo Excel (chamado pelo método dump)
def substituir_linhas_em_excel(nome_arquivo, nome_planilha, linhas):

    new_file = True

    # O try foi pra carregar o arquivo, não tratava incialmente ter o arquivo, mas sem a sheet 'Summary'
    try:
        # Tenta carregar o arquivo existente
        wb = load_workbook(nome_arquivo)

        # Instancia a sheet 'Summary'
        ws = wb[nome_planilha]

        # Remove a sheet 'Summary'
        wb.remove(ws)

        new_file = False

    # Não existe o arquivo
    except FileNotFoundError:
        # Se o arquivo não existe, cria um novo
        wb = Workbook()

    # Existe o arquivo mas não a sheet
    except KeyError:
        # Cria a sheet 'Summary'
        ws = wb.create_sheet(nome_planilha)

    ws = wb.create_sheet(nome_planilha)

    # Criando o cabeçalho
    linhas.insert(0, ['DATA', 'ITEM', 'DETALHE', 'OCORRÊNCIA', 'VALOR', 'CARTÃO', 'PARCELA', 'CATEGORIA', 'TAG', 'MEIO'])

    # Inicializa o contador de linhas da planilha
    num_linha_excel = 1

    # Inclui as linhas no arquivo do Excel
    for linha in linhas:
        ws.append(linha)
        
        # Pintar a fonte das linhas que contêm transações no futuro de cinza
        if isinstance(linha[0], date):
            data_linha = linha[0]
            data_hoje = datetime.now().date()
            if data_linha > data_hoje:
                for cell in ws[num_linha_excel]:
                    cell.font = Font(color="808080")

        # Formata como moeda em BRL a coluna E (5) do VALOR
        for cell in ws[num_linha_excel]:
            if cell.column == 5:
                cell.number_format = 'R$ #,##0.00'

        # Pintar de vermelho a fonte das células das categorias preenchidas por AI
        if 'ai_gpt' in linha:
            for cell in ws[num_linha_excel]:
                # A coluna F (6) é da CATEGORIA
                if cell.column == 6:
                    # print("Vou pintar a célula da linha " + str(num_linha_excel) + " e coluna " + str(cell.column))
                    cell.font = Font(color='FF0000')

        num_linha_excel += 1

    formata_planilha(ws)

    if verbose == "true":
        # Exclui a linha de cabeçalho
        print(f"\tRegistros salvos: {ws.max_row-1}")

    # Salva os stats
    # save_stats(wb)

    # Salva o arquivo do Excel
    wb.save(nome_arquivo)

# Formata a planilha
def formata_planilha(sheet):
    
    # Configura o tamanho das colunas
    colunas_menores = ['A', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
    largura_menor = 20

    for coluna in colunas_menores:
        sheet.column_dimensions[coluna].width = largura_menor

    colunas_maiores = ['B', 'C']
    largura_maior = 40

    for coluna in colunas_maiores:
        sheet.column_dimensions[coluna].width = largura_maior

    # Habilita a quebra de texto nas colunas maiores
    for coluna in colunas_maiores:
        for cell in sheet[coluna]:
            cell.alignment = Alignment(wrap_text=True)

    # Defina a altura desejada para todas as linhas
    altura_desejada = 15

    for linha in sheet.iter_rows(min_row=1, max_row=sheet.max_row):
        for cell in linha:
            sheet.row_dimensions[cell.row].height = altura_desejada
    
    # Centraliza as células das colunas menores
    for coluna in colunas_menores:
        for cell in sheet[coluna]:
            cell.alignment = cell.alignment.copy(horizontal='center')

    # Centraliza as células da primeira linha
    numero_da_linha = 1
    alinhamento = Alignment(horizontal='center', vertical='center')

    # Defina o estilo de fonte como negrito
    fonte_negrito = Font(bold=True)

    # Percorra todas as células na linha e defina o alinhamento centralizado
    for coluna in range(1, sheet.max_column + 1):
        sheet.cell(row=numero_da_linha, column=coluna).alignment = alinhamento
        sheet.cell(row=numero_da_linha, column=coluna).font = fonte_negrito

    # Definir o padrão de preenchimento com fundo branco
    padrao_preenchimento = PatternFill(start_color='FFFFFF', end_color='FFFFFF', fill_type='solid')

    # Iterar sobre todas as células da planilha e aplicar o preenchimento
    for linha in sheet.iter_rows():
        for celula in linha:
            celula.fill = padrao_preenchimento

    # [X] Pintar o fundo das células da primeira linha entre as colunas A e J de cinza
    fill = PatternFill(start_color="808080", end_color="808080", fill_type="solid")
    font = Font(color="FFFFFF", bold=True)

    # Loop pelas primeiras 10 colunas da primeira linha
    for col in range(1, 11):
        # Seleciona a célula na primeira linha e na coluna atual
        cell = sheet.cell(row=1, column=col)
        # Define o preenchimento da célula
        cell.fill = fill
        cell.font = font

    # Ative o filtro na primeira linha
    sheet.auto_filter.ref = sheet.dimensions

    # Congela a primeira linha
    sheet.freeze_panes = sheet['A2']

# Carregar arquivo de texto
def ler_arquivo(nome_arquivo):
    linhas = []
    with open(nome_arquivo, 'r', -1, 'utf-8') as arquivo:
        for linha in arquivo:
            linhas.append(linha.strip())
    return linhas

# Carregar arquivo xlsx
def ler_arquivo_xlsx(nome_arquivo, nome_planilha):
    # Carregar o arquivo Excel
    workbook = load_workbook(nome_arquivo)

    # Selecionar a planilha ativa
    sheet = workbook.get_sheet_by_name(nome_planilha)

    # Iterar sobre as linhas da planilha
    return (row for row in sheet.iter_rows(values_only=True))

# Carregar arquivo xls
def ler_arquivo_xls(nome_arquivo):
    # Carregar o arquivo Excel
    workbook = xlrd.open_workbook(nome_arquivo)

    # Selecionar a planilha ativa
    sheet = workbook.sheet_by_index(0)

    # Iterar sobre as linhas da planilha
    for row in range(sheet.nrows):
        yield sheet.row_values(row)

# Salvar dados recém carregados em excel
def salva_excel(nome_arquivo, nome_planilha):

    transactions = db.fetch_recent_transactions(nome_planilha)

    if verbose == "true":
        print(f"\tRegistros lidos: {len(transactions)}")

    if (len(transactions) > 0):

        # Função de chave para a ordenação
        def chave_de_ordenacao(dic):
            return dic['data']

        # Ordenar a lista de dicionários pela chave 'data'
        lista_ordenada = sorted(transactions, key=chave_de_ordenacao)

        # Transforma a lista de dicionários em uma lista de listas, sem os nomes das chaves
        lista_de_listas = [list(item.values()) for item in lista_ordenada]

        nome_planilha = "Summary"

        # Salva os dados em arquivo excel
        incluir_linhas_em_excel(nome_arquivo, nome_planilha, lista_de_listas)

def get_modification_time(file_path):
    if platform.system() == 'Windows':
        modification_time = os.path.getmtime(file_path)
        db.update_mtime(file_path, modification_time)
        return modification_time
    else:
        print("Este exemplo funciona apenas no Windows, a obtenção da data de criação pode variar em outros sistemas operacionais.")


def dump_history():

    transactions = db.fetch_transactions()

    print(f"\tRegistros lidos: {len(transactions)}")

    if (len(transactions) > 0):

        # Função de chave para a ordenação
        def chave_de_ordenacao(dic):
            return dic['data']

        # Ordenar a lista de dicionários pela chave 'data'
        lista_ordenada = sorted(transactions, key=chave_de_ordenacao)

        # Transforma a lista de dicionários em uma lista de listas, sem os nomes das chaves
        lista_de_listas = [list(item.values()) for item in lista_ordenada]

        nome_planilha = "Summary"

        # Salva os dados em arquivo excel
        substituir_linhas_em_excel(PATH_TO_FINAL_OUTPUT_FILE, nome_planilha, lista_de_listas)

        if verbose == "true":
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"\n[{timestamp}] Fim do 'dump' do DB em XLSX.")

def save_stats(wb):

    stats = db.fetch_stats()

    nome_planilha = 'Stats'

    # Verificar se a planilha já existe para apagar e criá-la se não existir
    if nome_planilha in wb.sheetnames:
        sheet_to_remove = wb[nome_planilha]
        wb.remove_sheet(sheet_to_remove)

    sheet = wb.create_sheet(title=nome_planilha)

    # Transforma a lista de dicionários em uma lista de listas, sem os nomes das chaves
    linhas_stats = [list(item.values()) for item in stats]

    # Insere o cabeçalho
    linhas_stats.insert(0, ['MEIO', 'ÚLTIMA TRANSAÇÃO', 'ÚLTIMA ATUALIZAÇÃO', 'ÚLTIMO ARQUIVO', 'TOTAL TRANSAÇÕES'])

    for linha in linhas_stats:
        sheet.append(linha)