import btg, xp, gpa, flash
import itau_cc
import btg_ci, sofisa_ci, xp_ci, rico_ci
import btg_scrapper
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
PATH_TO_SOFISA_CI_INPUT_FILE = os.path.join(ROOT_DIR, 'in\\sofisa_ci.txt')
PATH_TO_SOFISA_CI_OUTPUT_FILE = os.path.join(ROOT_DIR, 'out\\sofisa_ci.xlsx')
PATH_TO_XP_CI_INPUT_FILE = os.path.join(ROOT_DIR, 'in\\xp_ci.xlsx')
PATH_TO_XP_CI_OUTPUT_FILE = os.path.join(ROOT_DIR, 'out\\xp_ci.xlsx')
PATH_TO_RICO_CI_INPUT_FILE = os.path.join(ROOT_DIR, 'in\\rico_ci.xlsx')
PATH_TO_RICO_CI_OUTPUT_FILE = os.path.join(ROOT_DIR, 'out\\rico_ci.xlsx')

PATH_TO_HISTORY_FILE = os.path.join(ROOT_DIR, 'data\\history.xlsx')

# Lê as feature toggles do arquivo de configuração
config = configparser.ConfigParser()
config.read(PATH_TO_CONFIG_FILE)

verbose = config.get('Toggle', 'verbose')

toggle_transform_btg = config.get('Toggle', 'toggle_transform_btg')
toggle_transform_xp = config.get('Toggle', 'toggle_transform_xp')
toggle_transform_gpa = config.get('Toggle', 'toggle_transform_gpa')
toggle_transform_flash = config.get('Toggle', 'toggle_transform_flash')
toggle_transform_itau_cc = config.get('Toggle', 'toggle_transform_itau_cc')
toggle_transform_btg_ci = config.get('Toggle', 'toggle_transform_btg_ci')
toggle_transform_sofisa_ci = config.get('Toggle', 'toggle_transform_sofisa_ci')
toggle_transform_xp_ci = config.get('Toggle', 'toggle_transform_xp_ci')
toggle_transform_rico_ci = config.get('Toggle', 'toggle_transform_rico_ci')

toggle_extract_btg = config.get('Toggle', 'toggle_extract_btg')

toggle_load_history = config.get('Toggle', 'toggle_load_history')

# Verifica a existência de um arquivo
def file_exists(file_path):
    return os.path.exists(file_path)

# Cartões

# BTG
if toggle_extract_btg == "true":

    print("\nIniciando 'extract' do cartão BTG...")       
    btg_scrapper.init(PATH_TO_BTG_INPUT_FILE)

if toggle_transform_btg == "true" and file_exists(PATH_TO_BTG_INPUT_FILE):

    print("\nIniciando 'transform' do Cartão BTG...")
    btg.init(PATH_TO_BTG_INPUT_FILE, PATH_TO_BTG_OUTPUT_FILE)

# XP
if toggle_transform_xp == "true" and file_exists(PATH_TO_XP_INPUT_FILE):
    print("\nIniciando 'transform' do Cartão XP...")
    xp.init(PATH_TO_XP_INPUT_FILE, PATH_TO_XP_OUTPUT_FILE)

if toggle_transform_gpa == "true" and file_exists(PATH_TO_GPA_INPUT_FILE):
    print("\nIniciando 'transform' doc Cartão GPA...")
    gpa.init(PATH_TO_GPA_INPUT_FILE, PATH_TO_GPA_OUTPUT_FILE)

if toggle_transform_flash == "true" and file_exists(PATH_TO_FLASH_INPUT_FILE):
    print("\nIniciando 'transform' do Cartão Flash...")
    flash.init(PATH_TO_FLASH_INPUT_FILE, PATH_TO_FLASH_OUTPUT_FILE)

# Contas
if toggle_transform_itau_cc == "true" and file_exists(PATH_TO_ITAU_CC_INPUT_FILE):
    print("\nIniciando 'transform' da Conta Itaú...")
    itau_cc.init(PATH_TO_ITAU_CC_INPUT_FILE, PATH_TO_ITAU_CC_OUTPUT_FILE)

# Investimentos
if toggle_transform_btg_ci == "true" and file_exists(PATH_TO_BTG_CI_INPUT_FILE):
    print("\nIniciando 'transform' do BTG investimentos...")
    btg_ci.init(PATH_TO_BTG_CI_INPUT_FILE, PATH_TO_BTG_CI_OUTPUT_FILE)

if toggle_transform_sofisa_ci == "true" and file_exists(PATH_TO_SOFISA_CI_INPUT_FILE):
    print("\nIniciando 'transform' do Sofisa investimentos...")
    sofisa_ci.init(PATH_TO_SOFISA_CI_INPUT_FILE, PATH_TO_SOFISA_CI_OUTPUT_FILE)

if toggle_transform_xp_ci == "true" and file_exists(PATH_TO_XP_CI_INPUT_FILE):
    print("\nIniciando 'transform' do XP investimentos...")
    xp_ci.init(PATH_TO_XP_CI_INPUT_FILE, PATH_TO_XP_CI_OUTPUT_FILE)

if toggle_transform_rico_ci == "true" and file_exists(PATH_TO_RICO_CI_INPUT_FILE):
    print("\nIniciando 'transform' do Rico investimentos...")
    rico_ci.init(PATH_TO_RICO_CI_INPUT_FILE, PATH_TO_RICO_CI_OUTPUT_FILE)

# HISTORY LOAD

if toggle_load_history == "true" and file_exists(PATH_TO_HISTORY_FILE):
    print("\nIniciando 'load' do histórico em BD...")
    db.carrega_historico(PATH_TO_HISTORY_FILE)