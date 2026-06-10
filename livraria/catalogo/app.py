"""
Microsserviço: Catálogo de Livros – Aplicação Livraria
Porta: 5011

Segunda aplicação construída a partir do Framework de Microsserviços.
Demonstra o reuso de MicroserviceBase num domínio diferente (livraria).

Endpoints
---------
GET /health  → {"status": "ok", "servico": "..."}  (frozen spot)
GET /livros  → lista JSON de livros                 (hotspot)
"""

from flask import jsonify
from shared.base_microservico import MicroserviceBase
from .dados import LIVROS


class CatalogoLivrariaService(MicroserviceBase):
    """
    Componente Catálogo – Livraria (Aplicação 2).

    Hotspot implementado:
        _registrar_rotas() → expõe GET /livros (em vez de /produtos).
        Demonstra como o mesmo framework suporta domínios distintos
        apenas trocando os dados e o nome da rota no hotspot.
    """

    def _registrar_rotas(self) -> None:
        @self.app.route("/livros")
        def listar_livros():
            return jsonify(LIVROS)


if __name__ == "__main__":
    CatalogoLivrariaService(__name__, porta=5011).executar()
