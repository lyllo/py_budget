import os
from langchain.chat_models import ChatOpenAI
from langchain.sql_database import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from sqlalchemy import create_engine
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory

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

def get_llm_model():
    llm = ChatOpenAI(
        temperature=0,
        openai_api_key=openai_api_key,
        model="gpt-3.5-turbo-0125"  # Usando o modelo gpt-3.5-turbo-0125 para consulta SQL
    )
    return llm

# Defina o prompt de entrada do SQLDatabaseChain
sqldbchain_prompt = PromptTemplate(
    input_variables=["query"],
    template="""Considerando o seguinte contexto dos dados:

    1. Formatação da Consulta:
    - Considere a pergunta fornecida pelo usuário em linguagem natural.
    - Verifique em sua memória se há contextos anteriores que possam ser relevantes para a consulta.
    - Sua primeira tarefa será criar um código SQL e não Markdown.
    - Não inclua em sua query SQL o comando "sql", colchetes, crases, nem mesmo ponto e vírgula.
    - Não utilize a cláusula LIMIT, a não ser que explicitamente solicitado pelo usuário.

    2. Interpretação de Perguntas:
    - Se o usuário mencionar "este mês", interprete sempre como o mês atual dentro do ano atual.
    - Para perguntas relacionadas a "gastos", exclua transações nas categorias: PROVENTOS, PROVENTOS CMCR, PROVENTOS PQR, ou RESGATE.
    - Ignore todas as transações das categorias: IMPOSTO, INVESTIMENTO, IPTU, OUTROS, PAGAMENTO, TRANSFERÊNCIA, REALOCAÇÃO, RENDIMENTO, TARIFA e TRANSFERÊNCIA.
    - Se o usuário perguntar sobre os seus limites, lembre-se de consultar a tabela LIMITS, onde estão armazenados os limites de gastos mensais de cada categoria.
    - Se o usuário perguntar quanto ainda pode gastar, sem especificar uma categoria nem período de tempo, considere que ele está interessado em saber sobre todo o mês atual.
    - Se o usuário perguntar sobre gastos, como "Quais foram meus maiores gastos neste mês?" ele estará se referindo a transações e não a categorias.

    3. Categorização de Dados:
    - Considere que transações "não categorizadas" possuem a coluna categoria preenchida com um valor em branco (''), e não com NULL.

    Ao gerar a resposta em linguagem natural para o usuário, considere as seguintes regras:

    1. Formatação de Resultados:
    - Suas respostas deverão ser sempre em português do Brasil.
    - Certifique-se de incluir o símbolo da moeda brasileira (R$) no resultado.
    - Utilize separador de milhar com ponto (.) e separador de decimais com vírgula (,).
    - Se a resposta envolver uma lista de transações, apresente os valores dos campos data, item e valor das transações.
    - As datas estão armazenadas no formato aaaa-mm-dd. Ao se referir a datas em sua resposta, traga no formato dd/mm/aaaa.

    2. Estilo de Resposta:
    - Nunca responda na primeira pessoa.
    - Reforce o tom profissional ao referir-se ao usuário como "você".

    Eis a pergunta do usuário:
    {query}
    """
)

# Cria uma instância de SQLDatabaseChain
llm = get_llm_model() # Obtém o modelo de linguagem
db = get_database_connection()  # Obtém a conexão do banco de dados

# Função para processar a entrada do usuário
def process_query(user_query, memory):

    db_chain = SQLDatabaseChain.from_llm(llm=llm, db=db, memory=memory, verbose=False)
    
    # Gera a consulta SQL
    formatted_sqldbchain_prompt = sqldbchain_prompt.format(query=user_query)
    sqldbchain_result = db_chain.run(formatted_sqldbchain_prompt)

    return sqldbchain_result