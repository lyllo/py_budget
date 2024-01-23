import mariadb
import sys
import hashlib
import load.files as files
import os
import configparser
from datetime import datetime
import io

# Caminho do arquivo atual
current_file_path = os.path.abspath(__file__)

# Caminho da raiz do projeto
ROOT_DIR = os.path.abspath(os.path.join(current_file_path, "../../.."))

# Caminho do diretório com scripts SQL
SQL_DIR = os.path.abspath(os.path.join(ROOT_DIR, "src/sql"))

# Caminho para arquivo de configuração
PATH_TO_CONFIG_FILE = os.path.join(ROOT_DIR, 'config.ini')

TIMESTAMP = int(datetime.timestamp(datetime.now()))

# Lê as feature toggles do arquivo de configuração
config = configparser.ConfigParser()
config.read(PATH_TO_CONFIG_FILE)

verbose = config.get('Toggle', 'verbose')

def conecta_bd():
    # Connect to MariaDB Platform
    try:
        conn = mariadb.connect(
            user="root",
            password="9!nT$u9!XZm3O#nE",
            host="127.0.0.1",
            port=3306,
            database="db_budget"

    )
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)

    return conn

# Gera o hash MD5 do registro
def gera_hash_md5(registro):
    data = registro['data']
    item = registro['item']
    valor = registro['valor']
    ocorrencia_dia = registro['ocorrencia_dia']

    # Used to debug hashing_issues that turned out to be about strings with spaces on the right
    # if registro['detalhe'] == 'PRESENTE MARIANA' and verbose == "true":
    #     print("Breakpoint")

    # Se data for do tipo datetime e não date, é porque estamos lendo de history.xlsx, portanto precisamos normalizar
    if isinstance(data, datetime):
        std_data = data.date()
    else:
        std_data = data
    
    std_item = item.rstrip() # remove todos os espaços em branco à direita da string
    std_valor = round(valor + 0.0005, 2) # dica pra manter 2 decimais, mesmo que zero
    std_ocorrencia_dia = ocorrencia_dia
    
    # input_string = str(data) + item + str(valor)
    # input_bytes = input_string.encode('utf-8')
    # md5_hash = hashlib.md5(input_bytes)
    # return md5_hash.hexdigest()

    if data is not None and item is not None and valor is not None:
        str_data = str(std_data)
        str_item = std_item
        str_valor = str(std_valor)
        str_ocorrencia_dia = str(std_ocorrencia_dia)

        input_string = str_data + str_item + str_valor + str_ocorrencia_dia

        input_bytes = input_string.encode('utf-8')
        md5_hash = hashlib.md5(input_bytes)
        return md5_hash.hexdigest()
    
    else:
        if verbose == "true":
            print("Erro: alguma variável é NoneType.")
        return None

def busca_simples(registro, buffer):
    # [x] Buscar apenas olhando para 3 chaves (data, item, valor)
    # [ ] Otimizar busca fazendo dump do buffer quando registro for em nova data
    # [ ] Tratar caso de transações feitas no mesmo dia para mesmo EC e valor, mas com portadores ('CARTAO') diferentes
      
    # Chaves a serem mantidas
    chaves_desejadas = ['data', 'item', 'valor']

    # Criar novo registro mantendo apenas as chaves desejadas
    novo_registro = {'data': registro['data'], 
                     'item': registro['item'],
                     'valor': registro['valor']}

    # Criar novos dicionários mantendo apenas as chaves desejadas
    nova_lista_de_dicionarios = [{chave: dicionario[chave] for chave in chaves_desejadas} for dicionario in buffer]

    if novo_registro in nova_lista_de_dicionarios:
        return nova_lista_de_dicionarios.count(novo_registro)
    else:
        return 0

