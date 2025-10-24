from __future__ import print_function
import os.path
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Escopo de permissão: acesso ao Google Calendar
SCOPES = ['https://www.googleapis.com/auth/calendar']

def autenticar_google_calendar():
    creds = None
    # O token salva o login autorizado (não precisa autenticar toda vez)
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # Se não há credenciais válidas, pede login no navegador
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            caminho_credentials = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'credentials.json'))
            flow = InstalledAppFlow.from_client_secrets_file(caminho_credentials, SCOPES)
            creds = flow.run_local_server(port=0)
        # Salva o token para uso futuro
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)
    return service

if __name__ == '__main__':
    service = autenticar_google_calendar()
    print("✅ Autenticação realizada com sucesso!")
