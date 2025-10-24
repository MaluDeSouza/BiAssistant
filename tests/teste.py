import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from datetime import datetime, timedelta
from biassistant.services.google_calendar_service import criar_evento

if __name__ == "__main__":
    inicio = datetime.now() + timedelta(minutes=5)
    fim = inicio + timedelta(hours=1)

    criar_evento(
        titulo="Reunião de teste com o BiAssistant",
        descricao="Evento criado automaticamente pelo projeto BiAssistant.",
        inicio=inicio,
        fim=fim,
        local="Google Meet"
    )
