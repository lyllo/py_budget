import os
from datetime import datetime
import load.files as files
import load.db as db
import config as config

def init(input_file, lista_de_registros, MEIO, output_file, PATH_TO_FINAL_OUTPUT_FILE):
    
    if config.verbose == "true":
        nome_arquivo_entrada = os.path.basename(input_file)
        print(f"\tRegistros lidos ({nome_arquivo_entrada}): {len(lista_de_registros)}")

    # Salva dados no banco
    if(config.toggle_db == "true"):

        now_timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"\n[{now_timestamp}] Iniciando 'load' do {MEIO} em db...")
        file_timestamp = files.get_modification_time(input_file)
        db.salva_registros(lista_de_registros, MEIO, os.path.basename(input_file), file_timestamp)

    # Salva as informações em um arquivo Excel temporário
    if(config.toggle_temp_sheet == "true"):

        now_timestamp = datetime.now().strftime("%H:%M:%S")
        nome_arquivo = output_file
        print(f"\n[{now_timestamp}] Iniciando 'load' do {MEIO} em xlsx temporário...")
        files.salva_lista_excel(nome_arquivo, MEIO, lista_de_registros)

    # Salva as informações em um arquivo Excel final
    if(config.toggle_final_sheet == "true"):

        now_timestamp = datetime.now().strftime("%H:%M:%S")
        nome_arquivo = PATH_TO_FINAL_OUTPUT_FILE
        print(f"\n[{now_timestamp}] Iniciando 'load' do {MEIO} em xlsx final...")
        files.salva_lista_excel(nome_arquivo, MEIO, lista_de_registros)