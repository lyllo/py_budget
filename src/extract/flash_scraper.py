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
url_login = 'https://user.flashapp.com.br/login'

# Substituir 'seu_usuario' e 'sua_senha' pelos seus dados reais
cpf = os.getenv('Flash_cpf')
senha = os.getenv('Flash_senha')

def init(PATH_TO_FLASH_INPUT_FILE):

    # Nome do arquivo de entrada
    nome_arquivo_entrada = os.path.basename(PATH_TO_FLASH_INPUT_FILE)

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

    # Aguarda um tempo para garantir que a página e os elementos foram carregados

    wait_time = random.uniform(2500,5000) / 1000

    if verbose == "true":
        print(f"Aguardando {wait_time:.2f}s pelo carregamento da home não logada...")

    time.sleep(wait_time)

    if verbose == "true":
        print("Preenchendo dados de login...")

    # Preenche o usuário e senha
    campo_cpf = driver.find_element(By.NAME, 'cpf')
    campo_senha = driver.find_element(By.NAME, 'password')

    campo_cpf.send_keys(cpf)
    campo_senha.send_keys(senha)

    # Submete o formulário
    botao_submit = driver.find_element(By.CLASS_NAME, 'ant-btn-primary')
    botao_submit.click()

    # Verificar se deu erro

    wait_time = random.uniform(2500,5000) / 1000

    time.sleep(wait_time)

    if verbose == "true":
        print(f"Aguardando {wait_time:.2f}s pelo carregamento da home...")

    # Pede otp para seguir com login
    otp = input("Digite o token de acesso: ")

    campo_otp = driver.find_element(By.CLASS_NAME, 'sc-cjibBx')

    campo_otp.send_keys(otp)

    # [ ] Dá pra capturar a string de Código Inválido para tratar o cenário 'não feliz'

    # Aguarda carregamento da home logada
    wait_time = random.uniform(5000,10000) / 1000
    time.sleep(wait_time)

    if verbose == "true":
        print(f"Aguardando {wait_time:.2f}s pelo carregamento da home logada...")

    # Abre o extrato
        
    link_extrato = driver.find_element(By.LINK_TEXT, "Extrato")
    link_extrato.click()

    # Aguarda carregamento do card de saldo e extrato
    wait_time = random.uniform(2500,5000) / 1000
    time.sleep(wait_time)
    if verbose == "true":
        print(f"Aguardando {wait_time:.2f}s pelo carregamento do extrato...")

        # [ ] Ajustar para gerar dinamicamente a string do mês anterior
        # String desejada a ser encontrada na página
        string_desejada = '/12/2023'
        encontrou_string = False

        if verbose == "true":
            print("Rolando as transações até encontrar o mês anterior...")

        # Loop para rolar a página e verificar se a string está presente
        while not encontrou_string:
            # Rola a página para baixo
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            # Verifica se a string está presente na página
            encontrou_string = string_desejada in driver.page_source

        # Localiza o elemento de texto na página usando XPath (substitua pelo seu seletor)
        elemento_texto = driver.find_element(By.CLASS_NAME, 'sc-bWOGAC')

        # Obtém o texto do elemento
        texto_para_copiar = elemento_texto.text

        # [x] Acertar o encoding do arquivo para crédito aparecer com é e não 'Compra no cr�dito autorizada'

        if verbose == "true":
            print("Salvando as transações em arquivo texto...")

        # Abre o arquivo para escrita e cola o texto
        with open(PATH_TO_FLASH_INPUT_FILE, 'w', encoding='utf-8') as arquivo:
            arquivo.write(texto_para_copiar)
        
    # Finalmente, feche o navegador quando terminar todas as operações
    driver.quit()

PATH_TO_FLASH_INPUT_FILE = os.path.join(ROOT_DIR, 'in\\flash.txt')
init(PATH_TO_FLASH_INPUT_FILE)