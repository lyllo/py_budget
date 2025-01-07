from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    incoming_msg = request.values.get('Body', '').lower()
    resp = MessagingResponse()
    msg = resp.message()

    # Processar a mensagem recebida
    if 'olá' in incoming_msg:
        msg.body('Olá! Como posso ajudar você?')
    elif 'help' in incoming_msg:
        msg.body('Ok, how can I help you?')
    elif 'casada' in incoming_msg:
        msg.body('Sim, com a pessoa mais inteligente e incrível que conhece, o Philippe.')
    else:
        msg.body('Desculpe, não entendi sua mensagem.')

    return str(resp)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
