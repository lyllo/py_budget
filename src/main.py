import extract.btg_scraper as btg_scraper
import extract.itau_scraper as itau_scraper
import extract.flash_scraper as flash_scraper
import extract.gpa_scraper as gpa_scraper

import transform.btg as btg
import transform.xp as xp
import transform.gpa as gpa
import transform.flash as flash
import transform.itau_cc as itau_cc
import transform.btg_cc as btg_cc
import transform.btg_ci as btg_ci
import transform.sofisa_ci as sofisa_ci
import transform.xp_ci as xp_ci
import transform.rico_ci as rico_ci

import load.db as db
import load.files as files

import os
from datetime import datetime
import config as config

# Configura os paths dos arquivos que serão utilizados
ROOT_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

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
PATH_TO_BTG_CC_INPUT_FILE = os.path.join(ROOT_DIR, 'in\\btg.txt')
PATH_TO_BTG_CC_OUTPUT_FILE = os.path.join(ROOT_DIR, 'out\\btg_cc.xlsx')

PATH_TO_BTG_CI_INPUT_FILE = os.path.join(ROOT_DIR, 'in\\btg_ci.txt')
PATH_TO_BTG_CI_OUTPUT_FILE = os.path.join(ROOT_DIR, 'out\\btg_ci.xlsx')
PATH_TO_SOFISA_CI_INPUT_FILE = os.path.join(ROOT_DIR, 'in\\sofisa_ci.txt')
PATH_TO_SOFISA_CI_OUTPUT_FILE = os.path.join(ROOT_DIR, 'out\\sofisa_ci.xlsx')
PATH_TO_XP_CI_INPUT_FILE = os.path.join(ROOT_DIR, 'in\\xp_ci.xlsx')
PATH_TO_XP_CI_OUTPUT_FILE = os.path.join(ROOT_DIR, 'out\\xp_ci.xlsx')
PATH_TO_RICO_CI_INPUT_FILE = os.path.join(ROOT_DIR, 'in\\rico_ci.xlsx')
PATH_TO_RICO_CI_OUTPUT_FILE = os.path.join(ROOT_DIR, 'out\\rico_ci.xlsx')

PATH_TO_HISTORY_FILE = os.path.join(ROOT_DIR, 'data\\history.xlsx')

# Verifica a existência de um arquivo
def file_exists(file_path):
    return os.path.exists(file_path)

# Cartões

# BTG
if config.toggle_extract_btg == "true":
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"\n[{timestamp}] Iniciando 'extract' do Cartão BTG...")       
    btg_scraper.init(PATH_TO_BTG_INPUT_FILE)

if config.toggle_transform_btg == "true" and file_exists(PATH_TO_BTG_INPUT_FILE):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"\n[{timestamp}] Iniciando 'transform' do Cartão BTG...")
    btg.init(PATH_TO_BTG_INPUT_FILE, PATH_TO_BTG_OUTPUT_FILE)

# XP
if config.toggle_transform_xp == "true" and file_exists(PATH_TO_XP_INPUT_FILE):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"\n[{timestamp}] Iniciando 'transform' do Cartão XP...")
    xp.init(PATH_TO_XP_INPUT_FILE, PATH_TO_XP_OUTPUT_FILE)

# GPA

if config.toggle_extract_gpa == "true":
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"\n[{timestamp}] Iniciando 'extract' do Cartão GPA...")       
    gpa_scraper.init(PATH_TO_GPA_INPUT_FILE)

if config.toggle_transform_gpa == "true" and file_exists(PATH_TO_GPA_INPUT_FILE):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"\n[{timestamp}] Iniciando 'transform' do Cartão GPA...")
    gpa.init(PATH_TO_GPA_INPUT_FILE, PATH_TO_GPA_OUTPUT_FILE)

# Flash

