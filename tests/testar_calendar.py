from datetime import datetime, timedelta
from biassistant.services.google_calendar_service import criar_evento

inicio = datetime.now() + timedelta(hours=1)
fim = inicio + timedelta(hours=1)

criar_evento(
    titulo="Teste integração Gemini + Twilio",
    descricao="Teste automático",
    inicio=inicio,
    fim=fim,
    local="Online"
)
