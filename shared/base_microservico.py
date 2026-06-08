"""
Módulo:     shared/base_microservico.py
Projeto:    Framework de Microsserviços para E-commerce / Livraria
Disciplina: Reuso de Software e Metodologias Ágeis – UFAL

Define a classe abstrata MicroserviceBase, núcleo do framework.
Implementa o padrão de projeto Template Method:

    inicializar()          ← Template Method fixo (frozen spot)
        _criar_flask_app() ← frozen spot
        _configurar_cors() ← frozen spot
        _registrar_health()← frozen spot
        _registrar_rotas() ← HOTSPOT obrigatório (abstrato)
        _configurar_extras()← HOTSPOT opcional (hook vazio)
"""

from abc import ABC, abstractmethod
from flask import Flask, jsonify
from flask_cors import CORS


class MicroserviceBase(ABC):
    """
    Classe abstrata base do Framework de Microsserviços.

    Padrão de Projeto: Template Method
    ===================================
    O método `inicializar()` define a sequência fixa (frozen spot)
    de configuração de qualquer microsserviço Flask construído com
    este framework.  Os pontos de variação de negócio são delegados
    às subclasses por meio de hotspots:

    Hotspots
    --------
    _registrar_rotas()    -- (abstract) DEVE ser implementado. Define
                             as rotas HTTP específicas do serviço.
    _configurar_extras()  -- (hook)     PODE ser sobrescrito. Permite
                             adicionar extensões, banco de dados, etc.

    Uso típico
    ----------
    class MeuServico(MicroserviceBase):
        def _registrar_rotas(self):
            @self.app.route("/minha-rota")
            def handler():
                return jsonify({"ok": True})

    if __name__ == "__main__":
        MeuServico(__name__, porta=5001).executar()
    """

    def __init__(self, nome: str, porta: int) -> None:
        """
        Parâmetros
        ----------
        nome  : identificador do microsserviço (passado ao Flask).
        porta : porta TCP em que o servidor vai escutar.
        """
        self.nome = nome
        self.porta = porta
        self.app: Flask | None = None

    # ------------------------------------------------------------------
    # TEMPLATE METHOD (frozen spot) — NÃO sobrescreva este método.
    # ------------------------------------------------------------------
    def inicializar(self) -> Flask:
        """
        Template Method: sequência fixa de inicialização.

        Passo 1 – _criar_flask_app()    (frozen spot)
        Passo 2 – _configurar_cors()    (frozen spot)
        Passo 3 – _registrar_health()   (frozen spot)
        Passo 4 – _registrar_rotas()    (HOTSPOT obrigatório)
        Passo 5 – _configurar_extras()  (HOTSPOT opcional)

        Retorna
        -------
        Flask: instância configurada e pronta para execução.
        """
        self.app = self._criar_flask_app()   # passo 1
        self._configurar_cors()              # passo 2
        self._registrar_health()             # passo 3
        self._registrar_rotas()              # passo 4 ← HOTSPOT
        self._configurar_extras()            # passo 5 ← HOTSPOT
        return self.app

    # ------------------------------------------------------------------
    # FROZEN SPOTS — implementação fixa, núcleo do framework.
    # ------------------------------------------------------------------
    def _criar_flask_app(self) -> Flask:
        """Frozen spot: instancia o objeto Flask com o nome do serviço."""
        return Flask(self.nome)

    def _configurar_cors(self) -> None:
        """Frozen spot: habilita CORS para comunicação entre origens."""
        CORS(self.app)

    def _registrar_health(self) -> None:
        """Frozen spot: registra GET /health padrão para monitoramento."""
        nome_servico = self.nome  # captura para o closure

        @self.app.route("/health")
        def health():
            return jsonify({"status": "ok", "servico": nome_servico})

    # ------------------------------------------------------------------
    # HOTSPOTS — pontos de adaptação para as subclasses.
    # ------------------------------------------------------------------
    @abstractmethod
    def _registrar_rotas(self) -> None:
        """
        HOTSPOT obrigatório.

        Subclasses DEVEM implementar este método registrando todas as
        rotas HTTP específicas do seu domínio de negócio em self.app.

        Exemplo:
            @self.app.route("/produtos")
            def listar():
                return jsonify(self.dados)
        """

    def _configurar_extras(self) -> None:
        """
        HOTSPOT opcional (hook vazio).

        Subclasses PODEM sobrescrever para adicionar extensões Flask,
        configurar banco de dados, registrar blueprints, etc.
        Por padrão não realiza nenhuma ação.
        """

    # ------------------------------------------------------------------
    # MÉTODO UTILITÁRIO
    # ------------------------------------------------------------------
    def executar(self) -> None:
        """Inicializa o serviço (se ainda não foi) e inicia o servidor."""
        if self.app is None:
            self.inicializar()
        self.app.run(port=self.porta, debug=True)
