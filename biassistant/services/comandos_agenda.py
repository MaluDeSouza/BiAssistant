import re
from datetime import datetime, timedelta
import biassistant.banco as banco
from biassistant.services.google_calendar_service import criar_evento

def interpretar_comando_agenda(texto):
    """
    Interpreta comandos como:
    'Adicionar compromisso amanhã às 14h: reunião com equipe.'
    """
    texto = texto.lower().strip()

    # Regex para identificar padrão
    padrao = r"adicionar compromisso (hoje|amanhã|dia \d{1,2}/\d{1,2}) às (\d{1,2})h(?: ?(\d{2}))?: (.+)"
    match = re.search(padrao, texto)

    if not match:
        return {
            "acao": "erro",
            "mensagem": "❌ Não entendi o formato. Use algo como:\n‘Adicionar compromisso amanhã às 14h: reunião com equipe.’"
        }

    dia_str, hora_str, minuto_str, descricao = match.groups()
    minuto_str = minuto_str or "00"

    # Determinar data
    hoje = datetime.now()
    if dia_str == "hoje":
        data_evento = hoje
    elif dia_str == "amanhã":
        data_evento = hoje + timedelta(days=1)
    else:
        dia, mes = map(int, dia_str.replace("dia ", "").split("/"))
        data_evento = datetime(hoje.year, mes, dia)

    # Montar horários
    hora = int(hora_str)
    minuto = int(minuto_str)
    inicio = datetime(data_evento.year, data_evento.month, data_evento.day, hora, minuto)
    fim = inicio + timedelta(hours=1)

    # Salvar no banco
    banco.add_event(
        descricao,
        data_evento.strftime("%Y-%m-%d"),
        f"{hora:02d}:{minuto:02d}",
        f"{(hora+1)%24:02d}:{minuto:02d}",
        "WhatsApp"
    )

    # Enviar pro Google Calendar
    inicio_iso = inicio.isoformat() + "-03:00"
    fim_iso = fim.isoformat() + "-03:00"
    criar_evento(descricao, "Adicionado via WhatsApp", inicio_iso, fim_iso)

    return {
        "acao": "adicionar_agenda",
        "titulo": descricao,
        "data": data_evento.strftime("%Y-%m-%d"),
        "hora_inicio": f"{hora:02d}:{minuto:02d}",
        "hora_fim": f"{(hora+1)%24:02d}:{minuto:02d}",
        "mensagem": f"📅 Compromisso '{descricao}' adicionado para {dia_str} às {hora:02d}:{minuto:02d}."
    }
