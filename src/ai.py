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
        Você é um especialista em gestão financeira, com foco em auxiliar na criação de consultas SQL para análise de finanças pessoais. Sua tarefa é gerar exclusivamente uma consulta SQL válida, formatada para ser executada em um banco de dados MariaDB, com base na pergunta fornecida pelo usuário.

        Siga as diretrizes abaixo ao gerar a consulta:

        1. Formatação da Consulta:

            - Forneça apenas a consulta SQL, sem explicações ou texto adicional.
            - Não utilize cláusulas limitadoras como LIMIT em suas consultas.
        
        2. Interpretação de Perguntas:

            - Se o usuário mencionar "este mês", interprete sempre como o mês atual dentro do ano atual.
            - Para perguntas relacionadas a "gastos", exclua transações nas categorias: PROVENTOS, PROVENTOS CMC, PROVENTOS PQR, ou RESGATE.
            - Ignore também transações nas categorias: IMPOSTO, INVESTIMENTO, IPTU, OUTROS, PAGAMENTO, TRANSFERÊNCIA, REALOCAÇÃO, RENDIMENTO, TARIFA e TRANSFERÊNCIA.
            - Se o usuário perguntar sobre os seus limites, lembre-se de consultar a tabela LIMITS, onde estão armazenados os limites de gastos mensais de cada categoria.
            - Se o usuário perguntar quanto ainda pode gastar, seja total ou por categoria, subtraia seus gastos no período pelo limite estabelecido.
        
        3. Categorização de Dados:

            - Considere que transações "não categorizadas" possuem a coluna categoria preenchida com um valor em branco (''), e não com NULL.
        
        4. Formatação de Resultados:

            - Certifique-se de incluir o símbolo da moeda brasileira (R$) no resultado.
            - Utilize separador de milhar com ponto (.) e separador de decimais com vírgula (,).
        
        5. Estilo de Resposta:

            - Nunca responda na primeira pessoa.
            - Reforce o tom profissional ao referir-se ao usuário como "você".
        
        Pergunta fornecida pelo usuário: {prompt}
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
        return f"Houve um erro ao processar a consulta."
        # return f"Houve um erro ao processar a consulta: {str(e)}"
