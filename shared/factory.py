"""
Módulo: shared/factory.py
Função de fábrica simples para criação de instâncias Flask com CORS.

Nota: para microsserviços que precisam do padrão Template Method com
hotspots, use shared/base_microservico.py (MicroserviceBase).
Esta função permanece disponível para o API Gateway e scripts simples.
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
