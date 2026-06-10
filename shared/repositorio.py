"""
Módulo: shared/repositorio.py

Padrão de Projeto: Repository + Strategy
=========================================
BaseRepository define a interface abstrata de acesso a dados (contrato).
As implementações concretas são variantes intercambiáveis (Strategy):

  MemoryRepository  → lista Python em memória (dados perdidos ao reiniciar)
  JsonRepository    → arquivo JSON em disco (dados persistem entre reinicializações)

Uso:
    repo = JsonRepository("dados/pedidos.json")
    repo.adicionar({"id": "abc1", "total": 89.90})
    todos = repo.listar()
"""

import json
import os
from abc import ABC, abstractmethod


class BaseRepository(ABC):
    """
    Interface abstrata do repositório de dados.

    Define o contrato que todas as implementações devem seguir,
    sem expor detalhes de armazenamento às camadas de negócio.
    """

    @abstractmethod
    def listar(self) -> list:
        """Retorna cópia de todos os registros."""

    @abstractmethod
    def adicionar(self, item: dict) -> None:
        """Persiste um novo registro."""

    @abstractmethod
    def remover(self, id) -> bool:
        """Remove o registro com o campo 'id' igual ao valor dado.
        Retorna True se encontrado e removido, False caso contrário."""

    @abstractmethod
    def limpar(self) -> None:
        """Remove todos os registros."""


class MemoryRepository(BaseRepository):
    """
    Estratégia: armazenamento em memória.
    Dados são perdidos ao reiniciar o serviço.
    Adequada para estado de sessão (ex.: carrinho de compras).
    """

    def __init__(self) -> None:
        self._dados: list = []

    def listar(self) -> list:
        return list(self._dados)

    def adicionar(self, item: dict) -> None:
        self._dados.append(item)

    def remover(self, id) -> bool:
        for i, item in enumerate(self._dados):
            if item.get("id") == id:
                self._dados.pop(i)
                return True
        return False

    def limpar(self) -> None:
        self._dados.clear()


class JsonRepository(BaseRepository):
    """
    Estratégia: armazenamento em arquivo JSON.
    Dados persistem entre reinicializações do serviço.
    Adequada para histórico (ex.: pedidos realizados).
    """

    def __init__(self, caminho: str) -> None:
        self._caminho = caminho
        diretorio = os.path.dirname(caminho)
        if diretorio:
            os.makedirs(diretorio, exist_ok=True)
        if not os.path.exists(caminho):
            self._salvar([])

    def listar(self) -> list:
        with open(self._caminho, encoding="utf-8") as f:
            return json.load(f)

    def adicionar(self, item: dict) -> None:
        dados = self.listar()
        dados.append(item)
        self._salvar(dados)

    def remover(self, id) -> bool:
        dados = self.listar()
        for i, item in enumerate(dados):
            if item.get("id") == id:
                dados.pop(i)
                self._salvar(dados)
                return True
        return False

    def limpar(self) -> None:
        self._salvar([])

    def _salvar(self, dados: list) -> None:
        with open(self._caminho, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
