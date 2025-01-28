from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import os
from fake_useragent import UserAgent
import random
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import datetime
import config as config

SUCCESSFUL_SCRAPING = 0
UNSUCCESSFUL_SCRAPING = 1

# URL de login do BTG Pactual
url_login = 'https://app.banking.btgpactual.com/login'

# Substituir 'seu_usuario' e 'sua_senha' pelos seus dados reais
usuario = os.getenv('BTG_user')
senha = os.getenv('BTG_pass')

def init(PATH_TO_BTG_INPUT_FILE):

    # Solicita o token de acesso (Desabilitando para não receber 401 na tentativa de obter timeline)
    # token_acesso = input("Digite o token de acesso: ")

    # Cria uma instância da classe UserAgent
    ua = UserAgent()

    # Gera um user-agent aleatório
    user_agent = ua.random

    if config.verbose == "true":
        print(f"[btg_scraper.py] Configurando user-agent: {user_agent}")

    # Configura;óes do driver do Chrome
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument(f"user-agent={user_agent}")
    chrome_options.add_argument('--disable-javascript')
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument('--incognito')
    chrome_options.add_argument('--headless') # Não carrega a GUI
    chrome_options.binary_location = 'C:\Program Files\Google\Chrome Beta\Application\chrome.exe'

    # Constrói o driver do Chrome
    driver = webdriver.Chrome(options=chrome_options)

    # Abre a página de login
    driver.get(url_login)

    # Aguarda um tempo para garantir que a página e os elementos foram carregados

    wait_time = random.uniform(5000,10000) / 1000

    if config.verbose == "true":
        print(f"[btg_scraper.py] Aguardando {wait_time:.2f}s pelo carregamento da tela de login...")

    time.sleep(wait_time)

    if config.verbose == "true":
        print("[btg_scraper.py] Preenchendo dados de login...")

    # Preenche o usuário e senha
    wait = WebDriverWait(driver, 10)
    campo_usuario = wait.until(EC.visibility_of_element_located((By.ID, '0cpf')))
    campo_senha = wait.until(EC.visibility_of_element_located((By.ID, '1senha')))

    campo_usuario.send_keys(usuario)
    campo_senha.send_keys(senha)

    # Submete o formulário
    botao_submit = driver.find_element(By.CSS_SELECTOR, 'btg-button[type="submit"]')
    botao_submit.click()

    # Verificar se deu erro

    wait_time = random.uniform(3000,5000) / 1000

    if config.verbose == "true":
        print(f"[btg_scraper.py] Aguardando {wait_time:.2f}s pelo carregamento da tela de token...")

    # Espera alguns segundos para o elemento com a classe "modal-error" aparecer
    try:
        elemento_modal_error = WebDriverWait(driver, wait_time).until(
            EC.presence_of_element_located((By.CLASS_NAME, "modal-error"))
        )
        if elemento_modal_error.is_displayed():
            print("[btg_scraper.py] O elemento com class 'modal-error' apareceu na tela. Encerrando execução do programa.")
            driver.quit()
            return UNSUCCESSFUL_SCRAPING

    except TimeoutException:

        # Comentar da 98 até a 125 para não seguir fluxo de OTP digitado
        # try:
        #     # wait_time = 10 # Espera 10s para autorizar o acesso pelo celular
        #     # if config.verbose == "true":
        #     #     print(f"[btg_scraper.py] Aguardando {wait_time:.2f}s para autorizar o acesso pelo celular...")

        #     parte_fixa_otp = '3id_'
        #     campo_token = WebDriverWait(driver, wait_time).until(
        #         EC.presence_of_element_located((By.CSS_SELECTOR, f'[id^="{parte_fixa_otp}"]'))
        #     )   
        
        #     # Submete o formulário de token
        #     if config.verbose == "true":
        #         print("[btg_scraper.py] Preenchendo dados do token...")
        #     campo_token.send_keys(token_acesso)
        #     campo_token.submit()

        # except TimeoutException:
        #     print("[btg_scraper.py] Tempo de espera esgotado. O campo do token não foi encontrado.")
        #     driver.quit()
        #     return UNSUCCESSFUL_SCRAPING
        
        # # [ ] Aqui ainda não está perfeito o fluxo, pois não está respeitando a pausa explícita de 10s para aprovar o acesso pelo celular.
        # wait_time = random.uniform(10000,15000) / 1000

        # if config.verbose == "true":
        #     print(f"[btg_scraper.py] Aguardando {wait_time:.2f}s pelo carregamento da home...")

        # time.sleep(wait_time)

        # Comentar da 128 até a 129 para seguir fluxo de OTP aprovado pelo celular
        print(f"[btg_scraper.py] Aguardando 15.00s pela aprovação do acesso pelo celular e carregamento da home...")
        time.sleep(15)        

        # [x] Acertar o scroll para baixo (no elemnto da timeline) até encontrar o texto do mês anterior
        # [x] Ajustar para gerar dinamicamente a string do mês anterior
        # String desejada a ser encontrada na página
        string_desejada = mes_anterior()

        # Identifica o elemento dentro do qual você deseja rolar

        try:
            wait_time = random.uniform(3000,5000) / 1000
            if config.verbose == "true":
                print(f"[btg_scraper.py] Aguardando {wait_time:.2f}s para encontrar a timeline...")
            time.sleep(wait_time)

            elemento_contenedor = WebDriverWait(driver, wait_time).until(
                EC.presence_of_element_located((By.XPATH, '//div[@class="timeline"]'))
            )

        except TimeoutException:
            print("[btg_scraper.py] Tempo de espera esgotado. A timeline não foi encontrada.")
            driver.quit() # [ ] Poderia tentar reiniciar automaticamente o script
            return UNSUCCESSFUL_SCRAPING

        # Controle de tempo
        inicio = time.time()
        encontrou_string = False

        timeout = random.uniform(30000,35000) / 1000
        if config.verbose == "true":
            print(f"[btg_scraper.py] Aguardando {timeout:.2f}s para popular a timeline...")

        # Loop para rolar a página e verificar se a string está presente
        while not encontrou_string:

            # Verifica se o tempo limite foi atingido
            if time.time() - inicio > timeout:
                if config.verbose == "true":
                    print("[btg_scraper.py] Tempo de espera esgotado. A timeline não foi populada.")
                return UNSUCCESSFUL_SCRAPING

            # Rola a página para baixo
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", elemento_contenedor)
            
            # Espera um curto período para a página ser renderizada
            driver.implicitly_wait(1)
            
            # Verifica se a string está presente na página
            encontrou_string = string_desejada in driver.page_source

        if config.verbose == "true":
            print(f"[btg_scraper.py] Copiando as transações até o início do mês anterior ({string_desejada})...")

        # Localiza o elemento de texto na página usando XPath
        elemento_texto = driver.find_element(By.XPATH, '//div[@class="timeline"]')

        # Obtém o texto do elemento
        texto_para_copiar = elemento_texto.text

        # A timeline foi populada
        if (texto_para_copiar != ''):
            
            if (texto_para_copiar != ''):

                if config.verbose == "true":
                    print("[btg_scraper.py] Salvando as transações em arquivo texto...")

                # Abre o arquivo para escrita e cola o texto
                with open(PATH_TO_BTG_INPUT_FILE, 'w', encoding='utf-8') as arquivo:
                    arquivo.write(texto_para_copiar)

                # Finalmente, feche o navegador quando terminar todas as operações
                driver.quit()
                return SUCCESSFUL_SCRAPING

        # A timeline não foi populada
        elif (texto_para_copiar == ''):
            if config.verbose == "true":
                print("[btg_scraper.py] Tempo de espera esgotado. A timeline não foi populada.")
                driver.quit()
                return UNSUCCESSFUL_SCRAPING

