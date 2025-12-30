import mariadb
import sys
import hashlib
import os
import configparser
from datetime import datetime
import io
import shutil
import locale
from datetime import timedelta
import load.files as files

# Caminho do arquivo atual
current_file_path = os.path.abspath(__file__)

# Caminho da raiz do projeto
ROOT_DIR = os.path.abspath(os.path.join(current_file_path, "../../.."))

# Caminho do diretório com scripts SQL
SQL_DIR = os.path.abspath(os.path.join(ROOT_DIR, "src/sql"))

# Caminho para arquivo de configuração
PATH_TO_CONFIG_FILE = os.path.join(ROOT_DIR, 'config.ini')

# Caminho para arquivo de saída
PATH_TO_OUTPUT_FILE = os.path.abspath(os.path.join(ROOT_DIR, "out/final.xlsx"))

# Caminho para arquivo de backup do histórico
PATH_TO_HISTORY_BACKUP_FILE = os.path.abspath(os.path.join(ROOT_DIR, "data/_history.xlsx"))

TIMESTAMP = int(datetime.timestamp(datetime.now()))

# Lê as feature toggles do arquivo de configuração
config = configparser.ConfigParser()
config.read(PATH_TO_CONFIG_FILE)

verbose = config['default']['verbose']

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
    # if registro['detalhe'] == 'DEBUG' and verbose == "true":
    #     print("Breakpoint")

    # Se data for do tipo datetime e não date, é porque estamos lendo de history.xlsx, portanto precisamos normalizar
    if isinstance(data, datetime):
        std_data = data.date()
    else:
        std_data = data
    
    std_item = item.rstrip() # remove todos os espaços em branco à direita da string
    
    try:
        std_valor = round(valor + 0.0005, 2) # dica pra manter 2 decimais, mesmo que zero
    except TypeError as e:
        if valor.startswith('='):
            std_valor = round(eval(valor[1:]) + 0.0005, 2)
    
    try:
        std_ocorrencia_dia = int(float(ocorrencia_dia))
    except:
        std_ocorrencia_dia = ocorrencia_dia

    if std_data is not None and std_item is not None and std_valor is not None:
        str_data = str(std_data)
        str_item = std_item
        str_valor = str(std_valor)
        str_ocorrencia_dia = str(std_ocorrencia_dia)

        input_string = str_data + str_item + str_valor + str_ocorrencia_dia
        
        # if verbose == "debug":
        #    print(f"[DEBUG HASH] Input: '{input_string}'")

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

        if ignora_registro(hash) != True:

            # COLLISION AWARENESS: If saving the FIRST part of an installment (1/N where N > 1),
            # purge any existing "full" (1/1) transaction for the same merchant and date.
            # This handles cases where history had the full amount but the scraper found the split.
            if registro['parcela'] and registro['parcela'].startswith('1/') and registro['parcela'] != '1/1':
                try:
                    if verbose == "true":
                        print(f"[DB] Installment detected (1/N). Purging any existing '1/1' for {registro['item']} on {registro['data']}")
                    cursor.execute(
                        "DELETE FROM transactions WHERE data = ? AND item = ? AND parcela = '1/1' AND meio = ?",
                        (registro['data'], registro['item'], meio)
                    )
                except Exception as e:
                    if verbose == "error":
                        print(f"Error purging 1/1 collision: {e}")

            try:
                cursor.execute(
                    "INSERT INTO transactions (data, item, detalhe, valor, cartao, parcela, ocorrencia_dia, categoria, categoria_fonte, tag, meio, fonte, hash, timestamp, file_timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                    (registro['data'], registro['item'],  registro['detalhe'], registro['valor'], registro['cartao'], registro['parcela'], registro['ocorrencia_dia'], registro['categoria'], registro['categoria_fonte'], registro['tag'], meio, fonte, hash, TIMESTAMP, file_timestamp))
                conn.commit()

                return 1
            
            except mariadb.Error as e:

                # Verifica se erro é referente a registro duplicado (hash agora é chave primária)
                if (e.errno == 1062):
                    # Se o registro que estamos tentando salvar tem categoria e o do banco não, atualiza
                    if registro.get('categoria') and registro.get('categoria') != '':
                        try:
                            # Busca o registro atual no banco pelo hash
                            cursor.execute("SELECT categoria FROM transactions WHERE hash = ?", (hash,))
                            resultado = cursor.fetchone()
                            if resultado and (not resultado[0] or resultado[0] == ''):
                                if verbose == "true":
                                    print(f"[DB] Atualizando categoria para registro existente: {registro['item']}")
                                cursor.execute(
                                    "UPDATE transactions SET categoria = ?, categoria_fonte = ? WHERE hash = ?",
                                    (registro['categoria'], registro['categoria_fonte'], hash)
                                )
                                conn.commit()
                        except Exception as ex:
                            if verbose == "error":
                                print(f"Erro ao tentar atualizar registro duplicado: {ex}")

                    salva_duplicado(registro, conn, meio, fonte, file_timestamp)
                    if verbose == "debug":
                        print(f"Registro duplicado ignorado (ou atualizado): {registro['item']}")

                else:
                    if verbose == "error":
                        print(f"Error em salva_registro: {e}")

                return 0
        
    return 0

# Verifica se é para ignorar transação
def ignora_registro(hash):
    ignora = False
    conn = conecta_bd()
    cursor = conn.cursor()
    cursor.execute(
    """
        SELECT COUNT(1) FROM ignored
        WHERE hash = ?
    """, 
    (f"{hash}",))
    # Obtendo o resultado
    resultado = cursor.fetchone()
    count = resultado[0] if resultado else 0
    if count != 0:
        ignora = True
        if verbose == "true":
            print(f"\tIgnorando registro com hash: {hash}")
    conn.close()
    return ignora

# Insere registros no banco de dados
def salva_registros(lista_de_registros, meio, fonte, file_timestamp):

    # Conecta ao banco
    conn = conecta_bd()

    # Inicializa o buffer do dia para identificação de transações duplicadas que não são falsos positivos
    buffer = []

    # Inicaliza contador de registros salvos
    num_registros_salvos = 0

    for registro in lista_de_registros:
        
        if ('ocorrencia_dia' not in registro):
            registro['ocorrencia_dia'] = None

        ocorrencias_dia = busca_simples(registro, buffer)

        if  ocorrencias_dia == 0:
            registro['ocorrencia_dia'] = 1 # Vai começar a popular mesmo as transações unitárias com 1, o que não é nada demais (ocupa um pouco mais de espaço em disco)
            buffer.append(registro)
       
        else:
            if verbose == "debug":
                print(f"O item {registro['item']} já ocorreu {ocorrencias_dia} vez(es) neste arquivo de entrada.")
            
            registro['ocorrencia_dia'] = ocorrencias_dia + 1
            
            buffer.append(registro)
    
        num_registros_salvos += salva_registro(registro, conn, meio, fonte, file_timestamp)
    
    if verbose == "true":
        print(f"\tRegistros lidos: {len(lista_de_registros)}\n\tRegisros salvos: {num_registros_salvos}")
    
    # Close Connection
    conn.close()

    # Return timestamp
    return num_registros_salvos

def carrega_historico(input_file):

    #Conecta ao banco
    conn = conecta_bd()

    sheet = 'Summary'

    # Obtém o timestamp de criação do arquivo
    file_timestamp = files.get_modification_time(input_file)

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

        # O -2 é para remover a linha do cabeçalho e a de end-of-file
        registros_lidos = num_registros_lidos
        registros_salvos = num_registros_salvos

        # Considera que a diferença entre registros lidos e registros salvos se dá pelo número de duplicados (deverá ser ZERO com a implentação da lógica que considera PORTADOR e OCORRÊNCIA)
        registros_duplicados = registros_lidos - registros_salvos
        
        print(f"""
            Registros lidos ({sheet}): {registros_lidos}
            Registros salvos ({sheet}): {registros_salvos}
            Registros duplicados ({sheet}): {registros_duplicados}
            """)

def atualiza_historico(input_file):

    PATH_TO_HISTORY_FILE = input_file

    # Verifica se arquivo de histórico é menos recente do que o arquivo de saída
    history_file_creation_time = os.path.getmtime(PATH_TO_HISTORY_FILE)
    output_file_creation_time = os.path.getmtime(PATH_TO_OUTPUT_FILE)

    # Comparar as datas
    if history_file_creation_time < output_file_creation_time:
        
        # Apaga _history.xlsx
        if os.path.exists(PATH_TO_HISTORY_BACKUP_FILE):  # Verificar se o arquivo existe
            os.remove(PATH_TO_HISTORY_BACKUP_FILE)
        
        # Renomeia history.xlsx para _history.xlsx
        if os.path.exists(PATH_TO_HISTORY_FILE):  # Verificar se o arquivo existe
            os.rename(PATH_TO_HISTORY_FILE, PATH_TO_HISTORY_BACKUP_FILE)
        
        # Copia out/final.xlsx para a data/history.xlsx
        try:
            shutil.copy(PATH_TO_OUTPUT_FILE, PATH_TO_HISTORY_FILE)
        except FileNotFoundError:
            print(f"O arquivo {PATH_TO_OUTPUT_FILE} não foi encontrado.")
        except Exception as e:
            print(f"Ocorreu um erro: {e}")

    elif history_file_creation_time >= output_file_creation_time:
        print("[db.py] Arquivo do histórico já está atualizado. Não vamos mexer no BD.")
        return
    
    sheet = 'Summary'

    num_registros_lidos = 0
    num_registros_alterados = 0
    num_registros_inalterados = 0
    num_registros_nao_encontrados = 0
    num_registros_corrigidos = 0
    num_registros_deletados = 0

    # Abre uma única conexão para todo o loop de atualização
    conn_shared = conecta_bd()

    # Itera nas linhas do arquivo de histórico
    for linha in files.ler_arquivo_xlsx(input_file, sheet):

        # Carrega um registro do arquivo Excel
        registro_excel = {'data': linha[0], 
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
        
        # Verifica se chegou a um registro válido
        if linha[0] is not None and linha[0] != 'DATA':
            
            # Procura o registro no banco
            current_hash = gera_hash_md5(registro_excel)
            registro_bd = fetch_transaction_by_hash(current_hash, conn_shared)

            if registro_bd != None:
                # Verifica se é para apagar o registro (contém "DELETE - " no campo 'DETALHE')
                if registro_excel['detalhe'] != None and registro_excel['detalhe'].find("DELETE - ") != -1:
                    num_registros_deletados += deleta_registro(registro_bd['hash'])

                # Verifica se houve alteração nos demais campos que não compõem a hash, ou seja, DETALHE, CARTÃO, PARCELA, CATEGORIA e TAG.
                elif verifica_alteracao(registro_bd, registro_excel, num_registros_lidos, conn_shared):
                    # Caso haja alteração atualiza o registro no banco, contabilizando para fins estatísticos
                    num_registros_alterados += 1

                # Caso contrário, apenas contabiliza para fins estatísticos
                else:
                    num_registros_inalterados += 1
            else:
                num_registros_nao_encontrados +=1
                if verbose == "true":
                    print(f"Registro não encontrado no BD: {registro_excel['data'].date()} | {registro_excel['item']} | {registro_excel['ocorrencia_dia']} | {registro_excel['valor']} | {current_hash}")

                # Tenta encontrar o registro pela tupla (data, item, ocorrencia_dia, valor) para corrigir o hash
                num_registros_corrigidos += fix_hash(registro_excel, conn_shared)

        num_registros_lidos += 1

    if verbose == "true":

        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"\n[{timestamp}] Fim do 'update' do XLSX em BD...")

        # O -1 é para excluir a linha de cabeçalho
        print(f"""
        Registros lidos ({sheet}): {num_registros_lidos-1}
        Registros alterados: {num_registros_alterados}
        Registros deletados: {num_registros_deletados}
        Registros inalterados: {num_registros_inalterados}
        Registros não encontrados: {num_registros_nao_encontrados}
            Registros corrigidos: {num_registros_corrigidos}
            Registros novos: {num_registros_nao_encontrados - num_registros_corrigidos}
        """)

def deleta_registro(hash):

    registro_deletado = 0

    #Conecta ao banco
    conn = conecta_bd()

    # Pega o cursor
    cursor = conn.cursor()

    try:
    
        # Copia o registro para a tabela de transações ignoradas para caso ele venha novamente dos golden sources
        cursor.execute(
            """
                INSERT INTO ignored
                SELECT * FROM transactions
                WHERE hash = ?
            """, 
            (f"{hash}",))
        
    except mariadb.Error as e:
        if verbose == "error":
            print(f"Erro ao inserir em ignored: {e}")

    try:
    
        # Deleta o registro da tabela de transações
        cursor.execute(
            """
                DELETE FROM transactions
                WHERE hash = ?
            """, 
            (f"{hash}",))
        
        if verbose == "true":
            print(f"Deletando de transactions registro com hash = '{hash}'")

        registro_deletado = cursor.rowcount

    except mariadb.Error as e:
        if verbose == "error":
            print(f"Erro ao deletar de transactions: {e}")
    
    # Commita a transação
    conn.commit()
    
    # Close Connection
    conn.close()

    return registro_deletado

def verifica_alteracao(registro_bd, registro_excel, num_registros_lidos, conn=None):
    houve_alteracao = False
    
    # Verifica se houve mudança na categoria separadamente para garantir o aprendizado
    if registro_excel['categoria'] != None and registro_excel['categoria'] != registro_bd['categoria']:
        try:
            import category as cat
            cat.aprende_categoria(registro_excel['item'], registro_excel['categoria'])
        except Exception as e:
            pass

    for chave in ['detalhe', 'cartao', 'parcela', 'categoria', 'tag']:
        valor_bd = registro_bd.get(chave)
        valor_excel = registro_excel.get(chave)
        
        if valor_excel != None and valor_excel != valor_bd:
            if verbose == "true":
                current_hash = registro_bd['hash']
                print(f'Divergência no valor da chave "{chave}" do registro {num_registros_lidos} de hash "{current_hash}":\nBD: {valor_bd}\nEXCEL: {valor_excel}\n')
            
            houve_alteracao = True
            # Se mudou a categoria, marcamos como Manual para o DB
            source = 'Manual' if registro_excel['categoria'] != registro_bd['categoria'] else registro_bd.get('categoria_fonte', 'history')
            update_record(registro_excel, source)
            # Retornamos no primeiro campo alterado pois update_record já atualiza todos os campos
            return True

    return houve_alteracao

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
            if verbose == "error":
                print(f"Error em salva_duplicado: {e}")

def fetch_recent_transactions(nome_planilha):

    transactions = []

    #Conecta ao banco
    conn = conecta_bd()

    # Pega o cursor
    cursor = conn.cursor()

    # Query the database
    cursor.execute(
        "SELECT * FROM transactions WHERE meio=? AND timestamp=(SELECT MAX(timestamp) FROM transactions)", 
        (f"{nome_planilha}",))

    # if nome_planilha == 'Summary':

    #     # Query the database
    #     cursor.execute(
    #         "SELECT * FROM transactions WHERE timestamp=(SELECT MAX(timestamp) FROM transactions)", 
    #         (f"{nome_planilha}",))
        
    # else:

    #     # Query the database
    #     cursor.execute(
    #         "SELECT * FROM transactions WHERE meio=? AND timestamp=(SELECT MAX(timestamp) FROM transactions)", 
    #         (f"{nome_planilha}",))

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

def fetch_limits():

    limits = []

    #Conecta ao banco
    conn = conecta_bd()

    # Pega o cursor
    cursor = conn.cursor()

    # Carrega a query
    sql_filepath = os.path.abspath(os.path.join(SQL_DIR, "LIMITS.sql"))
    with io.open(sql_filepath, 'r', encoding='utf-8') as file:
        consulta_sql = file.read()

    # Query the database
    cursor.execute(consulta_sql)

    # Print Result-set
    for (categoria, plan, actual, gap) in cursor:
        stat = {'categoria': categoria, 
                'plan': plan,
                'actual': actual,
                'gap': gap
               }
        limits.append(stat)

    return limits

def fetch_history():

    history = []

    #Conecta ao banco
    conn = conecta_bd()

    # Pega o cursor
    cursor = conn.cursor()

    # Carrega a query
    sql_filepath = os.path.abspath(os.path.join(SQL_DIR, "HISTORY.sql"))
    with io.open(sql_filepath, 'r', encoding='utf-8') as file:
        consulta_sql = file.read()

    # Query the database
    cursor.execute(consulta_sql)

    # Print Result-set
    for (categoria, periodo, total) in cursor:
        stat = {'categoria': categoria, 
                'periodo': periodo,
                'total': total * -1 # Para que o gráfico do histórico faça sentido
               }
        history.append(stat)

    return history

def fetch_current_months_transactions(category):

    transactions = []

    #Conecta ao banco
    conn = conecta_bd()

    # Pega o cursor
    cursor = conn.cursor()

    # Carrega a query
    consulta_sql = f"""
                        SELECT
                            *
                        FROM
                            transactions
                        WHERE
                            categoria = '{category}'
                            AND YEAR(DATA) = YEAR(CURDATE()) AND MONTH(data) = MONTH(CURDATE())
                        ORDER BY
                            valor
                        ASC
                    """

    # Query the database
    cursor.execute(consulta_sql)

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

def fetch_transaction_by_hash(hash, conn=None):
    
    #Conecta ao banco se não houver conexão
    should_close = False
    if conn is None:
        conn = conecta_bd()
        should_close = True

    # Pega o cursor
    cursor = conn.cursor()

    # Carrega a query
    consulta_sql = f"""
                        SELECT
                            *
                        FROM
                            transactions
                        WHERE
                            hash = '{hash}'
                    """

    # Query the database
    cursor.execute(consulta_sql)

    transaction = None

    # Print Result-set
    for (data, item, detalhe, valor, cartao, parcela, ocorrencia_dia, categoria, categoria_fonte, tag, meio, fonte, hash, timestamp, file_timestamp) in cursor:
        
        transaction = {'data': data, 
                       'item': item,
                       'detalhe': detalhe,
                       'valor': valor,
                       'cartao': cartao,
                       'parcela': parcela,
                       'ocorrencia_dia': ocorrencia_dia, 
                       'categoria': categoria,
                       'categoria_fonte': categoria_fonte,
                       'tag': tag,
                       'meio': meio,
                       'arquivo_fonte': fonte,
                       'hash': hash,
                       'timestamp': timestamp,
                       'file_timestamp': file_timestamp}

    if transaction != None:
        return transaction
    else:
        # [ ] Verificar motivo de divergência de hashes
        # if verbose == "true":
        #    print ('Divergência de hash!')
        return None

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

def update_record(registro_excel, category, conn=None):

    #Conecta ao banco se não houver conexão
    should_close = False
    if conn is None:
        conn = conecta_bd()
        should_close = True

    # Pega o cursor
    cursor = conn.cursor()

    detalhe = registro_excel['detalhe']
    if detalhe == None:
        detalhe = ''

    cartao = registro_excel['cartao']
    if cartao == None:
        cartao = ''
    
    parcela = registro_excel['parcela']
    if parcela == None:
        parcela = ''

    categoria = registro_excel['categoria']
    if categoria == None:
        categoria = ''

    tag = registro_excel['tag']
    if tag == None:
        tag = ''

    hash = gera_hash_md5(registro_excel)

    if category == "Manual":
        # Aprendizado automático: salva no binário a correção manual do usuário
        try:
            import category as cat
            cat.aprende_categoria(registro_excel['item'], registro_excel['categoria'])
        except Exception as e:
            if verbose == "error":
                print(f"Erro ao disparar aprendizado automático: {e}")

        # Query the database
        cursor.execute(
            "UPDATE transactions SET detalhe = ?, cartao = ?, parcela = ?, categoria = ?, tag = ?, categoria_fonte = 'Manual' WHERE hash = ?",
            (f"{detalhe}",f"{cartao}",f"{parcela}",f"{categoria}",f"{tag}",f"{hash}",))
        
    else:

        # Query the database
        cursor.execute(
            "UPDATE transactions SET detalhe = ?, cartao = ?, parcela = ?, categoria = ?, tag = ? WHERE hash = ?",
            (f"{detalhe}",f"{cartao}",f"{parcela}",f"{categoria}",f"{tag}",f"{hash}",))
    
    # Close Connection
    if should_close:
        conn.close()

def fix_hash(registro_excel, conn=None):
    fixed_hash = 0
    # fetch_transaction_by_tuple ainda abre sua própria conexão por enquanto (menos crítico)
    registro_bd = fetch_transaction_by_tuple(registro_excel)
    registro_excel_hash = gera_hash_md5(registro_excel)
    
    if registro_bd != None:    
        update_hash(registro_bd['hash'], registro_excel_hash)
        fixed_hash = 1
    else:
        # Se não encontrou nem por tupla, é novo ou item mudou de nome
        if conn is None:
            conn = conecta_bd()
            should_close = True
        else:
            should_close = False
            
        salva_registro(registro_excel, conn, registro_excel['meio'], 'Manual', TIMESTAMP)
        
        if should_close:
            conn.close()
            
    return fixed_hash

def update_hash(old_hash, new_hash):

    #Conecta ao banco
    conn = conecta_bd()

    # Pega o cursor
    cursor = conn.cursor()

    # Query the database
    cursor.execute(
        "UPDATE transactions SET hash = ? WHERE hash = ?",
        (f"{new_hash}",f"{old_hash}",))
    
    # Commita a transação
    conn.commit()

    # Close Connection
    conn.close()

def fetch_transaction_by_tuple(registro_excel):

    #Conecta ao banco
    conn = conecta_bd()

    # Pega o cursor
    cursor = conn.cursor()

    # Carrega a query
    consulta_sql = f"""
                        SELECT
                            *
                        FROM
                            transactions
                        WHERE
                            data = '{registro_excel['data'].date()}'
                        AND
                            item = '{registro_excel['item']}'
                        AND
                            ocorrencia_dia = '{registro_excel['ocorrencia_dia']}'
                        AND
                            ROUND(valor, 1) = ROUND({registro_excel['valor']}, 1);
                    """

    # Query the database
    cursor.execute(consulta_sql)

    transaction = None

    # Print Result-set
    for (data, item, detalhe, valor, cartao, parcela, ocorrencia_dia, categoria, categoria_fonte, tag, meio, fonte, hash, timestamp, file_timestamp) in cursor:
        
        transaction = {'data': data, 
                       'item': item,
                       'detalhe': detalhe,
                       'valor': valor,
                       'cartao': cartao,
                       'parcela': parcela,
                       'ocorrencia_dia': ocorrencia_dia, 
                       'categoria': categoria,
                       'categoria_fonte': categoria_fonte,
                       'tag': tag,
                       'meio': meio,
                       'arquivo_fonte': fonte,
                       'hash': hash,
                       'timestamp': timestamp,
                       'file_timestamp': file_timestamp}

    if transaction != None:
        return transaction
    else:
        # [ ] Verificar motivo de divergência de hashes
        # if verbose == "true":
        #    print ('Divergência de hash!')
        return None    

def fetch_most_recent_transaction_date_formatted():
    """
    Busca a data da transação mais recente no banco de dados,
    considerando apenas transações não parceladas, e formata para 'DD/Mon' em português.
    """
    # Define o locale para português
    locale.setlocale(locale.LC_TIME, 'pt_BR.utf8')

    # Conecta ao banco
    conn = conecta_bd()

    # Pega o cursor
    cursor = conn.cursor()

    # Executa a consulta para buscar a data mais recente de transações não parceladas
    cursor.execute(
        """
        SELECT MAX(data)
        FROM transactions
        WHERE parcela IS NULL OR parcela = ''
        """
    )

    # Obtém o resultado
    result = cursor.fetchone()
    most_recent_date = result[0] if result else None

    # Fecha a conexão
    conn.close()

    # Formata a data para 'DD/Mon' se existir
    if most_recent_date:
        adjusted_date = most_recent_date - timedelta(days=1)
        formatted_date = adjusted_date.strftime('%d/%b')
        day, month = formatted_date.split('/')
        return f"{day}/{month.capitalize()}"
    return None