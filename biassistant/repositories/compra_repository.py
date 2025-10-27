# biassistant/repositories/compra_repository.py
import os
import sqlite3

# Caminho seguro para Render: usa /tmp
DB_PATH = "/tmp/assistente.db"

# Cria a pasta se não existir
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def criar_tabela():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS compras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item TEXT NOT NULL,
            quantidade INTEGER,
            preco REAL
        )
    """)
    conn.commit()
    conn.close()


def adicionar_compra(nome, quantidade=1):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO compras (nome, quantidade) VALUES (?, ?)", (nome, quantidade))
    conn.commit()
    conn.close()

def listar_compras():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM compras")
    resultados = cursor.fetchall()
    conn.close()
    return resultados

def atualizar_compra(id, quantidade):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE compras SET quantidade=? WHERE id=?", (quantidade, id))
    conn.commit()
    conn.close()

def remover_compra(id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM compras WHERE id=?", (id,))
    conn.commit()
    conn.close()
