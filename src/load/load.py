import os
import sys
import configparser
from datetime import datetime
import load.files as files
import load.db as db

# Caminho do arquivo atual
current_file_path = os.path.abspath(__file__)

# Caminho da raiz do projeto
ROOT_DIR = os.path.abspath(os.path.join(current_file_path, "../../.."))

sys.path.append(ROOT_DIR)

# Caminho para arquivo de configuração
PATH_TO_CONFIG_FILE = os.path.join(ROOT_DIR, 'config.ini')

# Lê as feature toggles do arquivo de configuração
config = configparser.ConfigParser()
config.read(PATH_TO_CONFIG_FILE)

toggle_db = config.get('Toggle', 'toggle_db')
toggle_temp_sheet = config.get('Toggle', 'toggle_temp_sheet')
toggle_final_sheet = config.get('Toggle', 'toggle_final_sheet')

verbose = config.get('Toggle', 'verbose')

def init(input_file, lista_de_registros, MEIO, output_file, PATH_TO_FINAL_OUTPUT_FILE):
    
    if verbose == "true":
        nome_arquivo_entrada = os.path.basename(input_file)
        print(f"\tRegistros lidos ({nome_arquivo_entrada}): {len(lista_de_registros)}")

    # Salva dados no banco
    if(toggle_db == "true"):

        now_timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"\n[{now_timestamp}] Iniciando 'load' do {MEIO} em db...")
        file_timestamp = files.get_modification_time(input_file)
        num_registros_salvos = db.salva_registros(lista_de_registros, MEIO, os.path.basename(input_file), file_timestamp)

        if num_registros_salvos > 0:

            # Salva as informações em um arquivo Excel temporário
            if(toggle_temp_sheet == "true"):

                now_timestamp = datetime.now().strftime("%H:%M:%S")
                nome_arquivo = output_file
                print(f"\n[{now_timestamp}] Iniciando 'load' do {MEIO} em xlsx temporário...")
                files.salva_excel(nome_arquivo, MEIO)

            # Salva as informações em um arquivo Excel final
            if(toggle_final_sheet == "true"):

                now_timestamp = datetime.now().strftime("%H:%M:%S")
                nome_arquivo = PATH_TO_FINAL_OUTPUT_FILE
                print(f"\n[{now_timestamp}] Iniciando 'load' do {MEIO} em xlsx final...")
                files.salva_excel(nome_arquivo, "Summary")