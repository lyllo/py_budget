import os
import configparser
import main

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
# [ ] Alterar registros apenas manipulados no Excel, não os que já estão no banco de dados.

PRESET = 'read_datasources'
# PRESET = 'update_database' # Pode chamar se por acaso apagar registros diretamente no banco e precisar restaurar com o Excel.
# PRESET = 'dump_database' # Pode chamar se der erro de atualização do arquivo xlsx por conta dele estar aberto, após ET do ETL acontecer.

verbose = config['default']['verbose']
simple_match = config['default']['simple_match']
similar_match = config['default']['similar_match']
ai_match = config['default']['ai_match']
load_xlsx = config['default']['load_xlsx']
debug_mode = config['default']['debug_mode']

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
toggle_transform_btg_mobile = config[PRESET]['toggle_transform_btg_mobile']
toggle_transform_btg_cc_mobile = config[PRESET]['toggle_transform_btg_cc_mobile']

toggle_extract_btg = config[PRESET]['toggle_extract_btg']
toggle_extract_btg_mobile = config[PRESET]['toggle_extract_btg_mobile']
toggle_extract_flash = config[PRESET]['toggle_extract_flash']
toggle_extract_gpa = config[PRESET]['toggle_extract_gpa']
toggle_extract_itau_cc = config[PRESET]['toggle_extract_itau_cc']

toggle_db = config[PRESET]['toggle_db']
toggle_temp_sheet = config[PRESET]['toggle_temp_sheet']
toggle_final_sheet = config[PRESET]['toggle_final_sheet']

toggle_load_history = config[PRESET]['toggle_load_history']
toggle_dump_history = config[PRESET]['toggle_dump_history']
toggle_update_data_from_excel = config[PRESET]['toggle_update_data_from_excel']

if __name__ == "__main__":
    main.main()