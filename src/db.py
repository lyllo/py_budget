import mariadb
import sys
import hashlib
import files
import os
import configparser

# Query the database
# cur.execute(
#     "SELECT * FROM transactions WHERE item=?", 
#     ("UBER",))

# Print Result-set
# for (data, item, valor, cartao, parcela, categoria, categoria_fonte, tag, meio) in cur:
#     print("Data: " + str(data) + "\n" +
#           "Item: " + item + "\n" +
#           "Valor: " + str(valor) + "\n")

# Configura os paths dos arquivos que serão utilizados
ROOT_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

PATH_TO_CONFIG_FILE = os.path.join(ROOT_DIR, 'config.ini')

# Lê as feature toggles do arquivo de configuração
config = configparser.ConfigParser()
config.read(PATH_TO_CONFIG_FILE)

verbose = config.get('Toggle', 'verbose')

REGISTROS_DUPLICADOS = []
NUM_REGISTROS_SALVOS = 0

# Gera o hash MD5 do registro
def gera_hash_md5(registro):
    data = registro['data']
    item = registro['item']
    valor = registro['valor']
    input_string = str(data) + item + str(valor)
    input_bytes = input_string.encode('utf-8')
    md5_hash = hashlib.md5(input_bytes)
    return md5_hash.hexdigest()

# Verifica se registro existe no banco de dados
def registro_existente(registro, cursor):
    hash_do_registro = gera_hash_md5(registro)
    # Consulta SQL para verificar a existência do registro
    query = "SELECT EXISTS(SELECT 1 FROM transactions WHERE hash = %s)"
    cursor.execute(query, (hash_do_registro,))
    return cursor.fetchone()[0]

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

def salva_registro(registro, conn, meio):

    # Pega o cursor
    cursor = conn.cursor()

    # Pula a linha de cabeçalho
    if(registro['data'] != 'DATA'):

        # Verifica se já existe tupla (data, item, valor) antes de salvar
        if not registro_existente(registro, cursor):

            # Verifica se transação é de cartão
            if ('cartao' not in registro):
                registro['cartao'] = ''
                registro['parcelas'] = ''
            try:
                cursor.execute(
                    "INSERT INTO transactions (data, item, valor, cartao, parcela, categoria, categoria_fonte, tag, meio, hash) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                    (registro['data'], registro['item'], registro['valor'], registro['cartao'], registro['parcelas'], registro['categoria'], registro['categoria_fonte'], registro['tag'], meio, gera_hash_md5(registro)))
                conn.commit()
                global NUM_REGISTROS_SALVOS
                NUM_REGISTROS_SALVOS += 1
            except mariadb.Error as e:
                print(f"Error: {e}")

        else:

            REGISTROS_DUPLICADOS.append(registro)

# Insere registros no banco de dados
def salva_registros(lista_de_registros, source):

    # Conecta ao banco
    conn = conecta_bd()

    for registro in lista_de_registros:
        salva_registro(registro, conn, source)
    
    # Close Connection
    conn.close()

def carrega_historico(input_file):

    num_registros_lidos = 0

    #Conecta ao banco
    conn = conecta_bd()

    # Itera nas linhas do arqauivo de histórico
    for linha in files.ler_arquivo_xlsx(input_file, "Summary"):
        
        # Criar um novo registro
        novo_registro = {'data': linha[0], 
                        'item': linha[1], 
                        'valor': linha[2], 
                        'categoria': linha[3],
                        'tag': linha[4],
                        'meio': linha[5],
                        'categoria_fonte': ''}
        
        salva_registro (novo_registro, conn, linha[5])

        num_registros_lidos += 1

    if verbose == "true":

        print(f"""
            Registros lidos: {num_registros_lidos-1}
            Registros salvos: {NUM_REGISTROS_SALVOS}
            Registros duplicados: {len(REGISTROS_DUPLICADOS)}
            """)