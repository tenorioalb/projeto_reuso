"""
Microsserviço: Catálogo de Produtos – Aplicação E-commerce
Porta: 5001

Endpoints
---------
GET /health    → {"status": "ok", "servico": "..."}   (frozen spot)
GET /produtos  → lista JSON de produtos                (hotspot)
"""

from flask import jsonify
from shared.base_microservico import MicroserviceBase
from .dados import PRODUTOS


class CatalogoService(MicroserviceBase):
    """
    Componente Catálogo – E-commerce (Aplicação 1).

    Hotspot implementado:
        _registrar_rotas() → expõe GET /produtos com eletrônicos.
    """

    def _registrar_rotas(self) -> None:
        @self.app.route("/produtos")
        def listar_produtos():
            return jsonify(PRODUTOS)


if __name__ == "__main__":
    CatalogoService(__name__, porta=5001).executar()
