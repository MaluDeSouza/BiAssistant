# gemini_connector.py
import os
import re
import json
from dotenv import load_dotenv

# SDK atual
from google import genai
from google.genai import types

# --- Integração com o Agno ---
from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.duckduckgo import DuckDuckGoTools

load_dotenv()

_cached_model = None

def get_client():
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Erro: variável de ambiente GEMINI_API_KEY ou GOOGLE_API_KEY não encontrada.")
        return None
    try:
        client = genai.Client(api_key=api_key)
        return client
    except Exception as e:
        print("Erro ao criar client Gemini:", e)
        return None

def escolher_modelo(client):
    """
    Tenta escolher um modelo preferido. Se não encontrar, pega o primeiro
    que suporte generateContent. Cacheia o resultado.
    """
    global _cached_model
    if _cached_model:
        return _cached_model

    preferred = [
        "gemini-2.5-flash", "gemini-2.5-flash-001",
        "gemini-2.0-flash", "gemini-2.0-flash-001",
        "gemini-2.5-pro", "gemini-2.0-pro"
    ]

    try:
        # tenta encontrar um preferido na lista de modelos
        for m in client.models.list():
            name = getattr(m, "name", None)
            if not name:
                continue
            model_id = name.split("/")[-1]
            if model_id in preferred:
                _cached_model = model_id
                print("Modelo selecionado (preferido):", _cached_model)
                return _cached_model

        # fallback: primeiro que suporte generateContent
        for m in client.models.list():
            model_id = m.name.split("/")[-1]
            supported = getattr(m, "supported_actions", None) or getattr(m, "supported_generation_methods", None) or []
            if "generateContent" in supported:
                _cached_model = model_id
                print("Modelo selecionado (por suporte):", _cached_model)
                return _cached_model

    except Exception as e:
        print("Aviso: não foi possível listar modelos:", e)

    # fallback final
    _cached_model = "gemini-2.0-flash"
    print("Usando fallback model:", _cached_model)
    return _cached_model

def interpretar_comando(frase: str) -> dict:
    """
    Retorna um dict com a interpretação ou {'acao':'erro', 'detalhe': ...}
    """
    client = get_client()
    if client is None:
        return {"acao": "erro", "detalhe": "API key não configurada"}

    prompt = f"""
Você é um assistente que interpreta mensagens de WhatsApp do usuário sobre:
- agenda pessoal (compromissos, reuniões)
- lista de compras

Responda SOMENTE em JSON válido, sem explicações extras.

Ações possíveis:
1. "adicionar_compra" (item, quantidade opcional)
2. "listar_compras"
3. "adicionar_agenda" (titulo, data YYYY-MM-DD, hora_inicio HH:MM, hora_fim HH:MM, marcador opcional)
4. "adicionar_agenda_google" (titulo, data YYYY-MM-DD, hora_inicio HH:MM, hora_fim HH:MM)

Regras:
- Se o usuário disser “adicionar compromisso amanhã às 14h: reunião com equipe”,
  converta “amanhã” para a data correspondente e gere:
  {{
    "acao": "adicionar_agenda_google",
    "titulo": "reunião com equipe",
    "data": "2025-10-23",
    "hora_inicio": "14:00",
    "hora_fim": "15:00"
  }}
  (considere 1h de duração caso não seja especificado)
- Sempre use formato 24h.
- Nunca inclua texto fora do JSON.

Pedido do usuário: "{frase}"
"""

    model = escolher_modelo(client)
    try:
        config = types.GenerateContentConfig(response_mime_type="application/json")
        response = client.models.generate_content(model=model, contents=prompt, config=config)
        text = getattr(response, "text", None) or str(response)

        # extrai JSON do retorno
        match = re.search(r'(\{.*\})', text, re.DOTALL)
        if match:
            payload = match.group(1)
            return json.loads(payload)
        return json.loads(text)

    except Exception as e:
        err = str(e)
        if "404" in err or "not found" in err.lower():
            print("Modelo não encontrado, atualizando lista e tentando outro modelo...")
            global _cached_model
            _cached_model = None
            try:
                model = escolher_modelo(client)
                response = client.models.generate_content(model=model, contents=prompt, config=config)
                text = getattr(response, "text", None) or str(response)
                match = re.search(r'(\{.*\})', text, re.DOTALL)
                if match:
                    return json.loads(match.group(1))
                return {"acao": "erro", "detalhe": "Resposta sem JSON", "raw": text}
            except Exception as e2:
                return {"acao": "erro", "detalhe": str(e2)}
        return {"acao": "erro", "detalhe": err}
    
# Cria o agente Agno usando o Gemini
agno_agent = Agent(
    model=Gemini(id="gemini-2.0-flash"),  # usa o mesmo modelo que já funcionou
    tools=[DuckDuckGoTools()],  # permite fazer pesquisas quando necessário
    instructions="Você é o assistente BiAssistant. Ajude o usuário com agenda, compras e informações gerais."
)

def responder_agno(mensagem: str) -> str:
    """
    Usa o Agno para gerar uma resposta natural e contextual.
    """
    try:
        resposta = agno_agent.run(mensagem)
        return str(resposta)
    except Exception as e:
        print("Erro ao gerar resposta com Agno:", e)
        return "Desculpe, houve um erro ao processar sua mensagem."
