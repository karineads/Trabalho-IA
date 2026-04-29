from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

BACKEND_URL = "http://localhost:8000/mensagem"  # Pessoa 2 (FastAPI)

# 🔹 Webhook da Evolution API
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    print("📩 Mensagem recebida:", data)

    # 🔥 extrair texto (ajustar conforme Evolution API)
    texto = data.get("message", {}).get("text", "")

    if not texto:
        return jsonify({"status": "no message"}), 200

    # 🔹 envia para backend principal (Pessoa 2)
    try:
        requests.post(BACKEND_URL, json={
            "mensagem": texto
        })
    except Exception as e:
        print("Erro ao enviar para backend:", e)

    return jsonify({"status": "ok"}), 200


# 🔹 teste simples de envio (opcional)
@app.route("/teste", methods=["GET"])
def teste():
    return "Webhook rodando 🚀"


app.run(port=5000)