if config.toggle_extract_flash == "true":
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"\n[{timestamp}] Iniciando 'extract' do Cartão Flash...")       
    flash_scraper.init(PATH_TO_FLASH_INPUT_FILE)

if config.toggle_transform_flash == "true" and file_exists(PATH_TO_FLASH_INPUT_FILE):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"\n[{timestamp}] Iniciando 'transform' do Cartão Flash...")
    flash.init(PATH_TO_FLASH_INPUT_FILE, PATH_TO_FLASH_OUTPUT_FILE)

# Contas
if config.toggle_extract_itau_cc == "true":
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"\n[{timestamp}] Iniciando 'extract' da Conta Itaú...")       
    itau_scraper.init(PATH_TO_ITAU_CC_INPUT_FILE)    

if config.toggle_transform_itau_cc == "true" and file_exists(PATH_TO_ITAU_CC_INPUT_FILE):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"\n[{timestamp}] Iniciando 'transform' da Conta Itaú...")
    itau_cc.init(PATH_TO_ITAU_CC_INPUT_FILE, PATH_TO_ITAU_CC_OUTPUT_FILE)

if config.toggle_transform_btg_cc == "true" and file_exists(PATH_TO_BTG_CC_INPUT_FILE):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"\n[{timestamp}] Iniciando 'transform' da Conta BTG...")
    btg_cc.init(PATH_TO_BTG_CC_INPUT_FILE, PATH_TO_BTG_CC_OUTPUT_FILE)

# Investimentos
if config.toggle_transform_btg_ci == "true" and file_exists(PATH_TO_BTG_CI_INPUT_FILE):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"\n[{timestamp}] Iniciando 'transform' do BTG Investimentos...")
    btg_ci.init(PATH_TO_BTG_CI_INPUT_FILE, PATH_TO_BTG_CI_OUTPUT_FILE)

if config.toggle_transform_sofisa_ci == "true" and file_exists(PATH_TO_SOFISA_CI_INPUT_FILE):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"\n[{timestamp}] Iniciando 'transform' do Sofisa Investimentos...")
    sofisa_ci.init(PATH_TO_SOFISA_CI_INPUT_FILE, PATH_TO_SOFISA_CI_OUTPUT_FILE)

if config.toggle_transform_xp_ci == "true" and file_exists(PATH_TO_XP_CI_INPUT_FILE):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"\n[{timestamp}] Iniciando 'transform' do XP Investimentos...")
    xp_ci.init(PATH_TO_XP_CI_INPUT_FILE, PATH_TO_XP_CI_OUTPUT_FILE)

if config.toggle_transform_rico_ci == "true" and file_exists(PATH_TO_RICO_CI_INPUT_FILE):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"\n[{timestamp}] Iniciando 'transform' do Rico Investimentos...")
    rico_ci.init(PATH_TO_RICO_CI_INPUT_FILE, PATH_TO_RICO_CI_OUTPUT_FILE)

# HISTORY LOAD (USED TO CREATE A FRESH NEW DB FROM THE DATA STORED IN AN EXCEL FILE)

if config.toggle_load_history == "true" and file_exists(PATH_TO_HISTORY_FILE):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"\n[{timestamp}] Iniciando 'load' do XLSX em BD...")
    db.carrega_historico(PATH_TO_HISTORY_FILE)

# DUMP HISTORY (USED TO CREATE A FRESH NEW FILE FROM THE DATA STORED IN THE DB)
    
if config.toggle_dump_history == "true":
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"\n[{timestamp}] Iniciando 'dump' do DB em XLSX...")
    files.dump_history()

# UPDATE DATA FROM EXCEL (USED TO UPDATE THE DB WITH THE DETAILS ENTERED IN AN EXCEL FILE)

if config.toggle_update_data_from_excel == "true" and file_exists(PATH_TO_HISTORY_FILE):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"\n[{timestamp}] Iniciando 'update' do XLSX em BD...")
    db.atualiza_historico(PATH_TO_HISTORY_FILE)
