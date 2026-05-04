import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()


def get_conn():
    return psycopg2.connect(
        os.getenv("DATABASE_URL"),
        cursor_factory=RealDictCursor
    )


def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS eventos (
            id SERIAL PRIMARY KEY,
            evento TEXT NOT NULL,
            data DATE NOT NULL,
            hora TIME NOT NULL,
            local TEXT,
            status TEXT DEFAULT 'confirmado',
            criado_em TIMESTAMP DEFAULT NOW()
        );
    """)

    conn.commit()
    cur.close()
    conn.close()


def horario_disponivel(data: str, hora: str, local: str) -> bool:
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT id FROM eventos
        WHERE data = %s
        AND hora = %s
        AND local = %s
        AND status = 'confirmado'
    """, (data, hora, local))

    ocupado = cur.fetchone() is not None

    cur.close()
    conn.close()

    return not ocupado


def salvar_evento(evento: str, data: str, hora: str, local: str):
    if not horario_disponivel(data, hora, local):
        return None

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO eventos (evento, data, hora, local)
        VALUES (%s, %s, %s, %s)
        RETURNING id
    """, (evento, data, hora, local))

    evento_id = cur.fetchone()["id"]

    conn.commit()
    cur.close()
    conn.close()

    return evento_id


def listar_eventos_do_dia(data: str):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, evento, data, hora, local, status
        FROM eventos
        WHERE data = %s
        AND status = 'confirmado'
        ORDER BY hora
    """, (data,))

    eventos = cur.fetchall()

    cur.close()
    conn.close()

    return eventos


def cancelar_evento(data: str, hora: str, local: str = None):
    conn = get_conn()
    cur = conn.cursor()

    if local:
        cur.execute("""
            UPDATE eventos
            SET status = 'cancelado'
            WHERE data = %s
            AND hora = %s
            AND local = %s
            AND status = 'confirmado'
        """, (data, hora, local))
    else:
        cur.execute("""
            UPDATE eventos
            SET status = 'cancelado'
            WHERE data = %s
            AND hora = %s
            AND status = 'confirmado'
        """, (data, hora))

    alterado = cur.rowcount > 0

    conn.commit()
    cur.close()
    conn.close()

    return alterado