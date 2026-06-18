import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()


def get_conn():
    return psycopg2.connect(os.getenv("DATABASE_URL"))


def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS eventos (
            id SERIAL PRIMARY KEY,
            evento TEXT NOT NULL,
            data DATE NOT NULL,
            hora TIME NOT NULL,
            local TEXT NOT NULL,
            status TEXT DEFAULT 'confirmado',
            criado_em TIMESTAMP DEFAULT NOW()
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS mensagens (
            id SERIAL PRIMARY KEY,
            chat_id TEXT NOT NULL,
            role TEXT NOT NULL,
            conteudo TEXT NOT NULL,
            criado_em TIMESTAMP DEFAULT NOW()
        );
    """)

    conn.commit()
    cur.close()
    conn.close()


def salvar_mensagem(chat_id: str, role: str, conteudo: str):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO mensagens (chat_id, role, conteudo)
        VALUES (%s, %s, %s)
        """,
        (chat_id, role, conteudo)
    )

    conn.commit()
    cur.close()
    conn.close()


def buscar_historico(chat_id: str, limite: int = 10):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT role, conteudo
        FROM mensagens
        WHERE chat_id = %s
        ORDER BY criado_em DESC
        LIMIT %s
        """,
        (chat_id, limite)
    )

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return [{"role": role, "content": conteudo} for role, conteudo in reversed(rows)]


def salvar_evento(evento: str, data: str, hora: str, local: str):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id
        FROM eventos
        WHERE data = %s
          AND hora = %s
          AND local = %s
          AND status = 'confirmado'
        """,
        (data, hora, local)
    )

    conflito = cur.fetchone()

    if conflito:
        cur.close()
        conn.close()
        return None

    cur.execute(
        """
        INSERT INTO eventos (evento, data, hora, local)
        VALUES (%s, %s, %s, %s)
        RETURNING id
        """,
        (evento, data, hora, local)
    )

    evento_id = cur.fetchone()[0]

    conn.commit()
    cur.close()
    conn.close()

    return evento_id


def listar_eventos_do_dia(data: str):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, evento, data, hora, local, status
        FROM eventos
        WHERE data = %s
          AND status = 'confirmado'
        ORDER BY hora
        """,
        (data,)
    )

    rows = cur.fetchall()

    cur.close()
    conn.close()

    eventos = []

    for row in rows:
        eventos.append({
            "id": row[0],
            "evento": row[1],
            "data": str(row[2]),
            "hora": str(row[3])[:5],
            "local": row[4],
            "status": row[5]
        })

    return eventos


def cancelar_evento(data: str, hora: str, local: str = None):
    conn = get_conn()
    cur = conn.cursor()

    if local:
        cur.execute(
            """
            UPDATE eventos
            SET status = 'cancelado'
            WHERE data = %s
              AND hora = %s
              AND local = %s
              AND status = 'confirmado'
            RETURNING id
            """,
            (data, hora, local)
        )
    else:
        cur.execute(
            """
            UPDATE eventos
            SET status = 'cancelado'
            WHERE data = %s
              AND hora = %s
              AND status = 'confirmado'
            RETURNING id
            """,
            (data, hora)
        )

    cancelado = cur.fetchone()

    conn.commit()
    cur.close()
    conn.close()

    return cancelado is not None
