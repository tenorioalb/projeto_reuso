"""
Microsserviço: Catálogo de Produtos – Aplicação E-commerce
Porta: 5001

Componente do Framework de Microsserviços.
Implementa o hotspot _registrar_rotas() herdado de MicroserviceBase,
expondo a lista de produtos eletrônicos disponíveis na loja.

Endpoints
---------
GET /health    → {"status": "ok", "servico": "..."}   (frozen spot)
GET /produtos  → lista JSON de produtos                (hotspot)
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from flask import jsonify
from shared.base_microservico import MicroserviceBase
from dados import PRODUTOS


class CatalogoService(MicroserviceBase):
    """
    Componente Catálogo – E-commerce (Aplicação 1).

    Herda de MicroserviceBase e implementa o hotspot _registrar_rotas()
    para expor os produtos eletrônicos da loja via GET /produtos.

    Ponto de adaptação (hotspot):
        Rota /produtos → retorna PRODUTOS (lista de eletrônicos).
    """

    def _registrar_rotas(self) -> None:
        """
        HOTSPOT: registra rotas específicas do catálogo de eletrônicos.

        Esta é a adaptação do framework para o domínio E-commerce:
        define qual coleção de dados é exposta e em qual endpoint.
        """

        @self.app.route("/produtos")
        def listar_produtos():
            """Retorna todos os produtos disponíveis no catálogo."""
            return jsonify(PRODUTOS)


# Ponto de entrada – instancia e executa o microsserviço
if __name__ == "__main__":
    servico = CatalogoService(__name__, porta=5001)
    servico.executar()
