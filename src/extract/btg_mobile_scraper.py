from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import os
from datetime import datetime
import subprocess
import time
import load.db as db
import config as config

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

# ============================================================================
# Helper Functions for Transaction Collection
# ============================================================================

def get_transaction_containers(driver):
    """
    Find all visible transaction containers using stable element characteristics.
    Transaction containers are ViewGroups that are both clickable and long-clickable.
    This works across app versions since it doesn't rely on obfuscated resource IDs.
    """
    try:
        # Find ViewGroups that are clickable AND long-clickable
        # These are transaction items that users can tap to see details
        containers = driver.find_elements(
            AppiumBy.XPATH,
            '//android.view.ViewGroup[@clickable="true" and @long-clickable="true"]'
        )
        return containers
    except Exception as e:
        print(f"⚠ Error finding transaction containers: {e}")
        return []

def create_transaction_signature(merchant, value, t_type, date):
    """
    Create a unique signature using only core stable fields.
    Ignores irrelevant/optional text like categories or extra descriptions
    which might vary depending on scroll position or capture timing.
    """
    if not merchant or not value:
        return None
    
    # Combine core stable fields for hashing
    # merchant, value, date, and general type (CARD/PIX etc)
    content = f"{merchant}_{value}_{t_type}_{date}"
    # Remove whitespace and newlines for consistent hashing
    content = content.replace(" ", "").replace("\n", "")
    return hash(content)

def extract_transaction_fields(texts):
    """
    Extract structured fields from transaction text array.
    
    Returns dict with parsed fields or None if invalid structure.
    """
    if len(texts) < 3:
        # Not a complete transaction, skip it
        return None
    
    import re
    
    # Identify type line and value indices
    type_idx = -1
    value_idx = -1
    
    keywords = ['Compra', 'Pix', 'Transferência', 'Pagamento', 'boleto', 'TransferÃªncia']
    for i, t in enumerate(texts):
        if any(kw in t for kw in keywords):
            type_idx = i
            break
            
    for i, t in enumerate(texts):
        if 'R$' in t:
            value_idx = i
            break
            
    if type_idx == -1 or value_idx == -1:
        # Core fields not found, skip
        return None
        
    # Remaining indices are potential merchant and category
    remaining_indices = [i for i in range(len(texts)) if i not in [type_idx, value_idx]]
    
    merchant = texts[remaining_indices[0]] if remaining_indices else "Unknown"
    category = texts[remaining_indices[1]] if len(remaining_indices) > 1 else ""
    
    transaction = {
        'type_line': texts[type_idx],
        'merchant': merchant,
        'category': category,
        'value': texts[value_idx],
        'all_texts': texts
    }
    
    # Parse transaction type line for additional info
    t_line = transaction['type_line']
    
    # Extract cardholder name (e.g., "Pix enviado por Cinthia Milsoni De Castro Rosa")
    cardholder_match = re.search(r'por\s+(.+)$', t_line)
    transaction['cardholder'] = cardholder_match.group(1) if cardholder_match else None
    
    # Extract installments (e.g., "Compra no crédito em 12x")
    installments_match = re.search(r'em\s+(\d+)x', t_line)
    transaction['installments'] = int(installments_match.group(1)) if installments_match else 1
    
    # Determine transaction type
    if 'Compra no crédito' in t_line or 'Compra no débito' in t_line:
        transaction['type'] = 'CARD'
    elif 'Pix' in t_line:
        transaction['type'] = 'PIX'
    elif 'Transferência' in t_line or 'TransferÃªncia' in t_line:
        transaction['type'] = 'TRANSFER'
    elif 'boleto' in t_line or 'Pagamento' in t_line:
        transaction['type'] = 'PAYMENT'
    else:
        transaction['type'] = 'OTHER'
    
    return transaction

def is_authorized_transaction(texts):
    """
    Check if transaction is authorized (should be included).
    Returns False if ANY field contains "não autorizada".
    """
    if not texts:
        return True
    
    for t in texts:
        if 'não autorizada' in t.lower():
            return False
    return True

