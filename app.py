from flask import Flask, request, Response
from twilio.twiml.messaging_response import MessagingResponse
from biassistant.gemini_connector import interpretar_comando, responder_agno
from biassistant.services.compras_service import inicializar, adicionar_item, listar_itens
from biassistant.services.google_calendar_service import criar_evento
import biassistant.banco as banco
from datetime import datetime
import os
import traceback

app = Flask(__name__)

# --- Inicialização segura do banco ---
try:
    banco.criar_tabelas()
    inicializar()
    print("✅ Banco de dados e tabelas inicializados com sucesso.")
except Exception as e:
    print("❌ Erro ao inicializar banco de dados:", e)
    traceback.print_exc()

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    incoming_msg = request.values.get("Body", "").strip()
    print(f"📩 Mensagem recebida: {incoming_msg}")
    resp = MessagingResponse()
    msg = resp.message()

    try:
        comando = interpretar_comando(incoming_msg)
        print("🧠 Comando interpretado:", comando)

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

            # Converte ISO 8601 com segurança
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
        else:
            resposta = responder_agno(incoming_msg)
            msg.body(resposta)

    except Exception as e:
        print("❌ Erro ao processar comando:")
        traceback.print_exc()
        msg.body("❓ Ocorreu um erro ao processar sua solicitação. Pode tentar reformular?")

    return Response(str(resp), mimetype="application/xml")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # pega porta do Render ou usa 5000 localmente
    print("🌐 Servidor iniciado na porta:", port)
    app.run(host="0.0.0.0", port=port, debug=False)
