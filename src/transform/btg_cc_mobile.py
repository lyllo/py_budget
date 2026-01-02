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

MEIO = "Conta BTG"

def obter_numero_mes(mes):
    meses = {
        'jan': 1, 'fev': 2, 'mar': 3, 'abr': 4, 'mai': 5, 'jun': 6,
        'jul': 7, 'ago': 8, 'set': 9, 'out': 10, 'nov': 11, 'dez': 12
    }
    return meses.get(mes.lower(), None)

def limpar_data(linha):
    # Matches '20/Dez' or 'Sábado 20/Dez' or '20/Dez/2023'
    match = re.search(r'(\d{1,2})/(jan|fev|mar|abr|mai|jun|jul|ago|set|out|nov|dez)', linha, re.IGNORECASE)
    if not match:
        return datetime.now().date() # Fallback
    
    dia = int(match.group(1))
    mes_str = match.group(2)
    mes = obter_numero_mes(mes_str)
    
    # Try once more for a 4-digit year anywhere in the line
    ano_match = re.search(r'(\d{4})', linha)
    if ano_match:
        ano = int(ano_match.group(1))
    else:
        # Better logic: if current month is Jan and transaction is Dec, it's last year
        now = datetime.now()
        ano = now.year
        if now.month == 1 and mes == 12:
            ano -= 1
    
    return datetime(ano, mes, dia).date()

def limpar_valor(linha):
    multiplicador = -1
    offset_valor = 4
    if linha.find("-") == -1:
        multiplicador = 1
        offset_valor = 4
    valor_float = "{:.2f}".format(multiplicador * float(linha[offset_valor:].replace(".","").replace(",",".")))
    return float(valor_float)

def encontra_linha_de_data(linha):
    linha_lower = linha.lower()
    meses = ["/jan", "/fev", "/mar", "/abr", "/mai", "/jun", "/jul", "/ago", "/set", "/out", "/nov", "/dez"]
    return any(m in linha_lower for m in meses)

def init(input_file, output_file):
    linhas_arquivo_raw = files.ler_arquivo(input_file)
    
    BTG_CATEGORIES = [
        "Alimentação", "Transporte", "Saúde", "Supermercado", "Lazer", "Compras", "Casa", 
        "Seguro", "Contas", "Viagem", "Educação", "Pet", "Luz", "Internet", "Streaming", 
        "Água", "Gás", "Outra Categoria", "Transferência", "Investimento", "Impostos",
        "Lazer e Entretenimento", "Mercado", "Vendas", "Salário", "Serviços", "Pagamento de conta",
        "Pagamento de boleto", "Pix enviado", "Transferência recebida", "Cancelamento", 
        "Estorno", "Crédito em confiança", "Finanças", "Assinaturas e Serviços", "Cuidados Pessoais"
    ]
    
    linhas_arquivo = [l.strip() for l in linhas_arquivo_raw]
    lista_de_registros = []
    seen_in_file = set()
    
    def normalize_match(s):
        if not s: return ""
        tr = str.maketrans("áàâãéèêíìîóòôõúùûç", "aaaaeeeiiioooouuuc")
        return s.lower().translate(tr).strip()

    print(f"\tRegistros lidos (btg_mobile.txt): {len([l for l in linhas_arquivo if 'R$' in l])}")
    
    line_dates = {}
    last_d = None
    for idx, line in enumerate(linhas_arquivo):
        if encontra_linha_de_data(line):
            last_d = limpar_data(line)
        line_dates[idx] = last_d

    for i in range(len(linhas_arquivo)):
        line = linhas_arquivo[i]
        if 'R$' in line and 'Saldo' not in line and not encontra_linha_de_data(line):
            try:
                valor = limpar_valor(line)
            except:
                continue
            if valor == 0: continue
            t_date = line_dates.get(i)
            if not t_date: continue
            
            cand_1 = linhas_arquivo[i-1] if i-1 >= 0 else None
            cand_2 = linhas_arquivo[i-2] if i-2 >= 0 else None
            
            norm_cand_1 = normalize_match(cand_1)
            cand_1_is_cat = any(normalize_match(cat) in norm_cand_1 for cat in BTG_CATEGORIES) if cand_1 else False
            
            if cand_1_is_cat:
                merchant = cand_2 if cand_2 and not encontra_linha_de_data(cand_2) else cand_1
            else:
                merchant = cand_1 if cand_1 and not encontra_linha_de_data(cand_1) else "Unknown"
            
            # Identify Type Bidirectionally (to accurately skip credit)
            potential_types = []
            for j in range(i-2, i+3):
                if j < 0 or j >= len(linhas_arquivo) or j == i: continue
                l_cand = linhas_arquivo[j]
                
                # STOP if we hit a date or value line between us and the type line
                if encontra_linha_de_data(l_cand) or ('R$' in l_cand and j != i):
                    if (j < i and any(encontra_linha_de_data(linhas_arquivo[k]) for k in range(j, i))) or \
                       (j > i and any(encontra_linha_de_data(linhas_arquivo[k]) for k in range(i+1, j+1))):
                        continue
                
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
                        is_cat_check = any(normalize_match(cat) in check_l_norm for cat in BTG_CATEGORIES)
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
            
            type_line = ""
            for pt in potential_types:
                low_pt = pt.lower()
                if any(k in low_pt for k in ["pix", "pagamento", "transfer", "crédito", "compra no", "em "]):
                    type_line = pt
                    break
            
            if not type_line and potential_types:
                if i+1 < len(linhas_arquivo) and i+1 in potential_types:
                    type_line = linhas_arquivo[i+1]
                elif potential_types:
                    type_line = potential_types[-1]

            # STRICT FILTER: Ignore credit card transactions for Account transformer
            t_lower = type_line.lower()
            if "crédito" in t_lower or "compra no" in t_lower:
                continue
                
            detalhe = ""
            if "Pix" in type_line:
                # Try to extract recipient/sender: "Pix enviado por Name" or "Pix recebido de Name"
                match = re.search(r'(?:por|de|recebido de|enviado para)\s+(.+)', type_line, re.IGNORECASE)
                detalhe = f"Pix - {match.group(1).strip()}" if match else "Pix"
            elif "Pagamento" in type_line or "boleto" in type_line.lower():
                detalhe = "Pagamento"
            elif "Transfer" in type_line:
                detalhe = "Transferência"

            cartao = 'PHILIPPE Q ROSA'
            if "CINTHIA" in type_line.upper(): cartao = 'CINTHIA ROSA'

            clean_merchant = merchant.strip()
            tx_signature = (t_date, clean_merchant, valor)
            if tx_signature in seen_in_file: continue
            seen_in_file.add(tx_signature)

            lista_de_registros.append({
                'data': t_date, 'item': clean_merchant, 'detalhe': detalhe, 'ocorrencia_dia': '',
                'valor': valor, 'cartao': cartao, 'parcela': '',
                'categoria': '', 'tag': '', 'categoria_fonte': ''
            })

    category.fill(lista_de_registros)
    load.init(input_file, lista_de_registros, MEIO, output_file, PATH_TO_FINAL_OUTPUT_FILE)