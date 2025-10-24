from biassistant.gemini_connector import interpretar_comando

frase = "Adicionar compromisso amanhã às 14h: reunião com equipe"
resultado = interpretar_comando(frase)

print(resultado)
