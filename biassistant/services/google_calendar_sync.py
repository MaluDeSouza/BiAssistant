import sqlite3
from datetime import datetime
from biassistant.services.google_calendar_service import criar_evento

def sincronizar_compromissos():
    # Caminho para o banco SQLite
    caminho_banco = "instance/Assistente.db"

    # Conecta ao banco
    conn = sqlite3.connect(caminho_banco)
    cursor = conn.cursor()

    # ✅ Garante que a tabela agenda existe antes de tentar ler
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS agenda (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT NOT NULL,
        data TEXT NOT NULL,
        hora_inicio TEXT,
        hora_fim TEXT,
        marcador TEXT
    );
    """)

    # Busca os compromissos
    cursor.execute("SELECT id, titulo, data, hora_inicio, hora_fim, marcador FROM agenda")
    compromissos = cursor.fetchall()

    if not compromissos:
        print("Nenhum compromisso encontrado no banco local.")
    else:
        print(f"{len(compromissos)} compromissos encontrados. Enviando para o Google Calendar...")

    # ✅ Loop precisa estar DENTRO da função
    for c in compromissos:
        id, titulo, data, hora_inicio, hora_fim, marcador = c

        try:
            # Monta o datetime completo
            formato_data = "%Y-%m-%d %H:%M"
            inicio = datetime.strptime(f"{data} {hora_inicio}", formato_data)
            fim = datetime.strptime(f"{data} {hora_fim}", formato_data)

            # Converte para ISO 8601 com timezone
            inicio_iso = inicio.isoformat() + "-03:00"
            fim_iso = fim.isoformat() + "-03:00"

            # Cria evento no Google Calendar
            criar_evento(titulo, marcador, inicio_iso, fim_iso)

        except Exception as e:
            print(f"❌ Erro ao sincronizar compromisso ID {id}: {e}")

    conn.close()
    print("✅ Sincronização concluída com sucesso!")
