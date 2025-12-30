import os
import sys
import configparser
from datetime import datetime
import re

# Caminho do arquivo atual
current_file_path = os.path.abspath(__file__)

# Caminho da raiz do projeto
ROOT_DIR = os.path.abspath(os.path.join(current_file_path, "../../.."))

sys.path.append(ROOT_DIR)

# from imports import *
import category
import load.files as files
import load.db as db
import installments
import load.load as load

# Caminho para arquivo de configuração
PATH_TO_CONFIG_FILE = os.path.join(ROOT_DIR, 'config.ini')

# Lê as feature toggles do arquivo de configuração
config = configparser.ConfigParser()
config.read(PATH_TO_CONFIG_FILE)
verbose = config['default']['verbose']

PATH_TO_FINAL_OUTPUT_FILE = os.path.join(ROOT_DIR, 'out\\final.xlsx')

MEIO = "Cartão BTG"

"""
  ______                /\/|                                _ _ _                     
 |  ____|              |/\/                 /\             (_) (_)                    
 | |__ _   _ _ __   ___ ___   ___  ___     /  \  _   ___  ___| |_  __ _ _ __ ___  ___ 
 |  __| | | | '_ \ / __/ _ \ / _ \/ __|   / /\ \| | | \ \/ / | | |/ _` | '__/ _ \/ __|
 | |  | |_| | | | | (_| (_) |  __/\__ \  / ____ \ |_| |>  <| | | | (_| | | |  __/\__ \
 |_|   \__,_|_| |_|\___\___/ \___||___/ /_/    \_\__,_/_/\_\_|_|_|\__,_|_|  \___||___/
                    )_)                                                               

"""

# Substituir mes
def obter_numero_mes(mes):
    meses = {
        'jan': 1,
        'fev': 2,
        'mar': 3,
        'abr': 4,
        'mai': 5,
        'jun': 6,
        'jul': 7,
        'ago': 8,
        'set': 9,
        'out': 10,
        'nov': 11,
        'dez': 12
    }
    return meses.get(mes.lower(), None)

# Obter o número de parcelas de uma transação
def obter_numero_parcelas(linha):
    # Encontra o número de 1 ou 2 dígitos seguido por 'x'
    match = re.search(r'(\d{1,2})x', linha)
    if match:
        return int(match.group(1))
    return None
   
# Converter strings no formato dd/mmm para variáveis do tipo datetime no formato aaaa-mm-dd
def limpar_data(linha):
    # Matches '20/Dez' or 'Sábado 20/Dez' or '20/Dez/2023'
    match = re.search(r'(\d{1,2})/(jan|fev|mar|abr|mai|jun|jul|ago|set|out|nov|dez)', linha, re.IGNORECASE)
    if not match:
        return datetime.now().date() # Fallback
    
    dia = int(match.group(1))
    mes_str = match.group(2)
    mes = obter_numero_mes(mes_str)
    
    ano_match = re.search(r'/\d{1,2}/(\d{4})', linha)
    if ano_match:
        ano = int(ano_match.group(1))
    else:
        # Default to current year for mobile scraper dates
        ano = datetime.now().year
    
    return datetime(ano, mes, dia).date()

# Converter strings no formato - R$xx,xx para variáveis do tipo float no formato xx,xx
def limpar_valor(linha):
    multiplicador = -1
    offset_valor = 4
    if linha.find("-") == -1:
        multiplicador = 1
        offset_valor = 4 # É igual a 3 quando faz copy/paste manual
    valor_float = "{:.2f}".format(multiplicador * float(linha[offset_valor:].replace(".","").replace(",",".")))
    return float(valor_float)

def encontra_linha_de_data(linha):
    linha_lower = linha.lower()
    if linha_lower.find("/jan") != -1 or linha_lower.find("/fev") != -1 or linha_lower.find("/mar") != -1 or linha_lower.find("/abr") != -1 or linha_lower.find("/mai") != -1 or linha_lower.find("/jun") != -1 or linha_lower.find("/jul") != -1 or linha_lower.find("/ago") != -1 or linha_lower.find("/set") != -1 or linha_lower.find("/out") != -1 or linha_lower.find("/nov") != -1 or linha_lower.find("/dez") != -1:
        return True
    else:
        return False

