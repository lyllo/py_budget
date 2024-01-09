from datetime import datetime
import category
import files
import db
import os
import configparser
import installments

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

    # Lê as linhas do arquivo para tratamento dos dados
    for linha in linhas_arquivo:
       
        # Encontra uma linha de data em Outubro ou Novembro
        if encontra_linha_de_data(linha):
            
            # Armazenar o valor da última data encontrada
            data = limpar_data(linha)

        # Encontra uma linha de status
        if linha.find("Compra ") != -1:

            if linha.find("não autorizada") == -1:
                unnautorized = True
            else:
                unnautorized = False

            # Criar um novo registro com valores padrões
            novo_registro = {'data': '', 
                            'item': '', 
                            'valor': '', 
                            'cartao': '', 
                            'parcelas': '',
                            'categoria': '',
                            'tag': '',
                            'source': ''}

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
                novo_registro['parcelas'] = "1/1"
            
        # Encontra uma linha de valor
        if linha.find("- R$", 0, 4) != -1:

            # Definir o valor da chave 'valor' com o valor encontrado
            novo_registro['valor'] = limpar_valor(linha)/parcelas

            # Verifica se valor é zerado e status é autorizado
            if novo_registro['valor'] != 0 and unnautorized != False:

                if parcelas == 1:
                    # Armazenar o novo registro de parcela única na lista de registros
                    lista_de_registros.append(novo_registro)

                else:
                    # Armazena os registros referentes a todas as parcelas na lista de registros
                    for parcela in range (1, parcelas+1):
                        # Armazena a data da primeira parcela
                        if (parcela == 1):
                            data_base = novo_registro['data']
                        data_parcela = installments.calcula_data_parcela(data_base, parcela)
                        nova_parcela = {'data': novo_registro['data'], 
                                        'item': novo_registro['item'], 
                                        'valor': novo_registro['valor'],  
                                        'cartao': novo_registro['cartao'],  
                                        'parcelas': '',
                                        'categoria': '',
                                        'tag': '',
                                        'categoria_fonte': ''}
                        nova_parcela['data'] = data_parcela
                        nova_parcela['parcelas'] = str(parcela) + "/" + str(parcelas)
                        lista_de_registros.append(nova_parcela)

        num_linha += 1

    # Preenche as categorias das transações
    category.fill(lista_de_registros)

    # Salva dados no banco
    if(toggle_db == "true"):
        print("\nIniciando 'load' do cartão BTG em db...")
        db.salva_registros(lista_de_registros, "Cartao BTG", os.path.basename(input_file))

    # Transforma a lista de dicionários em uma lista de listas, sem os nomes das chaves
    lista_de_listas = [list(item.values()) for item in lista_de_registros]

    # Adiciona o cabeçalho à lista de listas
    lista_de_listas.insert(0, ['DATA', 'ITEM', 'VALOR', 'CARTAO', 'PARCELAS', 'CATEGORIA', 'TAG', 'SOURCE'])

    # Salva as informações em um arquivo Excel
    nome_arquivo = output_file
    print("\nIniciando 'load' do cartão BTG em xlsx...")		
    files.incluir_linhas_em_excel(nome_arquivo, lista_de_listas)