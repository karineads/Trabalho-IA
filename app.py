from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

BACKEND_URL = "http://localhost:8000/mensagem"


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("Mensagem recebida:", data)

    message = data.get("message", {})
    texto = message.get("text")

    if not texto:
        return jsonify({"status": "no message"}), 200

    chat_id = message.get("chat", {}).get("id")

    if not chat_id:
        return jsonify({"status": "no chat id"}), 200

    try:
        requests.post(
            BACKEND_URL,
            json={
                "mensagem": texto,
                "chat_id": str(chat_id)
            },
            timeout=30
        )
    except Exception as e:
        print("Erro ao enviar para backend:", e)

    return jsonify({"status": "ok"}), 200


@app.route("/teste", methods=["GET"])
def teste():
    return "Webhook Telegram rodando"


if __name__ == "__main__":
    app.run(port=5000, debug=True)
