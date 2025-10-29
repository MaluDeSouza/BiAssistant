from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from biassistant.gemini_connector import interpretar_comando, responder_agno
from biassistant.services.compras_service import inicializar, adicionar_item, listar_itens
from biassistant.services.google_calendar_service import criar_evento
import biassistant.banco as banco
from datetime import datetime
import os

app = Flask(__name__)

# Inicializa banco e tabela de compras
banco.criar_tabelas()
inicializar()

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    incoming_msg = request.values.get("Body", "").strip()
    resp = MessagingResponse()
    msg = resp.message()

    comando = interpretar_comando(incoming_msg)
    print("Comando interpretado:", comando)

    try:
        # --- LISTA DE COMPRAS ---
        if comando["acao"] == "adicionar_compra":
            sucesso = adicionar_item(comando["item"], comando.get("quantidade", 1))
            if sucesso:
                msg.body(f"✅ Item '{comando['item']}' adicionado à lista de compras!")
            else:
                msg.body(f"⚠️ O item '{comando['item']}' já consta na lista de compras.")

        elif comando["acao"] == "listar_compras":
            itens = listar_itens()
            if itens:
                lista = "\n- ".join([f"{i['nome']} (x{i['quantidade']})" for i in itens])
                msg.body("🛒 Sua lista de compras:\n- " + lista)
            else:
                msg.body("🛒 Sua lista de compras está vazia.")

        # --- AGENDA LOCAL ---
        elif comando["acao"] == "adicionar_agenda":
            banco.add_event(
                comando["titulo"],
                comando["data"],
                comando["hora_inicio"],
                comando["hora_fim"],
                comando.get("marcador")
            )
            msg.body(f"📅 Compromisso '{comando['titulo']}' adicionado à agenda local!")

        # --- AGENDA GOOGLE CALENDAR ---
        elif comando["acao"] == "adicionar_agenda_google":
            data = comando["data"]
            hora_inicio = comando["hora_inicio"]
            hora_fim = comando["hora_fim"]

            inicio = datetime.fromisoformat(f"{data}T{hora_inicio}:00")
            fim = datetime.fromisoformat(f"{data}T{hora_fim}:00")

            criar_evento(
                titulo=comando["titulo"],
                descricao="Adicionado via Assistente WhatsApp",
                inicio=inicio,
                fim=fim
            )

            msg.body(f"✅ Compromisso '{comando['titulo']}' adicionado ao Google Calendar!")

        # --- FALLBACK: AGNO (resposta natural) ---
        elif comando.get("acao") == "erro" or comando.get("acao") not in [
            "adicionar_compra",
            "listar_compras",
            "adicionar_agenda",
            "adicionar_agenda_google"
        ]:
            resposta = responder_agno(incoming_msg)
            msg.body(resposta)

        else:
            msg.body("⚠️ Não consegui interpretar sua solicitação. Tente novamente.")

    except Exception as e:
        msg.body("❓ Não entendi sua mensagem. Pode tentar reformular?")
        print("Erro ao processar comando:", e, comando)

    return str(resp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # pega a porta do Render ou usa 5000 localmente
    app.run(host="0.0.0.0", port=port, debug=False)