# biassistant/models/compra.py

class Compra:
    def __init__(self, id, nome, quantidade=1):
        self.id = id
        self.nome = nome
        self.quantidade = quantidade

    def __str__(self):
        return f"{self.nome} (x{self.quantidade})"
