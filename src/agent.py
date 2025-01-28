from ai import process_query
from langchain.memory import ConversationBufferMemory

def main():
    # Cria uma instância de memória para o usuário
    user_id = "5511996477913"
    memory = ConversationBufferMemory(memory_key=user_id)

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
            # Log da memória antes de processar a pergunta
            # print(f"Memória antes: {memory.load_memory_variables({})}")

            resposta = process_query(pergunta, memory)
            print(f"Assistente: {resposta}")

            # Atualiza a memória com a pergunta e a resposta
            memory.save_context({"input": pergunta}, {"output": resposta})

            # Log da memória depois de processar a pergunta
            # print(f"Memória depois: {memory.load_memory_variables({})}")
        
        except Exception as e:
            print(f"Erro ao processar sua solicitação: {str(e)}")

if __name__ == "__main__":
    main()