"""
  ______                /\/|                                _ _ _                     
 |  ____|              |/\/                 /\             (_) (_)                    
 | |__ _   _ _ __   ___ ___   ___  ___     /  \  _   ___  ___| |_  __ _ _ __ ___  ___ 
 |  __| | | | '_ \ / __/ _ \ / _ \/ __|   / /\ \| | | \ \/ / | | |/ _` | '__/ _ \/ __|
 | |  | |_| | | | | (_| (_) |  __/\__ \  / ____ \ |_| |>  <| | | | (_| | | |  __/\__ \
 |_|   \__,_|_| |_|\___\___/ \___||___/ /_/    \_\__,_/_/\_\_|_|_|\__,_|_|  \___||___/
                    )_)                                                               

"""

def mes_anterior():
    # Dicionário de tradução de meses
    meses_pt = {
        "jan": "Jan",
        "feb": "Fev",
        "mar": "Mar",
        "apr": "Abr",
        "may": "Mai",
        "jun": "Jun",
        "jul": "Jul",
        "aug": "Ago",
        "sep": "Set",
        "oct": "Out",
        "nov": "Nov",
        "dec": "Dez"
    }
    
    # Obter data atual
    hoje = datetime.date.today()
    
    # Obter o primeiro dia do mês anterior
    primeiro_dia_mes_anterior = hoje.replace(day=1) - datetime.timedelta(days=30)
    
    # Obter o nome do mês anterior no formato abreviado em inglês
    mes_anterior_abreviado_en = primeiro_dia_mes_anterior.strftime("/%b").lower()
    
    # Traduzir para português
    mes_anterior_abreviado_pt = meses_pt[mes_anterior_abreviado_en[1:]]  # Ignora o "/" no início
    
    return "/" + mes_anterior_abreviado_pt