def get_date_headers(driver):
    """
    Find all visible date headers on screen.
    Returns dict mapping Y-position to date text.
    """
    try:
        # Find all TextViews
        all_text_elements = driver.find_elements(AppiumBy.CLASS_NAME, 'android.widget.TextView')
        
        date_headers = {}
        import re
        date_pattern = re.compile(r'\d{1,2}/[A-Z][a-z]{2}')  # Matches "20/Dez", "19/Dez", etc.
        
        for elem in all_text_elements:
            text = elem.text
            if text and date_pattern.search(text):
                try:
                    bounds = elem.get_attribute('bounds')
                    # Extract Y coordinate from bounds [x1,y1][x2,y2]
                    y_coord = int(bounds.split(',')[1].split(']')[0])
                    date_headers[y_coord] = text
                except:
                    continue
        
        return date_headers
    except Exception as e:
        print(f"⚠ Error finding date headers: {e}")
        return {}

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
        confirm_button = driver.find_element(AppiumBy.XPATH, '//*[@content-desc="Next"]')
        confirm_button.click()

        # Esperar até que a tela inicial carregue
        print("Esperar até 20s para garantir que a tela inicial carregou")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((AppiumBy.XPATH, '//*[@text="Atividades"]'))
        )

        # Get target date from database
        formatted_date = db.fetch_most_recent_transaction_date_formatted()
        
        # ====================================================================
        # New Container-Based Collection with Deduplication
        # ====================================================================
        
        print("🔍 Starting container-based transaction collection...")
        print(f"📅 Collecting until: {formatted_date}")
        
        seen_signatures = set()  # Track collected transactions by content signature
        collected_data = []
        scroll_count = 0
        max_scrolls = 100  # Safety limit
        no_new_items_count = 0
        current_date = None
        
        while scroll_count < max_scrolls:
            try:
                # Check if target date reached
                driver.find_element(AppiumBy.XPATH, f'//*[contains(@text, "{formatted_date}")]')
                print(f"✓ Target date '{formatted_date}' found after {scroll_count} scrolls")
                
                # Final collection pass
                new_count = collect_new_transactions(
                    driver, seen_signatures, collected_data, current_date
                )
                print(f"✓ Final collection: {new_count} new transactions")
                break
                
            except:
                # Collect new transactions from current screen
                new_count, current_date = collect_new_transactions(
                    driver, seen_signatures, collected_data, current_date
                )
                
                print(f"📊 Scroll {scroll_count + 1}: +{new_count} new | {len(seen_signatures)} total unique")
                
                # Check for no progress (possible end of list)
                if new_count == 0:
                    no_new_items_count += 1
                    if no_new_items_count >= 3:
                        print("⚠ No new transactions in 3 consecutive scrolls - stopping")
                        break
                else:
                    no_new_items_count = 0
                
                # Perform adaptive scroll based on visible containers
                perform_adaptive_scroll(driver)
                
                # Debug capture if enabled
                if config.debug_mode == 'true':
                    capture_screen_and_dump(driver, scroll_count, len(seen_signatures))
                
                # Add scroll marker for backward compatibility with transformer
                collected_data.append("\n=== SCROLL ===\n")
                scroll_count += 1
                sleep(0.8)  # Wait for scroll to complete
        
        print(f"\n{'='*60}")
        print(f"📈 Collection Summary:")
        print(f"  Total unique transactions: {len(seen_signatures)}")
        print(f"  Total scrolls performed: {scroll_count}")
        print(f"  Output items (including dates/markers): {len(collected_data)}")
        print(f"{'='*60}\n")
        
        # Save collected data to file
        print(f"💾 Saving {len(seen_signatures)} unique transactions to {PATH_TO_BTG_MOBILE_INPUT_FILE}")
        with open(PATH_TO_BTG_MOBILE_INPUT_FILE, "w", encoding="utf-8") as file:
            for data in collected_data:
                file.write(data + "\n")

    finally:
        # Fechar o driver ao final
        print("🔌 Closing Appium driver")
        driver.quit()

# ============================================================================
# Collection Helper Functions
# ============================================================================

def collect_new_transactions(driver, seen_signatures, collected_data, last_date):
    """
    Collect new transactions from current screen that haven't been seen before.
    Returns count of new transactions found and the most recent date.
    """
    from selenium.common.exceptions import StaleElementReferenceException
    
    # Get all transaction containers on current screen
    containers = get_transaction_containers(driver)
    
    # Get date headers to associate with transactions
    date_headers = get_date_headers(driver)
    
    # Get screen dimensions for safe bottom margin
    window_size = driver.get_window_size()
    screen_height = window_size['height']
    # Skip items where the bottom is in the last 5% of screen (avoid partial captures)
    bottom_safe_threshold = int(screen_height * 0.95)
    
    new_count = 0
    current_date = last_date
    
    for container in containers:
        try:
            # Check if container is fully visible (avoid partial captures at bottom)
            container_bounds = container.get_attribute('bounds')
            # Extract Y2 coordinate from bounds [x1,y1][x2,y2]
            container_bottom_y = int(container_bounds.split('][')[1].split(',')[1].replace(']', ''))
            
            if container_bottom_y > bottom_safe_threshold:
                # Item is likely cut off at the bottom, skip and wait for next scroll
                continue

            # Extract all TextViews from this container
            # Use retry logic for stale elements (RecyclerView may recycle during extraction)
            max_retries = 2
            texts = None
            
            for attempt in range(max_retries):
                try:
                    text_elements = container.find_elements(AppiumBy.CLASS_NAME, 'android.widget.TextView')
                    texts = [elem.text for elem in text_elements if elem.text]
                    break  # Success, exit retry loop
                except StaleElementReferenceException:
                    if attempt == max_retries - 1:
                        # Last attempt failed, skip this container
                        print(f"  ⚠ Stale element after {max_retries} retries, skipping container")
                        break
                    # Wait briefly and retry
                    sleep(0.1)
            
            if not texts or len(texts) < 3:
                # Not a complete transaction, skip
                continue
            
            # Identify core fields for parsing and signature
            fields = extract_transaction_fields(texts)
            if not fields:
                continue

            # Check if transaction is authorized (check ALL text fields)
            if not is_authorized_transaction(texts):
                print(f"  ⊘ Skipping unauthorized: {fields['merchant']}")
                continue

            # Find the date for this transaction to use in signature
            item_date = current_date
            try:
                container_y = int(container_bounds.split(',')[1].split(']')[0])
                closest_y = -1
                for date_y, date_text in date_headers.items():
                    if date_y < container_y and date_y > closest_y:
                        item_date = date_text
                        closest_y = date_y
            except:
                pass

            # Create signature using core fields ONLY (Robust against extra descriptive text)
            signature = create_transaction_signature(
                merchant=fields['merchant'],
                value=fields['value'],
                t_type=fields['type'],
                date=item_date
            )
            
            if signature in seen_signatures:
                # Already collected this transaction
                continue
            
            # If date changed, record it
            if item_date and item_date != current_date:
                collected_data.append(item_date)
                current_date = item_date
            
            # Add normalized 4-line transaction to output
            # Format: Merchant, Category, Value, Type Line
            # This ensures backward compatibility with transformers using fixed offsets.
            collected_data.append(fields['merchant'])
            collected_data.append(fields['category'] or "")
            collected_data.append(fields['value'])
            collected_data.append(fields['type_line'])
            
            # Mark as seen
            seen_signatures.add(signature)
            new_count += 1
            
        except Exception as e:
            print(f"  ⚠ Error processing container: {e}")
            continue
    
    return new_count, current_date

