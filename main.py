from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv
import psycopg2
import requests
import os

load_dotenv()

app = FastAPI(title="Bot WhatsApp - Backend IA")

# ─── Clientes ──────────────────────────────────────────────────────────────────

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

EVOLUTION_URL  = os.getenv("EVOLUTION_API_URL")   # ex: http://localhost:8080
EVOLUTION_KEY  = os.getenv("EVOLUTION_API_KEY")
INSTANCE_NAME  = os.getenv("EVOLUTION_INSTANCE")  # nome da instância criada no painel

# ─── Banco de Dados ─────────────────────────────────────────────────────────────

def get_conn():
    return psycopg2.connect(os.getenv("DATABASE_URL"))

def init_db():
    """Cria a tabela de mensagens se ainda não existir."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS mensagens (
            id         SERIAL PRIMARY KEY,
            telefone   TEXT        NOT NULL,
            role       TEXT        NOT NULL,   -- 'user' ou 'assistant'
            conteudo   TEXT        NOT NULL,
            criado_em  TIMESTAMP   DEFAULT NOW()
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

init_db()

# ─── Helpers ────────────────────────────────────────────────────────────────────

def buscar_historico(telefone: str, limite: int = 10) -> list[dict]:
    """Retorna as últimas mensagens do usuário para montar o contexto."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT role, conteudo
        FROM mensagens
        WHERE telefone = %s
        ORDER BY criado_em DESC
        LIMIT %s
        """,
        (telefone, limite),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    # Inverte para ordem cronológica correta
    return [{"role": r, "content": c} for r, c in reversed(rows)]


def salvar_mensagem(telefone: str, role: str, conteudo: str):
    """Persiste uma mensagem no banco."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO mensagens (telefone, role, conteudo) VALUES (%s, %s, %s)",
        (telefone, role, conteudo),
    )
    conn.commit()
    cur.close()
    conn.close()


def chamar_groq(historico: list[dict], mensagem_nova: str) -> str:
    """Envia o histórico + mensagem atual para o Groq e retorna a resposta."""
    messages = [
        {
            "role": "system",
            "content": (
                "Você é um assistente prestativo e simpático que responde via WhatsApp. "
                "Seja objetivo, use linguagem natural em português brasileiro. "
                "Não use markdown com asteriscos pois o WhatsApp não renderiza igual."
            ),
        },
        *historico,
        {"role": "user", "content": mensagem_nova},
    ]

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        max_tokens=1024,
        temperature=0.7,
    )
    return response.choices[0].message.content


def enviar_whatsapp(telefone: str, texto: str):
    """Envia a resposta de volta ao WhatsApp via Evolution API."""
    if not EVOLUTION_URL or not EVOLUTION_KEY or not INSTANCE_NAME:
        print("⚠️  Variáveis da Evolution API não configuradas. Pulando envio.")
        return

    url = f"{EVOLUTION_URL}/message/sendText/{INSTANCE_NAME}"
    headers = {"apikey": EVOLUTION_KEY, "Content-Type": "application/json"}
    payload = {
        "number": telefone,
        "textMessage": {"text": texto},
    }
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=10)
        r.raise_for_status()
        print(f"✅ Resposta enviada para {telefone}")
    except Exception as e:
        print(f"❌ Erro ao enviar para WhatsApp: {e}")


# ─── Modelos Pydantic ───────────────────────────────────────────────────────────

class MensagemEntrada(BaseModel):
    mensagem: str
    telefone: str = "desconhecido"   # número do remetente (ex: 5511999999999)


# ─── Rotas ──────────────────────────────────────────────────────────────────────

@app.post("/mensagem")
async def receber_mensagem(body: MensagemEntrada):
    """
    Rota principal chamada pelo webhook Flask.
    Fluxo: recebe texto → busca histórico → chama Groq → salva → envia WhatsApp.
    """
    print(f"📨 [{body.telefone}] {body.mensagem}")

    try:
        # 1. Busca histórico do usuário
        historico = buscar_historico(body.telefone)

        # 2. Gera resposta com IA
        resposta = chamar_groq(historico, body.mensagem)

        # 3. Salva no banco
        salvar_mensagem(body.telefone, "user", body.mensagem)
        salvar_mensagem(body.telefone, "assistant", resposta)

        # 4. Envia de volta ao WhatsApp
        enviar_whatsapp(body.telefone, resposta)

        return {"status": "ok", "resposta": resposta}

    except Exception as e:
        print(f"❌ Erro interno: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/historico/{telefone}")
async def ver_historico(telefone: str):
    """Rota auxiliar para consultar o histórico de um usuário (útil para debug)."""
    return {"telefone": telefone, "mensagens": buscar_historico(telefone, limite=50)}


@app.get("/health")
async def health():
    """Verificação de saúde da API."""
    return {"status": "online"}


# ─── Inicialização ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
