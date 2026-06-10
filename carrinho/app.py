"""
Microsserviço: Carrinho – Serviço Compartilhado
Porta: 5002

Serviço de plataforma compartilhado entre TODAS as aplicações do framework.
Usa namespaces para isolar o estado do carrinho de cada aplicação:

    ?ns=ecommerce  → carrinho da Loja Didática
    ?ns=livraria   → carrinho da Livraria Didática

Cada namespace mantém seu próprio MemoryRepository independente.
Demonstra o conceito de "Platform Service": lógica de negócio comum
implementada uma única vez e consumida por múltiplas aplicações.

Endpoints
---------
GET    /health                   → {"status": "ok", "servico": "..."}     (frozen spot)
GET    /carrinho?ns=<ns>         → lista itens do namespace               (hotspot)
POST   /carrinho?ns=<ns>         → adiciona item; body: {id, nome, preco} (hotspot)
DELETE /carrinho/<id>?ns=<ns>    → remove item pelo id                    (hotspot)
POST   /carrinho/limpar?ns=<ns>  → esvazia o namespace                    (hotspot)
"""

import logging

from flask import request, jsonify
from shared.base_microservico import MicroserviceBase
from shared.repositorio import MemoryRepository


class CarrinhoCompartilhado(MicroserviceBase):
    """
    Serviço de Carrinho compartilhado (Platform Service).

    Mantém um MemoryRepository por namespace, isolando o estado
    de cada aplicação que usa este serviço.

    Hotspot _configurar_extras(): logging estruturado que identifica
    qual namespace foi afetado em cada operação.
    """

    def __init__(self, nome: str, porta: int) -> None:
        super().__init__(nome, porta)
        self._repositorios: dict[str, MemoryRepository] = {}

    def _repo(self, ns: str) -> MemoryRepository:
        """Retorna (ou cria) o repositório para o namespace dado."""
        if ns not in self._repositorios:
            self._repositorios[ns] = MemoryRepository()
        return self._repositorios[ns]

    def _configurar_extras(self) -> None:
        """HOTSPOT opcional: logging estruturado com identificação de namespace."""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [carrinho] %(levelname)s %(message)s",
            datefmt="%H:%M:%S",
        )
        self.app.logger.setLevel(logging.INFO)
        self.app.logger.info(
            "Carrinho Compartilhado pronto na porta %s", self.porta
        )

    def _registrar_rotas(self) -> None:

        @self.app.route("/carrinho", methods=["GET"])
        def ver_carrinho():
            ns = request.args.get("ns", "default")
            return jsonify(self._repo(ns).listar())

        @self.app.route("/carrinho", methods=["POST"])
        def adicionar_ao_carrinho():
            ns = request.args.get("ns", "default")
            item = request.get_json()
            if not item or "id" not in item or "preco" not in item:
                return jsonify({"erro": "Dados inválidos"}), 400
            self._repo(ns).adicionar(item)
            self.app.logger.info(
                "[%s] Adicionado: %s", ns, item.get("nome")
            )
            return jsonify({"mensagem": "Item adicionado ao carrinho!"})

        @self.app.route("/carrinho/<int:item_id>", methods=["DELETE"])
        def remover_do_carrinho(item_id):
            ns = request.args.get("ns", "default")
            removido = self._repo(ns).remover(item_id)
            if not removido:
                return jsonify({"erro": "Item não encontrado no carrinho."}), 404
            self.app.logger.info("[%s] Removido id=%s", ns, item_id)
            return jsonify({"mensagem": "Item removido do carrinho."})

        @self.app.route("/carrinho/limpar", methods=["POST"])
        def limpar_carrinho():
            ns = request.args.get("ns", "default")
            self._repo(ns).limpar()
            self.app.logger.info("[%s] Carrinho esvaziado.", ns)
            return jsonify({"mensagem": "Carrinho esvaziado."})


if __name__ == "__main__":
    CarrinhoCompartilhado(__name__, porta=5002).executar()
