from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

BACKEND_URL = "http://localhost:8000/mensagem"  # FastAPI


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("📩 Mensagem recebida:", data)

    # ── Extrai o texto da mensagem ──────────────────────────────────────────────
    message = data.get("message", {})
    # A Evolution API pode enviar em campos diferentes dependendo do tipo
    texto = (
        message.get("conversation")          # texto simples
        or message.get("extendedTextMessage", {}).get("text")  # texto longo
        or message.get("text", "")
    )

    if not texto:
        return jsonify({"status": "no message"}), 200

    # ── Extrai o número do remetente ────────────────────────────────────────────
    # formato: "5511999999999@s.whatsapp.net"
    remote_jid = data.get("key", {}).get("remoteJid", "desconhecido")
    telefone = remote_jid.split("@")[0]   # fica só: "5511999999999"

    # Ignora mensagens enviadas pelo próprio bot
    from_me = data.get("key", {}).get("fromMe", False)
    if from_me:
        return jsonify({"status": "own message, ignored"}), 200

    # ── Envia para o FastAPI ────────────────────────────────────────────────────
    try:
        requests.post(
            BACKEND_URL,
            json={"mensagem": texto, "telefone": telefone},
            timeout=30,
        )
    except Exception as e:
        print("Erro ao enviar para backend:", e)

    return jsonify({"status": "ok"}), 200


@app.route("/teste", methods=["GET"])
def teste():
    return "Webhook rodando 🚀"


if __name__ == "__main__":
    app.run(port=5000)
