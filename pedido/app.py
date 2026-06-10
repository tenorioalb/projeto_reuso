"""
Microsserviço: Pedido – Serviço Compartilhado
Porta: 5004

Registra o histórico de compras de TODAS as aplicações do framework.
Usa JsonRepository para persistência real: os pedidos sobrevivem a
reinicializações do serviço.

Demonstra o padrão Repository + Strategy em uso concreto:
  _configurar_extras() instancia JsonRepository (hotspot opcional),
  tornando o mecanismo de persistência um detalhe de configuração.

Endpoints
---------
GET  /health              → {"status": "ok", "servico": "..."}  (frozen spot)
POST /pedidos             → cria pedido; body: {total, dominio, itens}
GET  /pedidos             → lista pedidos; filtro opcional: ?dominio=livraria
GET  /pedidos/<pedido_id> → detalha um pedido específico
"""

import os
import uuid
from datetime import datetime

from flask import request, jsonify
from shared.base_microservico import MicroserviceBase
from shared.repositorio import JsonRepository


class PedidoService(MicroserviceBase):
    """
    Serviço de Pedidos compartilhado entre E-commerce e Livraria.

    Hotspot _configurar_extras(): instancia JsonRepository apontando para
    dados/pedidos.json — ponto onde a estratégia de persistência é escolhida.
    Uma subclasse poderia sobrescrever _configurar_extras() para usar
    SqliteRepository ou qualquer outra variante sem alterar as rotas.
    """

    def __init__(self, nome: str, porta: int) -> None:
        super().__init__(nome, porta)
        self._repo: JsonRepository | None = None

    def _configurar_extras(self) -> None:
        """
        HOTSPOT opcional: inicializa o repositório de pedidos.
        JsonRepository cria o diretório e o arquivo automaticamente
        na primeira execução.
        """
        self._repo = JsonRepository("dados/pedidos.json")
        self.app.logger.info(
            "PedidoService pronto na porta %s — dados em dados/pedidos.json",
            self.porta,
        )

    def _registrar_rotas(self) -> None:

        @self.app.route("/pedidos", methods=["POST"])
        def criar_pedido():
            dados = request.get_json()
            if not dados or "total" not in dados:
                return jsonify({"erro": "'total' é obrigatório"}), 400

            pedido = {
                "id":      str(uuid.uuid4())[:8],
                "dominio": dados.get("dominio", "desconhecido"),
                "total":   round(float(dados["total"]), 2),
                "itens":   dados.get("itens", []),
                "data":    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status":  "confirmado",
            }
            self._repo.adicionar(pedido)
            self.app.logger.info(
                "Pedido %s criado — R$%.2f [%s]",
                pedido["id"], pedido["total"], pedido["dominio"],
            )
            return jsonify(pedido), 201

        @self.app.route("/pedidos", methods=["GET"])
        def listar_pedidos():
            dominio = request.args.get("dominio")
            todos = self._repo.listar()
            if dominio:
                todos = [p for p in todos if p.get("dominio") == dominio]
            return jsonify(todos)

        @self.app.route("/pedidos/<pedido_id>", methods=["GET"])
        def obter_pedido(pedido_id):
            pedido = next(
                (p for p in self._repo.listar() if p["id"] == pedido_id), None
            )
            if not pedido:
                return jsonify({"erro": "Pedido não encontrado"}), 404
            return jsonify(pedido)


if __name__ == "__main__":
    PedidoService(__name__, porta=5004).executar()
