"""
Microsserviço: Pagamento – Aplicação E-commerce
Porta: 5003

Componente do Framework de Microsserviços.
Implementa o hotspot _registrar_rotas() herdado de MicroserviceBase,
processando a confirmação de pagamento com base no total recebido.

Endpoints
---------
GET  /health    → {"status": "ok", "servico": "..."}   (frozen spot)
POST /pagamento → {"mensagem": str}; body: {total: float}(hotspot)
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from flask import request, jsonify
from shared.base_microservico import MicroserviceBase


class PagamentoService(MicroserviceBase):
    """
    Componente Pagamento – E-commerce (Aplicação 1).

    Recebe o total da compra e retorna uma mensagem de confirmação.
    Em um sistema real, esta classe integraria com uma gateway de
    pagamento externa (ex.: Stripe, PagSeguro).

    Ponto de adaptação (hotspot):
        Rota POST /pagamento com mensagem específica do domínio.
    """

    def _registrar_rotas(self) -> None:
        """
        HOTSPOT: registra rota de processamento de pagamento.

        Adaptação do framework: define a lógica de validação do total
        e o formato da mensagem de confirmação devolvida ao gateway.
        """

        @self.app.route("/pagamento", methods=["POST"])
        def realizar_pagamento():
            """
            Processa o pagamento do carrinho.
            Body esperado: {"total": float}
            """
            dados = request.get_json()
            if not dados or "total" not in dados:
                return jsonify({"erro": "Total não informado"}), 400
            total = dados["total"]
            return jsonify({
                "mensagem": f"Pagamento de R${total:.2f} realizado com sucesso!"
            })


# Ponto de entrada – instancia e executa o microsserviço
if __name__ == "__main__":
    servico = PagamentoService(__name__, porta=5003)
    servico.executar()
