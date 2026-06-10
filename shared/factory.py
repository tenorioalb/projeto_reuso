"""
Módulo: shared/factory.py

Função de fábrica para criação de instâncias Flask com CORS.

Quando usar esta função vs. MicroserviceBase
--------------------------------------------
- Use `MicroserviceBase` para microsserviços de negócio (catálogo, carrinho,
  pagamento) que precisam do padrão Template Method com hotspots.
- Use `criar_app()` para componentes de infraestrutura como os API Gateways,
  que orquestram serviços mas não expõem hotspots de negócio próprios.
"""

from flask import Flask
from flask_cors import CORS


def criar_app(nome: str) -> Flask:
    """
    Cria e retorna uma instância Flask com CORS habilitado.

    Parâmetros
    ----------
    nome : str — nome do módulo/serviço (normalmente __name__).

    Retorna
    -------
    Flask: instância pronta para registrar rotas.
    """
    app = Flask(nome)
    CORS(app)
    return app
