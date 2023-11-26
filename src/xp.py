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

# Converter strings no formato dd/mm/aaaa para variáveis do tipo datetime no formato aaaa-mm-dd
def limpar_data(str_data):
    dia = int(str_data[0:2])
    mes = int(str_data[3:5])
    ano = int(str_data[6:10])

    data_datetime = datetime(ano, mes, dia).date()

    return data_datetime

# Converter strings no formato - R$xx,xx para variáveis do tipo float no formato xx,xx
def limpar_valor(str_valor):
    valor_float = "{:.2f}".format(-1 * float(str_valor[3:].replace(".","").replace(",",".")))
    return float(valor_float)

def limpar_parcelas(str_parcelas):
        if (str_parcelas == '-'):
            str_parcelas_limpa = '1/1'
        else:
            str_parcelas_limpa = str_parcelas.replace(' de ', '/')
        return str_parcelas_limpa

# Encontrar posições de uma string dentro de outra string, armazenando os resultados em uma lista
def encontrar_todas_ocorrencias(s, sub):
    start = 0
    positions = []  # Lista para armazenar as posições
    while True:
        start = s.find(sub, start)
        if start == -1: 
            return positions  # Retorna a lista de posições
        positions.append(start)
        start += len(sub)  # use start += 1 to find overlapping matches

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

        # Verifica se é a primeira linha, de cabeçalho
        if (num_linha != 0):

            # Cria um novo registro com valores nulos
            novo_registro = {'data': '', 
                                'item': '', 
                                'valor': '',
                                'cartao': '',
                                'parcelas': '', 
                                'categoria': '',
                                'tag': '',
                                'source': ''}

            # Busca a posição dos separadores
            posicoes = encontrar_todas_ocorrencias(linha, ';')

            # Máscara: Data;Estabelecimento;Portador;Valor;Parcela

            # Armazena os caracteres que representam a data da tramsação no formato dd/mm/aaaa
            str_data = linha[:posicoes[0]]
            
            # Armazena os caracteres que representam a descrição da transação (= item)
            str_item = linha[posicoes[0]+1:posicoes[1]]
            
            # Armazena os caracteres que representam o portador do cartão (= cartao)
            str_cartao = linha[posicoes[1]+1:posicoes[2]]

            # Armazena os caracteres que representam o valor da transação no formato R$ xxx.xxx,xx
            str_valor = linha[posicoes[2]+1:posicoes[3]]

            # Armazena os caracteres que representam o número da parcela da transação
            str_parcelas = linha[posicoes[3]+1:]

            # Transforma a data do tipo 'string' para o tipo 'date'
            date_data = limpar_data(str_data)

            # Armazena o valor da chave 'data' com a data já no tipo 'date'
            novo_registro['data'] = date_data

            # Armazena o valor da chave 'item' com o item já no tipo 'string'
            novo_registro['item'] = str_item

            # Transforma o valor do tipo 'string' para o tipo 'float'
            float_valor = limpar_valor(str_valor)  

            # Armazena o valor da chave 'valor' com o valor já no tipo 'float'
            novo_registro['valor'] = float_valor

            # Armazena o valor, já limpo, da chave 'cartao'
            novo_registro['cartao'] = str_cartao

            # Armazena o valor, já limpo, da chave 'parcelas'
            novo_registro['parcelas'] = limpar_parcelas(str_parcelas)

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