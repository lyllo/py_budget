from ai import ai_query

# Pergunta do usuário
pergunta = "Em que categoria estão os maiores gastos do ano passado?"

# Chamada à função para obter a resposta
resposta = ai_query(pergunta)

# Exibe a resposta gerada
print(f"Q: {pergunta}")
print(f"A: {resposta}")