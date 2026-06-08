"""
Microsserviço: Catálogo de Livros – Aplicação Livraria
Porta: 5011

Segunda aplicação construída a partir do Framework de Microsserviços.
Demonstra o reuso de MicroserviceBase num domínio diferente (livraria),
adaptando o hotspot _registrar_rotas() para expor livros em /livros.

Endpoints
---------
GET /health  → {"status": "ok", "servico": "..."}  (frozen spot)
GET /livros  → lista JSON de livros                 (hotspot)
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from flask import jsonify
from shared.base_microservico import MicroserviceBase
from dados import LIVROS


class CatalogoLivrariaService(MicroserviceBase):
    """
    Componente Catálogo – Livraria (Aplicação 2).

    Reutiliza MicroserviceBase (framework) e implementa o hotspot
    _registrar_rotas() com rota e dados específicos do domínio livraria.

    Ponto de adaptação (hotspot):
        Rota /livros (em vez de /produtos) → retorna LIVROS.
        Demonstra como o mesmo framework suporta domínios distintos
        apenas trocando os dados e o nome da rota no hotspot.
    """

    def _registrar_rotas(self) -> None:
        """
        HOTSPOT: rotas do catálogo de livros.

        Adaptação: expõe GET /livros com dados do módulo dados.py.
        Compare com CatalogoService (E-commerce), que expõe /produtos.
        Ambos herdam o mesmo framework; apenas o hotspot muda.
        """

        @self.app.route("/livros")
        def listar_livros():
            """Retorna todos os livros disponíveis no catálogo."""
            return jsonify(LIVROS)


# Ponto de entrada
if __name__ == "__main__":
    servico = CatalogoLivrariaService(__name__, porta=5011)
    servico.executar()
