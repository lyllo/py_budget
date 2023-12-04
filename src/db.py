import mariadb
import sys
import hashlib

# Query the database
# cur.execute(
#     "SELECT * FROM transactions WHERE item=?", 
#     ("UBER",))

# Print Result-set
# for (data, item, valor, cartao, parcela, categoria, categoria_fonte, tag, meio) in cur:
#     print("Data: " + str(data) + "\n" +
#           "Item: " + item + "\n" +
#           "Valor: " + str(valor) + "\n")

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

# Insere registros no banco de dados
def salva(lista_de_registros, meio):

    # Connect to MariaDB Platform
    try:
        conn = mariadb.connect(
            user="root",
            password="9!nT$u9!XZm3O#nE",
            host="127.0.0.1",
            port=3306,
            database="my_finances"

    )
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)

    # Get Cursor
    cursor = conn.cursor()

    for registro in lista_de_registros:
        if not registro_existente(registro, cursor):
            if ('cartao' not in registro):
                registro['cartao'] = ''
                registro['parcelas'] = ''
            try:
                cursor.execute(
                    "INSERT INTO transactions (data, item, valor, cartao, parcela, categoria, categoria_fonte, tag, meio, hash) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                    (registro['data'], registro['item'], registro['valor'], registro['cartao'], registro['parcelas'], registro['categoria'], registro['source'], registro['tag'], meio, gera_hash_md5(registro)))
                conn.commit()
            except mariadb.Error as e:
                print(f"Error: {e}")
    
    # Close Connection
    conn.close()