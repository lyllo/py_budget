from datetime import datetime
import category
import files

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
    
# Converter strings no formato dd/mmm para variáveis do tipo datetime no formato aaaa-mm-dd
def limpar_data(linha):
    data_string = linha
    if len(data_string) != 6:
        data_string = linha[-6:]
    else:
        data_string = linha

    mes = obter_numero_mes(data_string[-3:].lower())

    # [ ] Permitir outros anos, além de 2023
    data_datetime = datetime(2023, mes, int(data_string[:2])).date()

    return data_datetime

# Converter strings no formato - R$xx,xx para variáveis do tipo float no formato xx,xx
def limpar_valor(linha):
    valor_float = "{:.2f}".format(-1 * float(linha[5:].replace(".","").replace(",",".")))
    valor_string = str(valor_float).replace(".",",")
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

            # Criar um novo registro com valores padrões
            novo_registro = {'data': '', 
                            'item': '', 
                            'valor': '', 
                            'cartao': '', 
                            'parcelas': '',
                            'categoria': '',
                            'tag': '',
                            'source': 'minha_fonte'}

            # Define o valor da chave 'data' com a última data encontrada
            novo_registro['data'] = data

            # Define o valor da chave 'item' com o item encontrado (linha anterior)
            novo_registro['item'] = linhas_arquivo[num_linha-1]

            # Define o valor da chave 'cartao' com o nome do portador
            if linha.find("CINTHIA") != -1:
                novo_registro['cartao'] = 'CINTHIA'
            else:
                novo_registro['cartao'] = 'PHILIPPE'

            # Define o valor da chave 'parcelas' com o número de parcelas da compra
            if linha.find("Compra no crédito em ") != -1:
                novo_registro['parcelas'] = "1/" + linha[21]
            else:
                novo_registro['parcelas'] = "1/1"
            
        # Encontra uma linha de valor
        if linha.find("- R$", 0, 4) != -1:

            # Definir o valor da chave 'valor' com o valor encontrado
            novo_registro['valor'] = limpar_valor(linha)

            # Verifica se valor é zerado
            if novo_registro['valor'] != 0:

                # Armazenar o novo registro na lista de registros
                lista_de_registros.append(novo_registro)

        num_linha += 1

    # Preenche as categorias das transações
    category.fill(lista_de_registros)

    # Transforma a lista de dicionários em uma lista de listas, sem os nomes das chaves
    lista_de_listas = [list(item.values()) for item in lista_de_registros]

    # Adiciona o cabeçalho à lista de listas
    lista_de_listas.insert(0, ['DATA', 'ITEM', 'VALOR', 'CARTAO', 'PARCELAS', 'CATEGORIA', 'TAG', 'SOURCE'])

    # Salva as informações em um arquivo Excel
    nome_arquivo = output_file		
    files.incluir_linhas_em_excel(nome_arquivo, lista_de_listas)