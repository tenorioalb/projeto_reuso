"""
Microsserviço: Pagamento – Serviço Compartilhado
Porta: 5003

Serviço de plataforma compartilhado entre TODAS as aplicações do framework.
A mensagem de confirmação é adaptada ao domínio informado no body:

    {"total": 89.90, "dominio": "livraria"}
    → "Compra de livros no valor de R$89.90 confirmada! Bons estudos!"

    {"total": 3500.00, "dominio": "ecommerce"}
    → "Pagamento de R$3500.00 realizado com sucesso!"

Demonstra configuração por dados (tabela de mensagens) em vez de
herança: sem subclasses, a variação é declarada no dicionário _MENSAGENS.

Endpoints
---------
GET  /health    → {"status": "ok", "servico": "..."}       (frozen spot)
POST /pagamento → {"mensagem": str}; body: {total, dominio} (hotspot)
"""

from flask import request, jsonify
from shared.base_microservico import MicroserviceBase

_MENSAGENS: dict[str, str] = {
    "ecommerce": "Pagamento de R${total:.2f} realizado com sucesso!",
    "livraria":  "Compra de livros no valor de R${total:.2f} confirmada! Bons estudos!",
}
_MENSAGEM_PADRAO = "Pagamento de R${total:.2f} realizado com sucesso!"


class PagamentoCompartilhado(MicroserviceBase):
    """
    Serviço de Pagamento compartilhado.

    A mensagem de confirmação é um "hotspot de dados": configurada
    por domínio no dicionário _MENSAGENS, sem necessidade de subclasses.
    Adicionar suporte a um novo domínio requer apenas uma nova entrada
    no dicionário — nenhuma alteração no código de lógica.
    """

    def _registrar_rotas(self) -> None:

        @self.app.route("/pagamento", methods=["POST"])
        def realizar_pagamento():
            dados = request.get_json()
            if not dados or "total" not in dados:
                return jsonify({"erro": "Total não informado"}), 400
            total   = float(dados["total"])
            dominio = dados.get("dominio", "")
            template = _MENSAGENS.get(dominio, _MENSAGEM_PADRAO)
            return jsonify({"mensagem": template.format(total=total)})


if __name__ == "__main__":
    PagamentoCompartilhado(__name__, porta=5003).executar()
