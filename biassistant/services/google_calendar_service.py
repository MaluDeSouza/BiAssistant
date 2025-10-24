from datetime import datetime, timedelta
from biassistant.services.google_calendar_auth import autenticar_google_calendar
import json

def criar_evento(titulo, descricao, inicio, fim, local=None):
    """
    Cria um evento no Google Calendar.
    - titulo: título do evento
    - descricao: descrição opcional
    - inicio, fim: objetos datetime (ou strings ISO 8601)
    - local: endereço ou link (opcional)
    """
    service = autenticar_google_calendar()

    evento = {
        'summary': titulo,
        'location': local,
        'description': descricao,
        'start': {
            'dateTime': inicio if isinstance(inicio, str) else inicio.isoformat(),
            'timeZone': 'America/Sao_Paulo',
        },
        'end': {
            'dateTime': fim if isinstance(fim, str) else fim.isoformat(),
            'timeZone': 'America/Sao_Paulo',
        },
    }
    print(json.dumps(evento, indent=2, ensure_ascii=False))
    event = service.events().insert(calendarId='primary', body=evento).execute()
    print(f"✅ Evento criado: {event.get('htmlLink')}")
    return event
