import os
import sys
import warnings

# Suppress warnings from google.generativeai and related packages early
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", message=".*google.generativeai.*")

import google.generativeai as genai
from langchain.chat_models import ChatOpenAI
from langchain.sql_database import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from sqlalchemy import create_engine
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
import tiktoken

# Configuração das credenciais
openai_api_key = os.getenv("OPENAI_API_KEY")
mariadb_password = os.getenv("MARIADB_PASSWORD")
gemini_api_key = os.getenv("GEMINI_API_KEY")

# Avisos de chaves faltantes
if not gemini_api_key:
    # print("AVISO: GEMINI_API_KEY não encontrada no ambiente. Categorização por IA será desativada.")
    pass
if not openai_api_key:
    # print("AVISO: OPENAI_API_KEY não encontrada no ambiente. Consultas SQL serão desativadas.")
    pass
if not mariadb_password:
    # print("AVISO: MARIADB_PASSWORD não encontrada no ambiente.")
    pass

# Lista oficial das 18 categorias do usuário (conforme imagem fornecida)
OFFICIAL_CATEGORIES = [
    "ALUGUEL", "DOMÉSTICA", "EDUCAÇÃO", "SAÚDE", "MERCADO",
    "LAZER", "CARRO", "COMPRAS", "ALIMENTAÇÃO", "PET",
    "LUZ", "SERVIÇOS", "CASA", "TRANSPORTE", "INTERNET",
    "STREAMING", "ÁGUA", "GÁS"
]

def get_database_connection():
    if not mariadb_password:
        return None
    username = "root"
    host = "127.0.0.1"
    port = 3306
    database = "db_budget"
    db_uri = f"mariadb+mariadbconnector://{username}:{mariadb_password}@{host}:{port}/{database}"
    engine = create_engine(db_uri)
    db = SQLDatabase(engine)
    return db

def get_llm_model():
    """Retorna o modelo OpenAI para consultas SQL (Legado)"""
    if not openai_api_key:
        return None
    llm = ChatOpenAI(
        temperature=0,
        openai_api_key=openai_api_key,
        model="gpt-3.5-turbo-0125"
    )
    return llm

def get_gemini_model():
    """Retorna o modelo Gemini para categorização (Gratuito)"""
    if not gemini_api_key:
        return None
    try:
        genai.configure(api_key=gemini_api_key)
        # Usando o flash para velocidade e custo gratuito
        model = genai.GenerativeModel('models/gemini-2.0-flash')
        return model
    except Exception as e:
        return None

def prepara_prompt(item):
    """Prepara o prompt para categorização de transações"""
    categorias_str = ", ".join(OFFICIAL_CATEGORIES)
    prompt = f"""Classifique a seguinte transação em UMA das categorias abaixo:
{categorias_str}

Transação: "{item}"

Responda APENAS com o nome da categoria, SEM pontuação ou explicação adicional.
Se não tiver certeza, responda "OUTROS"."""
    return prompt

def interagir_com_llm(prompt):
    """Categorização utilizando Google Gemini (Gratuito/Billing)"""
    if not gemini_api_key:
        return "OUTROS", None
    try:
        model = get_gemini_model()
        if not model:
            return "OUTROS", None
            
        # Nova sintaxe para generate_content
        response = model.generate_content(
            contents=prompt
        )
        
        text = response.text.strip().upper()
        usage = response.usage_metadata
        return text, usage
    except Exception as e:
        print(f"Erro ao interagir com Gemini: {e}")
        return "OUTROS", None

def process_query(user_query, memory):
    """Processamento de query SQL em linguagem natural (Legado - OpenAI)"""
    llm = get_llm_model()
    db = get_database_connection()
    if not llm or not db:
        return "Serviço de consulta SQL não disponível devido a chaves de API/DB ausentes."
    
    db_chain = SQLDatabaseChain.from_llm(llm=llm, db=db, memory=memory, verbose=False)
    # Nota: Simplificado para manter compatibilidade
    return db_chain.run(user_query)
