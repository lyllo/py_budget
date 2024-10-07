import category
import load.files as files
import load.load as load
import os
import configparser

# Caminho do arquivo atual
current_file_path = os.path.abspath(__file__)

# Caminho da raiz do projeto
ROOT_DIR = os.path.abspath(os.path.join(current_file_path, "../../.."))

# Caminho para arquivo de configuração
PATH_TO_CONFIG_FILE = os.path.join(ROOT_DIR, 'config.ini')
PATH_TO_FINAL_OUTPUT_FILE = os.path.join(ROOT_DIR, 'out\\final.xlsx')

MEIO = "XP Investimentos"



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

        if ((linha[5] != None) and (linha[5] != '') and (linha[5] != 'Valor (R$)')):

          # Criar um novo registro com valores padrões
          novo_registro = {'data': '', 
                          'item': '',
                          'detalhe': '',
                          'ocorrencia_dia': '', 
                          'valor': '',  
                          'categoria': '',
                          'tag': '',
                          'categoria_fonte': ''}

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

    # Carrega os dados em db e/ou arquivo
    load.init(input_file, lista_de_registros, MEIO, output_file, PATH_TO_FINAL_OUTPUT_FILE)