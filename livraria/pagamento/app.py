"""
[DEPRECADO] Microsserviço: Pagamento de Livros – Aplicação Livraria
Porta: 5013

ATENÇÃO: Este serviço foi SUBSTITUÍDO pelo Pagamento Compartilhado em
pagamento/app.py (porta 5003, body: {total, dominio: "livraria"}).

O gateway da Livraria (livraria/gateway/app.py) já utiliza o serviço
compartilhado. Este arquivo é mantido apenas como referência histórica
que ilustra a evolução da arquitetura: de serviços duplicados por domínio
para Platform Services configurados por dados (dicionário _MENSAGENS).

Endpoints (não usar em produção — inicie pagamento/app.py :5003)
---------
GET  /health    → {"status": "ok", "servico": "..."}       (frozen spot)
POST /pagamento → {"mensagem": str}; body: {total: float}  (hotspot)
"""

from flask import request, jsonify
from shared.base_microservico import MicroserviceBase


class PagamentoLivrariaService(MicroserviceBase):
    """
    Componente Pagamento – Livraria (Aplicação 2).

    Hotspot implementado:
        _registrar_rotas() → mensagem de confirmação adaptada à livraria
        ("Compra de livros confirmada! Bons estudos!").
    """

    def _registrar_rotas(self) -> None:
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


if __name__ == "__main__":
    PagamentoLivrariaService(__name__, porta=5013).executar()
