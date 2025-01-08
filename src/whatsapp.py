from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from ai import ai_query

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    incoming_msg = request.values.get('Body', '').lower()
    resp = MessagingResponse()
    msg = resp.message()

    # Processar a mensagem recebida
    # if 'olá' in incoming_msg:
    #     msg.body('Olá! Como posso ajudar você?')
    # else:
    #     msg.body('Desculpe, não entendi sua mensagem.')

    pergunta = incoming_msg
    resposta = ai_query(pergunta)

    # print(f"Q: {pergunta}")
    # print(f"A: {resposta}")

    msg.body(resposta)

    return str(resp)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
