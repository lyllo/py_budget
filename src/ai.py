import os
from langchain.chat_models import ChatOpenAI
from langchain.sql_database import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from sqlalchemy import create_engine

# Configuração das credenciais
openai_api_key = os.getenv("OPENAI_API_KEY")
mariadb_password = os.getenv("MARIADB_PASSWORD")

if not openai_api_key or not mariadb_password:
    raise ValueError("As chaves OPENAI_API_KEY e MARIADB_PASSWORD são necessárias.")

# Função para obter a conexão com o banco de dados
def get_database_connection():
    username = "root"
    host = "127.0.0.1"
    port = 3306
    database = "db_budget"
    db_uri = f"mariadb+mariadbconnector://{username}:{mariadb_password}@{host}:{port}/{database}"

    # Usando o SQLAlchemy para criar a conexão com o banco de dados
    engine = create_engine(db_uri)
    
    # Criando a instância do SQLDatabase, passando a conexão do SQLAlchemy
    db = SQLDatabase(engine)
    return db

# Função para obter a resposta gerada pelo modelo LLM
def ai_query(prompt):
    llm = ChatOpenAI(
        temperature=0,
        openai_api_key=openai_api_key,
        model="gpt-3.5-turbo-0125"  # Usando o modelo gpt-3.5-turbo para consulta SQL
    )

    # Passa a pergunta diretamente para o modelo LLM para gerar a consulta SQL
    query_prompt = f"""
    Você é um especialista financeiro. Sua tarefa é gerar uma consulta SQL válida com base na pergunta fornecida. 
    A consulta deve ser executada em um banco de dados MariaDB. Apenas forneça a consulta SQL sem explicações ou texto adicional.
    Se o usuário pergunta sobre '''este mês''', considera sempre que ele também está se referindo a '''este ano'''.
    Se o usuário perguntar sobre gastos, desconsidere as transações cuja categoria sejam PROVENTOS, PROVENTOS CMC ou PROVENTOS PQR.
    Desconsidere todas as transações cuja categoria seja IMPOSTO, INVESTIMENTO, IPTU, OUTROS, PAGAMENTO, TRANSFERÊNCIA, REALOCAÇÃO, RENDIMENTO, TARIFA ou TRANSFERÊNCIA.
    As transações que não estão categorizadas, tem um valor em branco na coluna categoria, e não NULL.
    Em suas respostas não se esqueça de incluir o símbolo da moeda brasileira (R$), separador de milhar com ponto (.) e de decimais com vírgula (,).
    Nunca responda na primeira pessoa, responda se referindo ao usuário como '''você'''.
    Pergunta: {prompt}
    """

    # Cria uma instância de SQLDatabaseChain
    db = get_database_connection()  # Obtém a conexão do banco de dados
    db_chain = SQLDatabaseChain.from_llm(llm=llm, db=db, verbose=False)

    try:
        # Obtém a consulta SQL gerada pelo modelo
        response = db_chain.run(query_prompt)

        # Remover a repetição da pergunta, se houver
        response = response.replace(prompt, "").strip()

        # Retorna a resposta limpa
        return response

    except Exception as e:
        return f"Houve um erro ao processar a consulta: {str(e)}"
