"""
[DEPRECADO] Microsserviço: Carrinho de Livros – Aplicação Livraria
Porta: 5012

ATENÇÃO: Este serviço foi SUBSTITUÍDO pelo Carrinho Compartilhado em
carrinho/app.py (porta 5002, ?ns=livraria).

O gateway da Livraria (livraria/gateway/app.py) já utiliza o serviço
compartilhado. Este arquivo é mantido apenas como referência histórica
que ilustra a evolução da arquitetura: de serviços duplicados por domínio
para Platform Services compartilhados por namespace.

Endpoints (não usar em produção — inicie carrinho/app.py :5002)
---------
GET    /health           → {"status": "ok", "servico": "..."}       (frozen spot)
GET    /carrinho         → lista JSON de livros no carrinho          (hotspot)
POST   /carrinho         → adiciona livro; body: {id, nome, preco}   (hotspot)
DELETE /carrinho/<id>    → remove primeira ocorrência do livro       (hotspot)
POST   /carrinho/limpar  → esvazia o carrinho                        (hotspot)
"""

from flask import request, jsonify
from shared.base_microservico import MicroserviceBase


class CarrinhoLivrariaService(MicroserviceBase):
    """
    Componente Carrinho – Livraria (Aplicação 2).

    Hotspot implementado:
        _registrar_rotas() → rotas do carrinho de livros com mensagem
        adaptada ao domínio ("Livro adicionado" vs "Item adicionado").
    """

    def __init__(self, nome: str, porta: int) -> None:
        super().__init__(nome, porta)
        self._carrinho: list = []

    def _registrar_rotas(self) -> None:
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

        @self.app.route("/carrinho/limpar", methods=["POST"])
        def limpar_carrinho():
            self._carrinho.clear()
            return jsonify({"mensagem": "Carrinho esvaziado."})


if __name__ == "__main__":
    CarrinhoLivrariaService(__name__, porta=5012).executar()
