from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import os
import configparser
from fake_useragent import UserAgent
import random

# Caminho do arquivo atual
current_file_path = os.path.abspath(__file__)

# Caminho da raiz do projeto
ROOT_DIR = os.path.abspath(os.path.join(current_file_path, "../../.."))

# Caminho para arquivo de configuração
PATH_TO_CONFIG_FILE = os.path.join(ROOT_DIR, 'config.ini')

# Caminho para a pasta de arquivos de entrada
PATH_TO_INPUT_FILES = os.path.join(ROOT_DIR, 'in\\')

# Lê as feature toggles do arquivo de configuração
config = configparser.ConfigParser()
config.read(PATH_TO_CONFIG_FILE)

verbose = config.get('Toggle', 'verbose')

# URL de login do BTG Pactual
url_login = 'https://www.itau.com.br/'

# Substituir 'seu_usuario' e 'sua_senha' pelos seus dados reais
agencia = '9155'
conta = '145692'

def init(PATH_TO_ITAU_CC_INPUT_FILE):

    # Nome do arquivo de entrada
    nome_arquivo_entrada = os.path.basename(PATH_TO_ITAU_CC_INPUT_FILE)

    # Cria uma instância da classe UserAgent
    ua = UserAgent()

    # Gera um user-agent aleatório
    user_agent = ua.random

    if verbose == "true":
        print(f"Configurando user-agent: {user_agent}")

    # Configurações do driver do Chrome
    chrome_options = webdriver.ChromeOptions()

    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument(f"user-agent={user_agent}")
    chrome_options.add_argument('--disable-javascript')
    chrome_options.add_argument('--incognito')
    chrome_options.add_argument('--headless') # Não carrega a GUI
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": PATH_TO_INPUT_FILES,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": False,
        "download_restrictions": 3,  # Permite sobregravar o mesmo arquivo
    })

    # Constrói o driver do Chrome
    driver = webdriver.Chrome(options=chrome_options)

    # Maximize a janela do navegador (apenas quando headless não é ativo)
    # driver.maximize_window()

    if verbose == "true":
        print("Acessando a home...")

    # Abre a página de login
    driver.get(url_login)
    
    # if verbose == "true":
    #     print("Diretório padrão de download:", chrome_options.to_capabilities()['goog:chromeOptions']['prefs']['download.default_directory'])

    # Aguarda um tempo para garantir que a página e os elementos foram carregados

    wait_time = random.uniform(3000,5000) / 1000

    if verbose == "true":
        print(f"Aguardando {wait_time:.2f}s pelo carregamento da home não logada...")

    time.sleep(wait_time)

    if verbose == "true":
        print("Preenchendo dados de agencia e conta...")

    # Preenche o usuário e senha
    campo_agencia = driver.find_element(By.ID, 'agencia')
    campo_conta = driver.find_element(By.ID, 'conta')

    campo_agencia.send_keys(agencia)
    campo_conta.send_keys(conta)

    # Submete o formulário
    botao_submit = driver.find_element(By.CSS_SELECTOR, '.login_button')
    botao_submit.click()

    # Verificar se deu erro

    wait_time = random.uniform(7500,10000) / 1000

    time.sleep(wait_time)

    if verbose == "true":
        print(f"Aguardando {wait_time:.2f}s pelo carregamento da página de login...")

    # Senha para inserir
    senha = os.getenv('Itau_pass')

    # Itera sobre cada dígito da senha

    for digito in senha:
        # Encontra o elemento da tecla correspondente
        xpath = f"//a[contains(@aria-label, '{digito}')]"
        elemento_tecla = driver.find_element(By.XPATH, xpath)

        # Clica na tecla
        elemento_tecla.click()

        # Aguarda um curto período (ajuste conforme necessário)
        wait_time = random.uniform(500,1000) / 1000
        time.sleep(wait_time)

    # Clicar no botão para acessar
    botao_acessar = driver.find_element(By.ID,'acessar')
    botao_acessar.click()

    # Aguarda carregamento da home logada
    wait_time = random.uniform(10000,15000) / 1000
    time.sleep(wait_time)
    if verbose == "true":
        print(f"Aguardando {wait_time:.2f}s pelo carregamento da home logada...")

    # Localiza o elemento pelo texto do link (neste caso, 'menu')
    card_saldo_e_extrato = driver.find_element(By.ID, 'pf-saldo-card')
    card_saldo_e_extrato.click()

    # Aguarda carregamento do card de saldo e extrato
    wait_time = random.uniform(5000,7500) / 1000
    time.sleep(wait_time)
    if verbose == "true":
        print(f"Aguardando {wait_time:.2f}s pelo carregamento do card de saldo e extrato...")

    # Localiza o botão para abrir a página de saldo e extrato
    botao_ver_extrato = driver.find_element(By.XPATH, "//button[@aria-label='ver extrato']")
    botao_ver_extrato.click()

    # Aguarda carregamento da página de saldo e extrato
    wait_time = random.uniform(7500,10000) / 1000
    time.sleep(wait_time)
    if verbose == "true":
        print(f"Aguardando {wait_time:.2f}s pelo carregamento da página de saldo e extrato...")

    # Localiza o botão para salvar o extrato
    botao_salvar = driver.find_element(By.ID, 'botao-opcoes-lancamentos')
    botao_salvar.click()
    
    # Localiza o botão para salvar o extrato em Excel
    botao_salvar_excel = driver.find_element(By.XPATH, "//a[@onclick=\"javascript:abrirExportarExcel('#botao-opcoes-lancamentos');\"]")
    botao_salvar_excel.click()

    # Aguarda um curto período (ajuste conforme necessário)
    wait_time = random.uniform(1000,2000) / 1000
    time.sleep(wait_time)

    # Localiza o checkbox para desmarcar posição consolidada
    checkbox_posicao_consolidada = driver.find_element(By.XPATH, '//*[@id="opcao-posicao-consolidada"]/label')
    checkbox_posicao_consolidada.click()

    # Aguarda um curto período (ajuste conforme necessário)
    wait_time = random.uniform(1000,2000) / 1000
    time.sleep(wait_time)

    # Localiza o checkbox para desmarcar limites
    checkbox_limites = driver.find_element(By.XPATH, '//*[@id="opcao-limites"]/label')
    checkbox_limites.click()
    
    # Aguarda um curto período (ajuste conforme necessário)
    wait_time = random.uniform(1000,2000) / 1000
    time.sleep(wait_time)

     # Localiza o botão para confirmar salvar o extrato em Excel
    salvar_excel_botao = driver.find_element(By.ID, 'salvar-excel-botao')
    salvar_excel_botao.click()

    # Aguarda o download do arquivo
    wait_time = random.uniform(2500,5000) / 1000
    time.sleep(wait_time)
    if verbose == "true":
        print(f"Aguardando {wait_time:.2f}s pelo download do arquivo...")   

    # Finalmente, feche o navegador quando terminar todas as operações
    driver.quit()

    # Renomeia o arquivo baixado para o padrão
    rename_file(PATH_TO_INPUT_FILES, nome_arquivo_entrada)

def rename_file(PATH_TO_INPUT_FILES, nome_arquivo_entrada):

    pasta = PATH_TO_INPUT_FILES  # Substitua pelo caminho real da sua pasta

    # Lista todos os arquivos na pasta
    arquivos_na_pasta = [os.path.join(pasta, arquivo) for arquivo in os.listdir(pasta) if os.path.isfile(os.path.join(pasta, arquivo))]

    # Obtém o nome do arquivo mais recente baseado no tempo de criação
    caminho_antigo = max(arquivos_na_pasta, key=os.path.getctime)

    # Novo nome do arquivo
    novo_nome = nome_arquivo_entrada

    # Caminho completo do arquivo novo
    caminho_novo = os.path.join(pasta, novo_nome)

    # Renomeia o arquivo
    os.rename(caminho_antigo, caminho_novo)