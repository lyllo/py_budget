from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import os
import configparser

# Configura os paths dos arquivos que serão utilizados
ROOT_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

PATH_TO_CONFIG_FILE = os.path.join(ROOT_DIR, 'config.ini')

PATH_TO_BTG_SCRAPPED_FILE = os.path.join(ROOT_DIR, 'in\\btg_scrapped.txt')

# Lê as feature toggles do arquivo de configuração
config = configparser.ConfigParser()
config.read(PATH_TO_CONFIG_FILE)

verbose = config.get('Toggle', 'verbose')

# [ ] Ler esse driver_path das variáveis de ambiente 
# Caminho para o seu chromedriver
driver_path = '"C:\\Users\\lyllo\\AppData\\Local\\chromedriver-win64\\chromedriver.exe"'

# URL de login do BTG Pactual
url_login = 'https://app.banking.btgpactual.com/login'

# Substitua 'seu_usuario' e 'sua_senha' pelos seus dados reais
usuario = os.getenv('BTG_user')
senha = os.getenv('BTG_pass')

# Solicita o token de acesso
token_acesso = input("Digite o token de acesso: ")

# Configuração do driver do Chrome
# É preciso deixar javascript desabilitado pois o BTG usa ele pra identificar se é robô
# De tempos em tempos vale também alterar o user-agent para não ser bloqueado
# [ ] Gerar dinamicamente o user-agent para evitar ser bloqueado

os.environ['webdriver.chrome.driver'] = driver_path
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
chrome_options.add_argument('--disable-javascript')
chrome_options.add_argument('--headless')

# Constrói o driver do Chrome
driver = webdriver.Chrome(options=chrome_options)

# Abre a página de login
driver.get(url_login)

# Aguarda um tempo para garantir que a página e os elementos foram carregados
time.sleep(5)

# Preenche o usuário e senha
campo_usuario = driver.find_element(By.ID, '0cpf')
campo_senha = driver.find_element(By.ID, '1senha')

campo_usuario.send_keys(usuario)
campo_senha.send_keys(senha)

# Submete o formulário
botao_submit = driver.find_element(By.CSS_SELECTOR, 'btg-button[type="submit"]')
botao_submit.click()

# Aguarda um tempo para a possível resposta da ação de login
time.sleep(5)

# Identifica o campo de entrada do token e envia o token

# Exemplo: encontre um elemento cujo ID comece com 'parte_variavel'
parte_fixa_otp = '3id_'
campo_token = driver.find_element(By.CSS_SELECTOR, f'[id^="{parte_fixa_otp}"]')
campo_token.send_keys(token_acesso)

# Submete o formulário de token (substitua isso pelo botão real, se necessário)
campo_token.submit()

# Aguarda um tempo para a possível resposta após a entrada do token
time.sleep(10)

# [x] Acertar o scroll para baixo (no elemnto da timeline) até encontrar o texto do mês anterior

# [ ] Ajustar para gerar dinamicamente a string do mês anterior
# String desejada a ser encontrada na página
string_desejada = '/Nov'

# Identifica o elemento dentro do qual você deseja rolar
elemento_contenedor = driver.find_element(By.XPATH, '//div[@class="timeline"]')

# Loop para rolar a página e verificar se a string está presente
encontrou_string = False
while not encontrou_string:
    # Rola a página para baixo
    # driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", elemento_alvo)
    # driver.execute_script("window.scrollBy(0, arguments[0].getBoundingClientRect().top);", elemento_alvo)
    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", elemento_contenedor)
    
    # Espera um curto período para a página ser renderizada
    # driver.implicitly_wait(2)
    
    # Verifica se a string está presente na página
    encontrou_string = string_desejada in driver.page_source

# Localiza o elemento de texto na página usando XPath (substitua pelo seu seletor)
elemento_texto = driver.find_element(By.XPATH, '//div[@class="timeline"]')

# Obtém o texto do elemento
texto_para_copiar = elemento_texto.text

# [x] Acertar o encoding do arquivo para crédito aparecer com é e não 'Compra no cr�dito autorizada'

# Abre o arquivo para escrita e cola o texto
with open(PATH_TO_BTG_SCRAPPED_FILE, 'w', encoding='utf-8') as arquivo:
    arquivo.write(texto_para_copiar)

# Finalmente, feche o navegador quando terminar todas as operações
driver.quit()