"""

  _____       __     _             _          _____           _       _   
 |_   _|     /_/    (_)           | |        / ____|         (_)     | |  
   | |  _ __  _  ___ _  ___     __| | ___   | (___   ___ _ __ _ _ __ | |_ 
   | | | '_ \| |/ __| |/ _ \   / _` |/ _ \   \___ \ / __| '__| | '_ \| __|
  _| |_| | | | | (__| | (_) | | (_| | (_) |  ____) | (__| |  | | |_) | |_ 
 |_____|_| |_|_|\___|_|\___/   \__,_|\___/  |_____/ \___|_|  |_| .__/ \__|
                                                               | |        
                                                               |_|        

"""

def init(input_file, output_file):
    """
    Transform BTG Mobile transactions from normalized 4-line scraper format.
    Format: Merchant, Category (ignored), Value, Type Line
    """

    # Load input file
    linhas_arquivo_raw = files.ler_arquivo(input_file)
    
    # Whitelist of known BTG Categories to help distinguish from Merchants
    BTG_CATEGORIES = [
        "Alimentação", "Transporte", "Saúde", "Supermercado", "Lazer", "Compras", "Casa", 
        "Seguro", "Contas", "Viagem", "Educação", "Pet", "Luz", "Internet", "Streaming", 
        "Água", "Gás", "Outra Categoria", "Transferência", "Investimento", "Impostos",
        "Lazer e Entretenimento", "Mercado", "Vendas", "Salário", "Serviços", "Pagamento de conta",
        "Pagamento de boleto", "Pix enviado", "Transferência recebida", "Cancelamento", 
        "Estorno", "Crédito em confiança", "Finanças", "Assinaturas e Serviços"
    ]
    
    # Pre-process: strip lines and remove empty ones but KEEP indices stable
    linhas_arquivo = [l.strip() for l in linhas_arquivo_raw]
    
    # Initialize
    lista_de_registros = []
    
    def normalize_match(s):
        if not s: return ""
        tr = str.maketrans("áàâãéèêíìîóòôõúùûç", "aaaaeeeiiioooouuuc")
        return s.lower().translate(tr).strip()

    # Aggressive Deduplication: (date, merchant, value, type_substr)
    seen_in_file = set()
    
    print(f"\tRegistros lidos (btg_mobile.txt): {len([l for l in linhas_arquivo if 'R$' in l])}")
    
    # 1. First Pass: Identify Date Headers
    line_dates = {}
    last_d = None
    for idx, line in enumerate(linhas_arquivo):
        if encontra_linha_de_data(line):
            last_d = limpar_data(line)
        line_dates[idx] = last_d

    # 2. Second Pass: Find all Value lines (R$) and pull data around them
    for i in range(len(linhas_arquivo)):
        line = linhas_arquivo[i]
        
        # Check if it's a value line (must contain R$ and not be a date/category itself)
        if 'R$' in line and not encontra_linha_de_data(line):
            try:
                valor = limpar_valor(line)
            except:
                continue
            
            if valor == 0:
                continue
                
            # Current date for this line
            t_date = line_dates.get(i)
            if not t_date:
                continue
                
            # Identify Merchant and Category
            # Usual: i-2: Merchant, i-1: Category, i: Value, i+1: Type
            merchant = "Unknown"
            category_found = ""
            
            cand_1 = linhas_arquivo[i-1] if i-1 >= 0 else None
            cand_2 = linhas_arquivo[i-2] if i-2 >= 0 else None
            
            norm_cand_1 = normalize_match(cand_1)
            cand_1_is_cat = any(normalize_match(cat) in norm_cand_1 for cat in BTG_CATEGORIES) if cand_1 else False
            
            if cand_1_is_cat:
                category_found = cand_1
                merchant = cand_2 if cand_2 and not encontra_linha_de_data(cand_2) else cand_1
            else:
                # If cand_1 is not a category, it might be the merchant itself (category skipped)
                merchant = cand_1 if cand_1 and not encontra_linha_de_data(cand_1) else "Unknown"
            
            # Identify Type Bidirectionally (check window around value)
            potential_types = []
            # Narrowed window to prevent crossing boundaries
            for j in range(i-2, i+3):
                if j < 0 or j >= len(linhas_arquivo) or j == i: continue
                l_cand = linhas_arquivo[j]
                
                # STOP if we hit a date or value line between us and the type line
                # But allow checking j if it's not a date/value itself
                if encontra_linha_de_data(l_cand) or ('R$' in l_cand and j != i):
                    # Check if this boundary is between us and j
                    if (j < i and any(encontra_linha_de_data(linhas_arquivo[k]) for k in range(j, i))) or \
                       (j > i and any(encontra_linha_de_data(linhas_arquivo[k]) for k in range(i+1, j+1))):
                        continue
                
                # Skip lines that are definitely NOT type lines
                if 'R$' in l_cand or encontra_linha_de_data(l_cand): continue
                
                # AFFINITY CHECK: Does this potential labeling line 'j' belong to US or the NEXT merchant?
                if j+1 < len(linhas_arquivo) and j+1 != i:
                    found_competitor = False
                    look_idx = j+1
                    while look_idx < len(linhas_arquivo) and look_idx != i:
                        check_l = linhas_arquivo[look_idx]
                        if '=== SCROLL ===' in check_l or encontra_linha_de_data(check_l):
                            break
                        
                        check_l_norm = normalize_match(check_l)
                        is_cat_check = any(normalize_match(cat) == check_l_norm for cat in BTG_CATEGORIES)
                        is_type_check = any(k in check_l.lower() for k in ["pix", "crédito", "pagamento", "transfer", "em "])
                        if not is_cat_check and not is_type_check and 'R$' not in check_l:
                            if check_l_norm != normalize_match(merchant):
                                if abs(look_idx-j) < abs(j-i):
                                    found_competitor = True
                                break
                        look_idx += 1
                    
                    if found_competitor:
                        continue

                if any(normalize_match(cat) == normalize_match(l_cand) for cat in BTG_CATEGORIES): continue
                potential_types.append(l_cand)
            
            # Pick the best type line (prioritize explicit installments, then general credit)
            type_line = ""
            # Pass 1: Look for explicit installments "em \d+x"
            for pt in potential_types:
                if re.search(r'em \d+x', pt, re.IGNORECASE):
                    type_line = pt
                    break
            
            # Pass 2: Look for general credit labels if no installments found
            if not type_line:
                for pt in potential_types:
                    low_pt = pt.lower()
                    if "crédito" in low_pt or "em " in low_pt or "autorizada" in low_pt:
                        type_line = pt
                        break
            
            # Pass 3: Secondary keywords
            if not type_line and potential_types:
                for pt in potential_types:
                    low_pt = pt.lower()
                    if any(k in low_pt for k in ["pix", "pagamento", "transfer", "adicional"]):
                        type_line = pt
                        break
            
            # Fallback
            if not type_line:
                if i+1 < len(linhas_arquivo) and i+1 in potential_types:
                    type_line = linhas_arquivo[i+1]
                elif potential_types:
                    type_line = potential_types[-1]

            # STRICT FILTER: Only process credit card transactions for this transformer
            t_lower = type_line.lower()
            if "crédito" not in t_lower and "compra no" not in t_lower:
                continue

            # Extract cardholder and installments
            cartao = 'PHILIPPE Q ROSA'
            if 'CINTHIA' in type_line.upper() or 'Cinthia' in type_line:
                cartao = 'CINTHIA ROSA'
            
            parcelas = 1
            if 'crédito' in type_line.lower() and ' em ' in type_line.lower():
                parcelas = obter_numero_parcelas(type_line) or 1

            # Skip unauthorized
            if 'não autorizada' in type_line.lower():
                continue

            # Deduplication Signature (Robust)
            # Use basic merchant name and value to avoid scroll noise
            # We also strip the merchant name to be sure
            clean_merchant = merchant.strip()
            tx_signature = (t_date, clean_merchant, valor)
            
            if tx_signature in seen_in_file:
                if verbose == "debug":
                    print(f"\tSkipping scroll duplicate: {clean_merchant} | {valor} on {t_date}")
                continue
            
            seen_in_file.add(tx_signature)

            # Create records
            if parcelas > 1:
                valor_parcela = valor / parcelas
                for p in range(1, parcelas + 1):
                    data_p = installments.calcula_data_parcela(t_date, p)
                    lista_de_registros.append({
                        'data': data_p, 'item': clean_merchant, 'detalhe': '', 'ocorrencia_dia': '',
                        'valor': valor_parcela, 'cartao': cartao, 'parcela': f"{p}/{parcelas}",
                        'categoria': '', 'tag': '', 'categoria_fonte': ''
                    })
            else:
                lista_de_registros.append({
                    'data': t_date, 'item': clean_merchant, 'detalhe': '', 'ocorrencia_dia': '',
                    'valor': valor, 'cartao': cartao, 'parcela': '1/1',
                    'categoria': '', 'tag': '', 'categoria_fonte': ''
                })

    # Fill categories using AI/learning
    category.fill(lista_de_registros)
    
    # Load to database and Excel
    load.init(input_file, lista_de_registros, MEIO, output_file, PATH_TO_FINAL_OUTPUT_FILE)
