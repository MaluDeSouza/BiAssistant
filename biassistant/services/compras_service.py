# biassistant/services/compras_service.py
from biassistant.repositories import compra_repository as repo

def inicializar():
    repo.criar_tabela()

def adicionar_item(nome, quantidade=1):
    compras = repo.listar_compras()
    # verifica duplicidade pelo nome (ignorando maiúsculas/minúsculas)
    if any(c[1].lower() == nome.lower() for c in compras):
        return False  # indica que já existe
    repo.adicionar_compra(nome, quantidade)
    return True

def listar_itens():
    compras = repo.listar_compras()
    return [{"id": c[0], "nome": c[1], "quantidade": c[2]} for c in compras]

def editar_item(id, nova_quantidade):
    repo.atualizar_compra(id, nova_quantidade)

def remover_item(id):
    repo.remover_compra(id)
