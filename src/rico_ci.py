import category
import files
import db
import os
import configparser

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

    # [ ] Tirar o nome da Worksheet hardcoded dessa parte do código
    # Lê as linhas do arquivo para tratamento dos dados
    for linha in files.ler_arquivo_xlsx(input_file, "Planilha1"):

        # Verifica se a linha se trata de uma transação (Coluna F não está sem valor ou com o título)

        if ((linha[5] != None) and (linha[5] != '')  and (linha[5] != 'Extrato da conta') and (linha[5] != 'Valor (R$)')):

            # Cria um novo registro com valores nulos
            novo_registro = {'data': '', 
                            'item': '', 
                            'valor': '', 
                            'categoria': '',
                            'tag': '',
                            'source': ''}

            # Armazena os caracteres que representam a data da tramsação no formato dd/mm/aaaa [Coluna B]
            date_data = linha[1]
            
            # Armazena os caracteres que representam a descrição da transação (= item) [Coluna D]
            str_item = linha[3]
            
            # Armazena os caracteres que representam o valor da transação no formato xxx.xxx,xx [Coluna F]
            float_valor = linha[5]

            # Armazena o valor da chave 'data' com a data já no tipo 'date'
            novo_registro['data'] = date_data.date()

            # Armazena o valor da chave 'item' com o item já no tipo 'string'
            novo_registro['item'] = str_item

            # Armazena o valor da chave 'valor' com o valor já no tipo 'float'
            novo_registro['valor'] = float_valor

            # Armazenar o novo registro na lista de registros
            lista_de_registros.append(novo_registro)

    # Preenche as categorias das transações
    category.fill(lista_de_registros)

    # Salva dados no banco
    if(toggle_db == "true"):
      db.salva(lista_de_registros, "CI_Rico")

    # Transforma a lista de dicionários em uma lista de listas, sem os nomes das chaves
    lista_de_listas = [list(item.values()) for item in lista_de_registros]

    # Adiciona o cabeçalho à lista de listas
    lista_de_listas.insert(0, ['DATA', 'ITEM', 'VALOR', 'CATEGORIA', 'TAG', 'SOURCE'])

    # Salva as informações em um arquivo Excel	
    files.incluir_linhas_em_excel(output_file, lista_de_listas)