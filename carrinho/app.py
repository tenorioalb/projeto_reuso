"""
Microsserviço: Carrinho de Compras – Aplicação E-commerce
Porta: 5002

Componente do Framework de Microsserviços.
Implementa o hotspot _registrar_rotas() herdado de MicroserviceBase,
gerenciando o estado do carrinho em memória durante a sessão.

Endpoints
---------
GET  /health    → {"status": "ok", "servico": "..."}   (frozen spot)
GET  /carrinho  → lista JSON de itens no carrinho       (hotspot)
POST /carrinho  → adiciona item; body: {id, nome, preco}(hotspot)
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from flask import request, jsonify
from shared.base_microservico import MicroserviceBase


class CarrinhoService(MicroserviceBase):
    """
    Componente Carrinho – E-commerce (Aplicação 1).

    Mantém o estado do carrinho como lista de instância (_carrinho),
    garantindo que cada processo do microsserviço tenha seu próprio
    estado isolado.

    Ponto de adaptação (hotspot):
        Rotas GET e POST /carrinho com validação de payload JSON.
    """

    def __init__(self, nome: str, porta: int) -> None:
        super().__init__(nome, porta)
        self._carrinho: list = []  # estado em memória da sessão

    def _registrar_rotas(self) -> None:
        """
        HOTSPOT: registra rotas de consulta e adição ao carrinho.

        Adaptação do framework: define a lógica de adição de itens
        e a estrutura de dados esperada (campos obrigatórios: id, preco).
        """

        @self.app.route("/carrinho", methods=["GET"])
        def ver_carrinho():
            """Retorna todos os itens atualmente no carrinho."""
            return jsonify(self._carrinho)

        @self.app.route("/carrinho", methods=["POST"])
        def adicionar_ao_carrinho():
            """
            Adiciona um item ao carrinho.
            Body esperado: {"id": int, "nome": str, "preco": float}
            """
            item = request.get_json()
            if not item or "id" not in item or "preco" not in item:
                return jsonify({"erro": "Dados inválidos"}), 400
            self._carrinho.append(item)
            return jsonify({"mensagem": "Item adicionado ao carrinho!"})


# Ponto de entrada – instancia e executa o microsserviço
if __name__ == "__main__":
    servico = CarrinhoService(__name__, porta=5002)
    servico.executar()
