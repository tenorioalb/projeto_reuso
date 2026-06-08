"""
Microsserviço: Pagamento de Livros – Aplicação Livraria
Porta: 5013

Segunda aplicação – reutiliza MicroserviceBase para processar
pagamentos da livraria.  A mensagem de confirmação é adaptada
ao contexto do domínio livraria (hotspot).

Endpoints
---------
GET  /health    → {"status": "ok", "servico": "..."}       (frozen spot)
POST /pagamento → {"mensagem": str}; body: {total: float}  (hotspot)
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from flask import request, jsonify
from shared.base_microservico import MicroserviceBase


class PagamentoLivrariaService(MicroserviceBase):
    """
    Componente Pagamento – Livraria (Aplicação 2).

    Ponto de adaptação (hotspot):
        Mensagem de confirmação específica para compra de livros,
        diferente da mensagem genérica do E-commerce.
    """

    def _registrar_rotas(self) -> None:
        """
        HOTSPOT: rota de pagamento com mensagem adaptada à livraria.

        Adaptação: a confirmação menciona "compra de livros" e
        encoraja o cliente com "Bons estudos!", diferenciando-se
        semanticamente do pagamento do E-commerce.
        """

        @self.app.route("/pagamento", methods=["POST"])
        def realizar_pagamento():
            dados = request.get_json()
            if not dados or "total" not in dados:
                return jsonify({"erro": "Total não informado"}), 400
            total = dados["total"]
            return jsonify({
                "mensagem": (
                    f"Compra de livros no valor de R${total:.2f} "
                    "confirmada! Bons estudos!"
                )
            })


# Ponto de entrada
if __name__ == "__main__":
    servico = PagamentoLivrariaService(__name__, porta=5013)
    servico.executar()
