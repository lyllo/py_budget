from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# from appium.webdriver.common.touch_action import TouchAction
from time import sleep
import os
import datetime
import subprocess
import time
import load.db as db

desired_caps = {
    'platformName': 'Android',
    'platformVersion': '16',
    'deviceName': 'RQCYA001J5A',
    'appPackage': 'com.btg.pactual.banking',
    "appActivity": ".banking_login.presentation.BankingLoginActivity",
    'automationName': 'UiAutomator2',
    'noReset': True # Pulo do gato para não perder o token entre execuções do script
}

senha = os.getenv('BTG_pass')

def init(PATH_TO_BTG_MOBILE_INPUT_FILE):

    #[ ] TO-DO: Inicializar automaticamente o Appium Server 

    # Inicia a sessão do Appium
    driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)

    try:
        # Esperar a tela de inicio carregar
        print("Esperar até 5s pelo carregamento da tela de login")
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((AppiumBy.XPATH, '//*[@text="Entrar"]'))
        )

        # Encontrar e clicar no botão "Entrar"
        print("Encontrar e clicar no botão 'Entrar'")
        entrar_button = driver.find_element(AppiumBy.XPATH, '//*[@text="Entrar"]')
        entrar_button.click()

        # Esperar um pouco para garantir que a tela de digitação da senha carregou
        print("Esperar até 5s para garantir que a próxima tela carregou")
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((AppiumBy.XPATH, '//*[@text="Qual a sua senha de acesso?"]'))
        )

        # Encontrar o campo para a senha e inserir o valor
        print("Encontrar o campo para a senha e inserir o valor")
        password_field = driver.find_element(AppiumBy.XPATH, '//*[@password="true"]')
        password_field.send_keys(senha)

        # Encontrar o botão de confirmação e clicar
        print("Encontrar o botão de confirmação e clicar")
        confirm_button = driver.find_element(AppiumBy.XPATH, '//*[@content-desc="Avançar"]')
        confirm_button.click()

        # Esperar até que a tela inicial carregue
        print("Esperar até 10s para garantir que a tela inicial carregou")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((AppiumBy.XPATH, '//*[@text="Atividades"]'))
        )

        # Função para realizar o scroll
        def scroll_down():
            # Ajustar os parâmetros para a resolução do Samsung Galaxy S21
            start_x = 540  # Metade da largura da tela
            start_y = 1800  # Ponto de início do scroll (próximo ao final da tela)
            end_x = 540  # Mesma posição horizontal
            end_y = 600  # Ponto de término do scroll (próximo ao topo da tela)
            duration = 500  # Duração do scroll em milissegundos

            driver.swipe(start_x, start_y, end_x, end_y, duration)

        # Lista para armazenar os dados coletados
        collected_data = []

        # [x] TO-DO: Substituir o texto do mês anterior (ou última data do BD) programaticamente.
        formatted_date = db.fetch_most_recent_transaction_date_formatted()
        print(f"Vamos rolar até {formatted_date}, data anterior à última transação não parcelada no BD.")

        # Loop para dar scroll até que o elemento desejado apareça
        while True:
            try:
                driver.find_element(AppiumBy.XPATH, f'//*[contains(@text, "{formatted_date}")]')
                # Coletar uma últime vez os elementos visíveis
                elements = driver.find_elements(AppiumBy.CLASS_NAME, 'android.widget.TextView')
                for element in elements:
                    text = element.text
                    if text:  # Verificar se o texto não está vazio
                        collected_data.append(text)
                break
            except:
                # Coletar dados dos elementos visíveis
                elements = driver.find_elements(AppiumBy.CLASS_NAME, 'android.widget.TextView')
                for element in elements:
                    text = element.text
                    if text:  # Verificar se o texto não está vazio
                        collected_data.append(text)
                # Realizar o scroll
                scroll_down()
                sleep(1)  # Aguardar um pouco para que o scroll seja concluído

        # Exibir os dados coletados
        print("Salvando os dados coletados em btg_mobile.txt")
        with open(PATH_TO_BTG_MOBILE_INPUT_FILE, "w", encoding="utf-8") as file:
            for data in collected_data:
                file.write(data + "\n")

    finally:
        # Fechar o driver ao final
        print("Fechar o driver ao final")
        driver.quit()

def start_appium():
    """Inicia o servidor Appium automaticamente."""
    try:
        # Inicia o Appium em segundo plano
        process = subprocess.Popen(["appium"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Aguarda alguns segundos para garantir que o servidor esteja rodando
        time.sleep(5)
        
        # Retorna o processo para permitir a finalização posterior
        return process
    except Exception as e:
        print(f"Erro ao iniciar o Appium: {e}")
        return None
    
def stop_appium(process):
    """Encerra o processo do Appium."""
    if process:
        process.terminate()
        print("Appium encerrado.")