def salva_registro(registro, conn, meio, fonte, file_timestamp):

    # Pega o cursor
    cursor = conn.cursor()

    # Pula a linha de cabeçalho
    if(registro['data'] != 'DATA'):

        # Verifica se transação é de cartão
        if ('cartao' not in registro):
            registro['cartao'] = ''
            registro['parcela'] = ''

        # Verifica se transação já tem detalhe (apenas teria em caso de carregamento em lote de histórico)
        if ('detalhe' not in registro):
            registro['detalhe'] = ''
        
        hash = gera_hash_md5(registro)

        try:
            cursor.execute(
                "INSERT INTO transactions (data, item, detalhe, valor, cartao, parcela, ocorrencia_dia, categoria, categoria_fonte, tag, meio, fonte, hash, timestamp, file_timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                (registro['data'], registro['item'],  registro['detalhe'], registro['valor'], registro['cartao'], registro['parcela'], registro['ocorrencia_dia'], registro['categoria'], registro['categoria_fonte'], registro['tag'], meio, fonte, hash, TIMESTAMP, file_timestamp))
            conn.commit()

            return 1
        
        except mariadb.Error as e:

            # Verifica se erro é referente a registro duplicado (hash agora é chave primária)
            if (e.errno == 1062):
                # Salvar duplicado serve apenas para depurar, pois em PROD pode jogar fora o que estiver em "offset concomitante"
                salva_duplicado(registro, conn, meio, fonte, file_timestamp)

            else:
                if verbose == "true":
                    print(f"Error em salva_registro: {e}")

            return 0
        
    return 0

# Insere registros no banco de dados
def salva_registros(lista_de_registros, meio, fonte, file_timestamp):

    # Conecta ao banco
    conn = conecta_bd()

    # Inicializa o buffer do dia para identificação de transações duplicadas que não são falsos positivos
    buffer = []

    for registro in lista_de_registros:
        
        if ('ocorrencia_dia' not in registro):
            registro['ocorrencia_dia'] = None

        ocorrencias_dia = busca_simples(registro, buffer)

        if  ocorrencias_dia == 0:
            registro['ocorrencia_dia'] = 1 # Vai começar a popular mesmo as transações unitárias com 1, o que não é nada demais (ocupa um pouco mais de espaço em disco)
            buffer.append(registro)
       
        else:
            if verbose == "true":
                print(f"O item {registro['item']} já ocorreu {ocorrencias_dia} vez(es) neste arquivo de entrada.")
            
            registro['ocorrencia_dia'] = ocorrencias_dia + 1
            
            buffer.append(registro)
    
        salva_registro(registro, conn, meio, fonte, file_timestamp)
    
    # Close Connection
    conn.close()

    # Return timestamp
    return TIMESTAMP

def carrega_historico(input_file):

    #Conecta ao banco
    conn = conecta_bd()

    # Lista de sheets do workbook, que são organizadas por meio de pagamento (IMPORTANTE: Existem outros meios que foram usados no passado e que estão ocultos)
    # sheets = ['Cartao BTG', 'Cartao XP', 'Cartao GPA', 'Cartao Flash', 'CC Itau', 'CI BTG', 'CI Sofisa', 'CI XP', 'CI Rico']

    sheet = 'Summary'

    # Obtém o timestamp de criação do arquivo
    file_timestamp = files.get_modification_time(input_file)

    # Itera pelas sheets do workbook (Lembrando que apenas as 3 primeiras têm 'CARTÃO' e 'PARCELA')
    # for sheet in sheets:

    num_registros_lidos = 0
    num_registros_salvos = 0

    if verbose == "true":
        print(f"Iniciando 'load' do {sheet} em BD...")

    # Itera nas linhas do arquivo de histórico
    for linha in files.ler_arquivo_xlsx(input_file, sheet):

        # Carrega um novo registro do arquivo Excel
        novo_registro = {'data': linha[0], 
                         'item': linha[1],
                         'detalhe': linha[2],
                         'ocorrencia_dia': linha[3],
                         'valor': linha[4],
                         'cartao': linha[5],
                         'parcela': linha [6], 
                         'categoria': linha[7],
                         'tag': linha[8],
                         'meio': linha[9],
                         'categoria_fonte': ''}
        
        # Verifica se chegou a um registro vazio antes de salvar
        if linha[0] is not None:
            num_registros_salvos += salva_registro(novo_registro, conn, novo_registro['meio'], os.path.basename(input_file), file_timestamp)

        num_registros_lidos += 1

    if verbose == "true":

        # O -1 é para remover a linha do cabeçalho
        registros_lidos = num_registros_lidos - 1
        registros_salvos = num_registros_salvos

        # Considera que a diferença entre registros lidos e registros salvos se dá pelo número de duplicados (deverá ser ZERO com a implentação da lógica que considera PORTADOR e OCORRÊNCIA)
        registros_duplicados = registros_lidos - registros_salvos
        
        print(f"""
            Registros lidos ({sheet}): {registros_lidos}
            Registros salvos ({sheet}): {registros_salvos}
            Registros duplicados ({sheet}): {registros_duplicados}
            """)
            
# [ ] Verificar se o registro duplicado já não existe na tabela de duplicado, se não em uma repetida rodada do script, todos os registros que são verdadeiros positivos, cairão na tabela de duplicados repetidas vezes
def salva_duplicado(registro, conn, meio, fonte, file_timestamp):

    # Pega o cursor
    cursor = conn.cursor()

    # Pula a linha de cabeçalho
    if(registro['data'] != 'DATA'):

        # Verifica se transação é de cartão
        if ('cartao' not in registro):
            registro['cartao'] = ''
            registro['parcela'] = ''

        # Verifica se transação já tem detalhe (apenas terá em caso de carregamento em lote de histórico)
        if ('detalhe' not in registro):
            registro['detalhe'] = ''

        try:
            cursor.execute(
                "INSERT INTO duplicates (data, item, detalhe, valor, cartao, parcela, ocorrencia_dia, categoria, categoria_fonte, tag, meio, fonte, hash, timestamp, file_timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                (registro['data'], registro['item'], registro['detalhe'], registro['valor'], registro['cartao'], registro['parcela'], registro['ocorrencia_dia'], registro['categoria'], registro['categoria_fonte'], registro['tag'], meio, fonte, gera_hash_md5(registro), TIMESTAMP, file_timestamp))
            conn.commit()

        except mariadb.Error as e:
            if verbose == "true":
                print(f"Error em salva_duplicado: {e}")

def fetch_transactions_where(nome_planilha, timestamp):

    transactions = []

    #Conecta ao banco
    conn = conecta_bd()

    # Pega o cursor
    cursor = conn.cursor()

    # Query the database
    cursor.execute(
        "SELECT * FROM transactions WHERE meio=? AND timestamp=?", 
        (f"{nome_planilha}",f"{timestamp}",))

    # Print Result-set
    for (data, item, detalhe, valor, cartao, parcela, ocorrencia_dia, categoria, categoria_fonte, tag, meio, fonte, hash, timestamp, file_timestamp) in cursor:
        transaction = {'data': data, 
                       'item': item,
                       'detalhe': detalhe,
                       'ocorrencia_dia': ocorrencia_dia, 
                       'valor': valor,
                       'cartao': cartao,
                       'parcela': parcela,
                       'categoria': categoria,
                       'tag': tag,
                       'meio': meio}
                    #    'categoria_fonte': categoria_fonte,
                    #    'meio': meio,
                    #    'arquivo_fonte': fonte,
                    #    'hash': hash,
                    #    'timestamp': timestamp,
                    #    'file_timestamp': file_timestamp}
        transactions.append(transaction)

    return transactions

def fetch_transactions():

    transactions = []

    #Conecta ao banco
    conn = conecta_bd()

    # Pega o cursor
    cursor = conn.cursor()

    # Query the database
    cursor.execute(
        "SELECT * FROM transactions")

    # Print Result-set
    for (data, item, detalhe, valor, cartao, parcela, ocorrencia_dia, categoria, categoria_fonte, tag, meio, fonte, hash, timestamp, file_timestamp) in cursor:
        transaction = {'data': data, 
                       'item': item,
                       'detalhe': detalhe,
                       'ocorrencia_dia': ocorrencia_dia, 
                       'valor': valor,
                       'cartao': cartao,
                       'parcela': parcela,
                       'categoria': categoria,
                       'tag': tag,
                       'meio': meio}
                    #    'categoria_fonte': categoria_fonte,
                    #    'meio': meio,
                    #    'arquivo_fonte': fonte,
                    #    'hash': hash,
                    #    'timestamp': timestamp,
                    #    'file_timestamp': file_timestamp}
        transactions.append(transaction)

    return transactions

def fetch_uncategorized_transactions():

    transactions = []

    #Conecta ao banco
    conn = conecta_bd()

    # Pega o cursor
    cursor = conn.cursor()

    # Query the database
    cursor.execute(
        "SELECT * FROM transactions WHERE categoria = ''")

    # Print Result-set
    for (data, item, detalhe, valor, cartao, parcela, ocorrencia_dia, categoria, categoria_fonte, tag, meio, fonte, hash, timestamp, file_timestamp) in cursor:
        transaction = {'data': data, 
                       'item': item,
                       'detalhe': detalhe,
                       'ocorrencia_dia': ocorrencia_dia, 
                       'valor': valor,
                       'cartao': cartao,
                       'parcela': parcela,
                       'categoria': categoria,
                       'tag': tag,
                       'meio': meio,
                    #    'categoria_fonte': categoria_fonte,
                    #    'meio': meio,
                    #    'arquivo_fonte': fonte,
                       'hash': hash}
                    #    'timestamp': timestamp,
                    #    'file_timestamp': file_timestamp}
        transactions.append(transaction)

    return transactions

def fetch_stats():

    stats = []

    #Conecta ao banco
    conn = conecta_bd()

    # Pega o cursor
    cursor = conn.cursor()

    # Carrega a query
    sql_filepath = os.path.abspath(os.path.join(SQL_DIR, "STATS_V2.sql"))
    with io.open(sql_filepath, 'r', encoding='utf-8') as file:
        consulta_sql = file.read()

    # Query the database
    cursor.execute(consulta_sql)

    # Print Result-set
    for (meio, last_transaction, last_update, last_file, total_transactions) in cursor:
        stat = {'method': meio, 
                'last_transaction': last_transaction,
                'last_update': last_update,
                'last_file_update': last_file,
                'total_transactions': total_transactions
               }
        stats.append(stat)

    return stats

def update_mtime(file_path, modification_time):
    file_name = os.path.basename(file_path)
    
    #Conecta ao banco
    conn = conecta_bd()

    # Pega o cursor
    cursor = conn.cursor()

    # Query the database
    cursor.execute(
        "UPDATE files SET mtime = ? WHERE nome = ?",
        (f"{modification_time}",f"{file_name}",))

    # Commita a transação
    conn.commit()
    
    # Close Connection
    conn.close()

def update_uncategorized_records(records):

    #Conecta ao banco
    conn = conecta_bd()

    # Pega o cursor
    cursor = conn.cursor()

    for record in records:

        detalhe = record['detalhe']
        categoria =record['categoria']
        tag = record['tag']
        hash = record['hash']

        # Query the database
        cursor.execute(
            "UPDATE transactions SET detalhe = ?, categoria = ?, tag = ? WHERE hash = ?",
            (f"{detalhe}",f"{categoria}",f"{tag}",f"{hash}",))
        
        # Commita a transação
        conn.commit()

    # Close Connection
    conn.close()