def perform_adaptive_scroll(driver):
    """
    Perform scroll based on visible transaction container positions.
    Scrolls by 60% of visible content to ensure overlap and prevent missing transactions.
    Uses safe margins to avoid triggering Android system gestures (like "recents").
    """
    try:
        # Get screen dimensions for safe margins
        size = driver.get_window_size()
        width = size['width']
        height = size['height']
        
        screen_center_x = int(width / 2)
        safe_start_y = int(height * 0.8)  # Stop 20% from bottom
        safe_end_y = int(height * 0.2)    # Stop 20% from top
        
        containers = get_transaction_containers(driver)
        
        if len(containers) >= 2:
            # Get Y positions of first and last visible containers
            first_bounds = containers[0].get_attribute('bounds')
            last_bounds = containers[-1].get_attribute('bounds')
            
            first_y = int(first_bounds.split(',')[1].split(']')[0])
            last_y = int(last_bounds.split(',')[1].split(']')[0])
            
            # Calculate scroll distance (60% of visible content for safe overlap)
            visible_height = last_y - first_y
            scroll_distance = int(visible_height * 0.6)
            
            # Perform swipe within safe bounds
            start_y = min(last_y, safe_start_y)
            end_y = max(start_y - scroll_distance, safe_end_y)
            
            # If distance is too small, use a default moderate scroll
            if start_y - end_y < 100:
                start_y = safe_start_y
                end_y = safe_end_y
                
            driver.swipe(screen_center_x, start_y, screen_center_x, end_y, 600)
            return
            
        # Fallback if few containers visible
        driver.swipe(screen_center_x, safe_start_y, screen_center_x, safe_end_y, 600)
        
    except Exception as e:
        print(f"  ⚠ Scroll failed: {e}")
        # Final emergency fallback for S21-like resolutions (safe coordinates)
        try:
            driver.swipe(540, 1600, 540, 800, 600)
        except:
            pass

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

def capture_screen_and_dump(driver, scroll_num=0, sig_count=0, logs_dir="logs"):
    """
    Capture screen with scroll number and signature count in filename for better debugging.
    Only called when debug_mode is enabled in config.ini.
    """
    # Ensure logs directory exists
    os.makedirs(logs_dir, exist_ok=True)
    
    # Generate unique filename based on timestamp and metrics
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_filename = f"scroll_{scroll_num:03d}_sigs_{sig_count}_{timestamp}"
    
    # Take screenshot
    screenshot_path = os.path.join(logs_dir, f"{base_filename}.png")
    driver.get_screenshot_as_file(screenshot_path)
    
    # Dump screen contents to text file (all visible elements with text)
    text_path = os.path.join(logs_dir, f"{base_filename}.txt")
    all_elements = driver.find_elements(AppiumBy.XPATH, "//*")  # Find all elements
    with open(text_path, "w", encoding="utf-8") as file:
        for element in all_elements:
            text = element.text
            if text:
                file.write(text + "\n")
    
    # Dump full UI XML (similar to uiautomator dump)
    xml_path = os.path.join(logs_dir, f"{base_filename}.xml")
    with open(xml_path, "w", encoding="utf-8") as file:
        file.write(driver.page_source)
    
    print(f"  📸 Debug capture: {base_filename}")