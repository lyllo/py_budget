from ai import ai_query

def main():
    print("Bem-vindo ao sistema de consulta! Faça suas perguntas ou digite 'sair' para encerrar.")
    while True:
        # Captura a pergunta do usuário
        pergunta = input("Você: ")
        
        # Verifica se o usuário deseja sair
        if pergunta.lower() in ["sair", "exit", "quit"]:
            print("Encerrando o sistema. Até logo!")
            break
        
        # Chama a função para processar a pergunta
        try:
            resposta = ai_query(pergunta)
            print(f"Assistente: {resposta}")
        except Exception as e:
            print(f"Erro ao processar sua solicitação: {str(e)}")

if __name__ == "__main__":
    main()
