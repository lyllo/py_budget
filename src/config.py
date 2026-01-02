import main
import configparser
import os

# Caminho do arquivo de configuração
PATH_TO_CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.ini')

# Lê as feature toggles do arquivo de configuração
config = configparser.ConfigParser()
config.read(PATH_TO_CONFIG_FILE)

# Manual Override Selection
# PRESET = 'scrape_and_load'
# PRESET = 'sync_categories'
PRESET = 'dump_database'

# [ ] Automatizar a seleção de PRESET baseado em flag de linha de comando ou status do DB
# [ ] Verificar se data de último update_database é maior do que read_datasource antes de trazer novos dados  
# [ ] Alterar registros apenas manipulados no Excel, não os que já estão no banco de dados.

verbose = config['default'].get('verbose', 'true')
simple_match = config['default'].get('simple_match', 'true')
similar_match = config['default'].get('similar_match', 'true')
ai_categorize = config['default'].get('ai_match', 'true')
debug_mode = config['default'].get('debug_mode', 'false')
load_xlsx = config['default'].get('load_xlsx', 'false')

toggle_extract_btg = config[PRESET].get('toggle_extract_btg', 'false')
toggle_extract_btg_mobile = config[PRESET].get('toggle_extract_btg_mobile', 'false')
toggle_transform_btg = config[PRESET].get('toggle_transform_btg', 'false')
toggle_transform_btg_mobile = config[PRESET].get('toggle_transform_btg_mobile', 'false')

toggle_transform_xp = config[PRESET].get('toggle_transform_xp', 'false')
toggle_extract_gpa = config[PRESET].get('toggle_extract_gpa', 'false')
toggle_transform_gpa = config[PRESET].get('toggle_transform_gpa', 'false')
toggle_extract_flash = config[PRESET].get('toggle_extract_flash', 'false')
toggle_transform_flash = config[PRESET].get('toggle_transform_flash', 'false')

toggle_extract_itau_cc = config[PRESET].get('toggle_extract_itau_cc', 'false')
toggle_transform_itau_cc = config[PRESET].get('toggle_transform_itau_cc', 'false')
toggle_transform_btg_cc = config[PRESET].get('toggle_transform_btg_cc', 'false')
toggle_transform_btg_cc_mobile = config[PRESET].get('toggle_transform_btg_cc_mobile', 'false')

toggle_transform_btg_ci = config[PRESET].get('toggle_transform_btg_ci', 'false')
toggle_transform_sofisa_ci = config[PRESET].get('toggle_transform_sofisa_ci', 'false')
toggle_transform_xp_ci = config[PRESET].get('toggle_transform_xp_ci', 'false')
toggle_transform_rico_ci = config[PRESET].get('toggle_transform_rico_ci', 'false')

toggle_db = config[PRESET].get('toggle_db', 'true')
toggle_temp_sheet = config[PRESET].get('toggle_temp_sheet', 'false')
toggle_final_sheet = config[PRESET].get('toggle_final_sheet', 'true')
toggle_dump_history = config[PRESET].get('toggle_dump_history', 'false')
toggle_load_history = config[PRESET].get('toggle_load_history', 'false')
toggle_update_data_from_excel = config[PRESET].get('toggle_update_data_from_excel', 'false')

if __name__ == "__main__":
    main.main()