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

# [x] Verificar se data de final.xlsx é maior do que history.xlsx antes de iniciar update_database
# [ ] Verificar se data de último update_database é maior do que read_datasource antes de trazer novos dados  

PRESET = 'read_datasources'
# PRESET = 'update_database'
# PRESET = 'dump_database'

verbose = config['default']['verbose']
simple_match = config['default']['simple_match']
similar_match = config['default']['similar_match']
ai_match = config['default']['ai_match']
load_xlsx = config['default']['load_xlsx']

toggle_transform_btg = config[PRESET]['toggle_transform_btg']
toggle_transform_xp = config[PRESET]['toggle_transform_xp']
toggle_transform_gpa = config[PRESET]['toggle_transform_gpa']
toggle_transform_flash = config[PRESET]['toggle_transform_flash']
toggle_transform_itau_cc = config[PRESET]['toggle_transform_itau_cc']
toggle_transform_btg_cc = config[PRESET]['toggle_transform_btg_cc']
toggle_transform_btg_ci = config[PRESET]['toggle_transform_btg_ci']
toggle_transform_sofisa_ci = config[PRESET]['toggle_transform_sofisa_ci']
toggle_transform_xp_ci = config[PRESET]['toggle_transform_xp_ci']
toggle_transform_rico_ci = config[PRESET]['toggle_transform_rico_ci']

toggle_extract_btg = config[PRESET]['toggle_extract_btg']
toggle_extract_flash = config[PRESET]['toggle_extract_flash']
toggle_extract_gpa = config[PRESET]['toggle_extract_gpa']
toggle_extract_itau_cc = config[PRESET]['toggle_extract_itau_cc']

toggle_db = config[PRESET]['toggle_db']
toggle_temp_sheet = config[PRESET]['toggle_temp_sheet']
toggle_final_sheet = config[PRESET]['toggle_final_sheet']

toggle_load_history = config[PRESET]['toggle_load_history']
toggle_dump_history = config[PRESET]['toggle_dump_history']
toggle_update_data_from_excel = config[PRESET]['toggle_update_data_from_excel']