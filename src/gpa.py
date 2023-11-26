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

    # Declara contador de linha e lista de registros
    lista_de_registros = []
    offset = False

    # Lê as linhas do arquivo para tratamento dos dados
    for linha in files.ler_arquivo_xls(input_file):

        if (offset == True) and (linha[3] != ''):

            # Cria um novo registro com valores nulos
            novo_registro = {'data': '', 
                                'item': '', 
                                'valor': '', 
                                'categoria': '',
                                'tag': '',
                                'source': ''}

            # Armazena os caracteres que representam a data da tramsação no formato dd/mm/aaaa [Coluna A]
            str_data = linha[0]
            
            # Armazena os caracteres que representam a descrição da transação (= item) [Coluna B]
            str_item = linha[1]
            
            # Armazena os caracteres que representam o valor da transação no formato xxx.xxx,xx [Coluna D]
            float_valor = linha[3]

            # Transforma a data do tipo 'string' para o tipo 'date'
            date_data = limpar_data(str_data)

            # Armazena o valor da chave 'data' com a data já no tipo 'date'
            novo_registro['data'] = date_data

            # Armazena o valor da chave 'item' com o item já no tipo 'string'
            novo_registro['item'] = str_item

            # Armazena o valor da chave 'valor' com o valor já no tipo 'float'
            novo_registro['valor'] = float_valor * -1

            # Armazenar o novo registro na lista de registros
            lista_de_registros.append(novo_registro)

        # Encontra a linha que antecede as transações (Coluna D = 'valor')
        if (linha[3] == 'valor'):
            offset = True

        # Encontra a linha que procede as transações (Coluna D = '')
        if (offset == True) and (linha[3] == ''):
            offset = False

    # Preenche as categorias das transações
    category.fill(lista_de_registros)

    # Transforma a lista de dicionários em uma lista de listas, sem os nomes das chaves
    lista_de_listas = [list(item.values()) for item in lista_de_registros]

    # Adiciona o cabeçalho à lista de listas
    lista_de_listas.insert(0, ['DATA', 'ITEM', 'VALOR', 'CATEGORIA', 'TAG', 'SOURCE'])

    # Salva as informações em um arquivo Excel
    nome_arquivo = output_file		
    files.incluir_linhas_em_excel(nome_arquivo, lista_de_listas)