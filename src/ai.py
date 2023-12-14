from langchain.sql_database import SQLDatabase
from langchain.chat_models import ChatOpenAI
from langchain_experimental.sql import SQLDatabaseChain
from langchain.callbacks import get_openai_callback

import openai

#
# BUSCA POR AI (SW 3.0)
#

# Definir chave de API do OpenAI
openai.api_key = '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'

# Função para fazer a chamada à API e obter a resposta da LLM
def interagir_com_llm(prompt):
    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=prompt,
        max_tokens=100,
        temperature=0.7,
        n=1,
        stop=None,
        timeout=10
    )
    return response.choices[0].text.strip()

# Função para carregar as categorias como string no prompt da LLM
def carrega_categorias():
    categorias = ["ÁGUA",
                "ALIMENTAÇÃO",
                "ALUGUEL",
                "BEBÊ",
                "CARRO",
                "CASA",
                # "COMPRAS",
                "DOMÉSTICA",
                "GÁS",
                "INTERNET",
                "LUZ",
                "MERCADO",
                # "OUTROS",
                "PET",
                "SAÚDE",
                "SERVIÇOS",
                "STREAMING",
                "TRANSPORTE",
                "VIAGENS"]
    return(", ".join(categorias))

# Prepara o prompt para um registro
def prepara_prompt(estabelecimentos):
    prompt = "Dentre as seguintes categorias \"" + carrega_categorias() + "\", qual é a mais adequada para classificar uma compra realizada com um cartão de crédito, cujo nome do estabelecimento comercial se chama " + str(estabelecimentos) + "?"
    # print("Prompt: " + prompt)
    # print(str(estabelecimentos))
    return prompt

def preenche_categorias_com_respostas_da_ai(lista_de_registros, resposta):
    # print(type(resposta))
    for indice, registro in enumerate(lista_de_registros):
        if "categoria" not in registro:
            registro['categoria'] = resposta[indice]
            registro['categoria_fonte'] = 'ai_gpt'

#
# CONECTA O BD AO LLM VIA LANGCHAIN
#

def ai_query(my_prompt):

    username = "root"
    password = "9!nT$u9!XZm3O#nE"
    host = "127.0.0.1"
    port = 3306
    mydatabase = "db_budget"
    md_uri = f"mariadb+mariadbconnector://{username}:{password}@{host}:{port}/{mydatabase}"
    db = SQLDatabase.from_uri(md_uri)

    OPENAI_API_KEY = "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"

    llm = ChatOpenAI(temperature=0, openai_api_key=OPENAI_API_KEY, model='gpt-3.5-turbo')

    db_chain = SQLDatabaseChain(llm=llm, database=db, verbose=True)

    with get_openai_callback() as cb:
        response = db_chain.run(my_prompt)
        print(f"Total Tokens: {cb.total_tokens}")
        print(f"Prompt Tokens: {cb.prompt_tokens}")
        print(f"Completion Tokens: {cb.completion_tokens}")
        print(f"Total Cost (USD): ${cb.total_cost}")