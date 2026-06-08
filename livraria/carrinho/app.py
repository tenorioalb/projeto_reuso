"""
Microsserviço: Carrinho de Livros – Aplicação Livraria
Porta: 5012

Segunda aplicação – reutiliza MicroserviceBase para gerenciar
o carrinho de livros.  A lógica de negócio é idêntica ao carrinho
do E-commerce; o que muda é a mensagem de confirmação (hotspot).

Endpoints
---------
GET    /health           → {"status": "ok", "servico": "..."}       (frozen spot)
GET    /carrinho         → lista JSON de livros no carrinho          (hotspot)
POST   /carrinho         → adiciona livro; body: {id, nome, preco}   (hotspot)
DELETE /carrinho/<id>    → remove primeira ocorrência do livro       (hotspot)
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from flask import request, jsonify
from shared.base_microservico import MicroserviceBase


class CarrinhoLivrariaService(MicroserviceBase):
    """
    Componente Carrinho – Livraria (Aplicação 2).

    Demonstra reuso do framework: a estrutura de inicialização
    (CORS, health-check, Flask setup) é herdada sem alteração.
    O hotspot _registrar_rotas() adapta apenas a mensagem de retorno.
    """

    def __init__(self, nome: str, porta: int) -> None:
        super().__init__(nome, porta)
        self._carrinho: list = []

    def _registrar_rotas(self) -> None:
        """
        HOTSPOT: rotas do carrinho de livros.

        Adaptação: mensagem de retorno específica para o contexto
        da livraria ("Livro adicionado" vs "Item adicionado").
        """

        @self.app.route("/carrinho", methods=["GET"])
        def ver_carrinho():
            return jsonify(self._carrinho)

        @self.app.route("/carrinho", methods=["POST"])
        def adicionar_ao_carrinho():
            item = request.get_json()
            if not item or "id" not in item or "preco" not in item:
                return jsonify({"erro": "Dados inválidos"}), 400
            self._carrinho.append(item)
            return jsonify({"mensagem": "Livro adicionado ao carrinho!"})

        @self.app.route("/carrinho/<int:livro_id>", methods=["DELETE"])
        def remover_do_carrinho(livro_id):
            for i, item in enumerate(self._carrinho):
                if item["id"] == livro_id:
                    self._carrinho.pop(i)
                    return jsonify({"mensagem": "Livro removido do carrinho."})
            return jsonify({"erro": "Livro não encontrado no carrinho."}), 404


# Ponto de entrada
if __name__ == "__main__":
    servico = CarrinhoLivrariaService(__name__, porta=5012)
    servico.executar()
