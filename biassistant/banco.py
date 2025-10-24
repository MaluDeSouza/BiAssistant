import sqlite3
import os
from datetime import datetime

DB_NAME = "assistente.db"

# ========= Funções de inicialização =========
def criar_tabelas():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Criar tabela agenda
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS agenda (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT NOT NULL,
        data TEXT NOT NULL,
        hora_inicio TEXT NOT NULL,
        hora_fim TEXT NOT NULL,
        marcador TEXT
    )
    ''')

    # Criar tabela lista de compras
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS lista_compras (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item TEXT NOT NULL,
        quantidade INTEGER,
        adicionado_em TEXT NOT NULL
    )
    ''')

    conn.commit()
    conn.close()

# ========= Funções para LISTA DE COMPRAS =========
def add_item(item, quantidade=1):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO lista_compras (item, quantidade, adicionado_em)
        VALUES (?, ?, ?)
    ''', (item, quantidade, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    conn.commit()
    conn.close()

def list_items():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT item, quantidade FROM lista_compras")
    items = cursor.fetchall()
    conn.close()
    return items

# ========= Funções para AGENDA =========
def add_event(titulo, data, hora_inicio, hora_fim, marcador=None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO agenda (titulo, data, hora_inicio, hora_fim, marcador)
        VALUES (?, ?, ?, ?, ?)
    ''', (titulo, data, hora_inicio, hora_fim, marcador))
    conn.commit()
    conn.close()

def list_events():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT titulo, data, hora_inicio, hora_fim, marcador FROM agenda")
    eventos = cursor.fetchall()
    conn.close()
    return eventos

def conectar_banco():
    caminho = os.path.join(os.path.dirname(__file__), '..', 'instance', 'Biassistant.db')
    return sqlite3.connect(caminho)