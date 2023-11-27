import btg, xp, gpa, flash
import itau_cc
import btg_ci 
#import sofisa_ci, xp_ci, rico_ci
import os
import configparser

# Configura os paths dos arquivos que serão utilizados
ROOT_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

PATH_TO_CONFIG_FILE = os.path.join(ROOT_DIR, 'config.ini')

PATH_TO_BTG_INPUT_FILE = os.path.join(ROOT_DIR, 'in\\btg.txt')
PATH_TO_BTG_OUTPUT_FILE = os.path.join(ROOT_DIR, 'out\\btg.xlsx')
PATH_TO_FLASH_INPUT_FILE = os.path.join(ROOT_DIR, 'in\\flash.txt')
PATH_TO_FLASH_OUTPUT_FILE = os.path.join(ROOT_DIR, 'out\\flash.xlsx')
PATH_TO_GPA_INPUT_FILE = os.path.join(ROOT_DIR, 'in\\gpa.xls')
PATH_TO_GPA_OUTPUT_FILE = os.path.join(ROOT_DIR, 'out\\gpa.xlsx')
PATH_TO_XP_INPUT_FILE = os.path.join(ROOT_DIR, 'in\\xp.csv')
PATH_TO_XP_OUTPUT_FILE = os.path.join(ROOT_DIR, 'out\\xp.xlsx')
PATH_TO_ITAU_CC_INPUT_FILE = os.path.join(ROOT_DIR, 'in\\itau_cc.xls')
PATH_TO_ITAU_CC_OUTPUT_FILE = os.path.join(ROOT_DIR, 'out\\itau_cc.xlsx')
PATH_TO_BTG_CI_INPUT_FILE = os.path.join(ROOT_DIR, 'in\\btg_ci.txt')
PATH_TO_BTG_CI_OUTPUT_FILE = os.path.join(ROOT_DIR, 'out\\btg_ci.xlsx')

# Lê as feature toggles do arquivo de configuração
config = configparser.ConfigParser()
config.read(PATH_TO_CONFIG_FILE)

verbose = config.get('Toggle', 'verbose')
toggle_btg = config.get('Toggle', 'toggle_btg')
toggle_xp = config.get('Toggle', 'toggle_xp')
toggle_gpa = config.get('Toggle', 'toggle_gpa')
toggle_flash = config.get('Toggle', 'toggle_flash')
toggle_itau_cc = config.get('Toggle', 'toggle_itau_cc')
toggle_btg_ci = config.get('Toggle', 'toggle_btg_ci')
toggle_sofisa_ci = config.get('Toggle', 'toggle_sofisa_ci')
toggle_xp_ci = config.get('Toggle', 'toggle_xp_ci')
toggle_rico_ci = config.get('Toggle', 'toggle_rico_ci')

# Verifica a existência de um arquivo
def file_exists(file_path):
    return os.path.exists(file_path)

# Cartões
if toggle_btg == "true" and file_exists(PATH_TO_BTG_INPUT_FILE):
    print("\nIniciando processo do cartão BTG...")
    btg.init(PATH_TO_BTG_INPUT_FILE, PATH_TO_BTG_OUTPUT_FILE)

if toggle_xp == "true" and file_exists(PATH_TO_XP_INPUT_FILE):
    print("\nIniciando processo do cartão XP...")
    xp.init(PATH_TO_XP_INPUT_FILE, PATH_TO_XP_OUTPUT_FILE)

if toggle_gpa == "true" and file_exists(PATH_TO_GPA_INPUT_FILE):
    print("\nIniciando processo do cartão GPA...")
    gpa.init(PATH_TO_GPA_INPUT_FILE, PATH_TO_GPA_OUTPUT_FILE)

if toggle_flash == "true" and file_exists(PATH_TO_FLASH_INPUT_FILE):
    print("\nIniciando processo do cartão Flash...")
    flash.init(PATH_TO_FLASH_INPUT_FILE, PATH_TO_FLASH_OUTPUT_FILE)

# Contas
if toggle_itau_cc == "true" and file_exists(PATH_TO_ITAU_CC_INPUT_FILE):
    print("\nIniciando processo do ITAU_CC...")
    itau_cc.init(PATH_TO_ITAU_CC_INPUT_FILE, PATH_TO_ITAU_CC_OUTPUT_FILE)

# Investimentos
if toggle_btg_ci == "true" and file_exists(PATH_TO_BTG_CI_INPUT_FILE):
    print("\nIniciando processo do BTG_CI...")
    btg_ci.init(PATH_TO_BTG_CI_INPUT_FILE, PATH_TO_BTG_CI_OUTPUT_FILE)

# sofisa_ci.init()
# xp_ci.init()
# rico_ci.init()