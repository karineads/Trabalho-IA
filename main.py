from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime
import requests
import os
import json

from database import (
    init_db,
    salvar_mensagem,
    buscar_historico,
    salvar_evento,
    listar_eventos_do_dia,
    cancelar_evento
)


load_dotenv()

app = FastAPI(title="Bot Telegram - Agenda com IA")

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

init_db()


def br_para_iso(data_str):
    if not data_str:
        return None

    formatos = ["%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"]

    for formato in formatos:
        try:
            return datetime.strptime(data_str, formato).strftime("%Y-%m-%d")
        except ValueError:
            continue

    return None


def iso_para_br(data_str):
    if not data_str:
        return None

    try:
        return datetime.strptime(str(data_str), "%Y-%m-%d").strftime("%d/%m/%Y")
    except ValueError:
        return str(data_str)


def chamar_groq(historico: list[dict], mensagem_nova: str) -> dict:
    hoje = datetime.now().strftime("%d/%m/%Y")

    messages = [
        {
            "role": "system",
            "content": f"""
Você é um assistente de agenda para Telegram.

Sua tarefa é interpretar a mensagem do usuário e retornar APENAS um JSON válido.

Não escreva explicações.
Não use markdown.
Não use crases.

A data atual para interpretar "hoje", "amanhã", "sexta", etc. é {hoje}.

As intenções possíveis são:
- marcar
- consultar
- cancelar
- incompleto
- desconhecido

O JSON deve seguir este formato:

{{
  "intencao": "marcar",
  "evento": "reunião",
  "data": "08/05/2026",
  "hora": "14:00",
  "local": "sala 3",
  "mensagem": null
}}

Regras:
- Use data no formato brasileiro DD/MM/AAAA.
- Use hora no formato HH:MM.
- Se faltar evento, data, hora ou local para marcar, use intencao "incompleto".
- Para consultar, a data é obrigatória.
- Para cancelar, tente extrair data, hora e local.
- Se faltar informação, coloque null no campo.
- O campo "mensagem" deve explicar o que está faltando quando a intenção for "incompleto".
"""
        },
        *historico,
        {"role": "user", "content": mensagem_nova}
    ]

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        max_tokens=500,
        temperature=0.2
    )

    texto = response.choices[0].message.content.strip()

    try:
        return json.loads(texto)
    except Exception:
        return {
            "intencao": "desconhecido",
            "evento": None,
            "data": None,
            "hora": None,
            "local": None,
            "mensagem": "Não consegui entender sua mensagem. Pode tentar escrever de outro jeito?"
        }


def montar_resposta(dados: dict) -> str:
    intencao = dados.get("intencao")
    evento = dados.get("evento")
    data = dados.get("data")
    hora = dados.get("hora")
    local = dados.get("local")

    data_iso = br_para_iso(data)

    if intencao == "marcar":
        if not evento or not data or not hora or not local:
            return dados.get("mensagem") or "Para marcar, preciso do evento, data, hora e local."

        if not data_iso:
            return "Não consegui entender a data. Use o formato DD/MM/AAAA, por exemplo: 08/05/2026."

        evento_id = salvar_evento(evento, data_iso, hora, local)

        if evento_id is None:
            return f"Esse horário já está ocupado em {local}. Tente outro horário ou local."

        return f"Evento confirmado! {evento} marcado para {iso_para_br(data_iso)} às {hora}, em {local}."

    elif intencao == "consultar":
        if not data:
            return "Qual dia você quer consultar?"

        if not data_iso:
            return "Não consegui entender a data. Use o formato DD/MM/AAAA."

        eventos = listar_eventos_do_dia(data_iso)

        if not eventos:
            return f"Não encontrei eventos confirmados para {iso_para_br(data_iso)}."

        resposta = f"Eventos confirmados para {iso_para_br(data_iso)}:\n"

        for e in eventos:
            resposta += f"- {e['hora']} | {e['evento']} | {e['local']}\n"

        return resposta.strip()

    elif intencao == "cancelar":
        if not data or not hora:
            return "Para cancelar, preciso saber a data e o horário do evento."

        if not data_iso:
            return "Não consegui entender a data. Use o formato DD/MM/AAAA."

        cancelado = cancelar_evento(data_iso, hora, local)

        if cancelado:
            return f"Evento de {iso_para_br(data_iso)} às {hora} cancelado com sucesso."

        return "Não encontrei nenhum evento confirmado com essas informações."

    elif intencao == "incompleto":
        return dados.get("mensagem") or "Faltam algumas informações. Me diga evento, data, hora e local."

    return "Não entendi muito bem. Você quer marcar, consultar ou cancelar um evento?"


def enviar_telegram(chat_id: str, texto: str):
    if not TELEGRAM_TOKEN:
        print("TELEGRAM_BOT_TOKEN não configurado.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": texto
    }

    try:
        r = requests.post(url, json=payload, timeout=10)
        r.raise_for_status()
        print(f"Resposta enviada para chat_id {chat_id}")
    except Exception as e:
        print(f"Erro ao enviar para Telegram: {e}")


class MensagemEntrada(BaseModel):
    mensagem: str
    chat_id: str


@app.post("/mensagem")
async def receber_mensagem(body: MensagemEntrada):
    print(f"📨 [{body.chat_id}] {body.mensagem}")

    try:
        historico = buscar_historico(body.chat_id)

        dados = chamar_groq(historico, body.mensagem)

        resposta = montar_resposta(dados)

        salvar_mensagem(body.chat_id, "user", body.mensagem)
        salvar_mensagem(body.chat_id, "assistant", resposta)

        enviar_telegram(body.chat_id, resposta)

        return {
            "status": "ok",
            "dados_interpretados": dados,
            "resposta": resposta
        }

    except Exception as e:
        print(f"Erro interno: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/historico/{chat_id}")
async def ver_historico(chat_id: str):
    return {
        "chat_id": chat_id,
        "mensagens": buscar_historico(chat_id, limite=50)
    }


@app.get("/health")
async def health():
    return {"status": "online"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
