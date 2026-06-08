"""
API Gateway – Aplicação Livraria
Porta: 5010

Único ponto de entrada do usuário para a aplicação Livraria.
Orquestra os três microsserviços via chamadas HTTP internas:

    Catálogo de Livros  → http://localhost:5011
    Carrinho de Livros  → http://localhost:5012
    Pagamento de Livros → http://localhost:5013

Rotas
-----
GET  /                        → tela principal (catálogo + carrinho)
GET  /adicionar/<int:livro_id>→ adiciona livro ao carrinho
GET  /remover/<int:livro_id>  → remove livro do carrinho
GET  /pagar                   → finaliza compra via microsserviço pagamento
"""

import os
from flask import Flask, render_template, redirect, url_for, request
import requests as http

app = Flask(__name__)

# URLs configuráveis por variável de ambiente (facilita deploy)
CATALOGO_URL  = os.environ.get("LIV_CATALOGO_URL",  "http://localhost:5011")
CARRINHO_URL  = os.environ.get("LIV_CARRINHO_URL",  "http://localhost:5012")
PAGAMENTO_URL = os.environ.get("LIV_PAGAMENTO_URL", "http://localhost:5013")


def buscar_livros() -> list:
    """Consulta o microsserviço Catálogo e retorna a lista de livros."""
    try:
        return http.get(f"{CATALOGO_URL}/livros", timeout=3).json()
    except http.exceptions.ConnectionError:
        return []


def buscar_carrinho() -> list:
    """Consulta o microsserviço Carrinho e retorna os itens atuais."""
    try:
        return http.get(f"{CARRINHO_URL}/carrinho", timeout=3).json()
    except http.exceptions.ConnectionError:
        return []


@app.route("/")
def index():
    """
    Tela principal da livraria.
    Agrega dados do Catálogo e do Carrinho para exibição unificada.
    Microsserviços utilizados: Catálogo (5011) e Carrinho (5012).
    """
    msg      = request.args.get("msg")
    erro     = request.args.get("erro")
    livros   = buscar_livros()
    carrinho = buscar_carrinho()
    total    = sum(item["preco"] for item in carrinho)
    return render_template(
        "index.html",
        livros=livros,
        carrinho=carrinho,
        total=total,
        msg=msg,
        erro=erro,
    )


@app.route("/adicionar/<int:livro_id>")
def adicionar(livro_id: int):
    """
    Adiciona um livro ao carrinho.
    Consulta o Catálogo (5011) para validar o livro e
    envia POST ao Carrinho (5012) para persistir o item.
    """
    livros = buscar_livros()
    livro  = next((l for l in livros if l["id"] == livro_id), None)
    if not livro:
        return redirect(url_for("index", erro="Livro não encontrado."))
    try:
        http.post(f"{CARRINHO_URL}/carrinho", json=livro, timeout=3)
    except http.exceptions.ConnectionError:
        return redirect(url_for("index", erro="Serviço de carrinho indisponível."))
    return redirect(url_for("index", msg=f'"{livro["nome"]}" adicionado ao carrinho!'))


@app.route("/remover/<int:livro_id>")
def remover(livro_id: int):
    """
    Remove um livro do carrinho.
    Envia DELETE ao Carrinho (5012) para remover a primeira ocorrência do livro.
    """
    try:
        http.delete(f"{CARRINHO_URL}/carrinho/{livro_id}", timeout=3)
    except http.exceptions.ConnectionError:
        return redirect(url_for("index", erro="Serviço de carrinho indisponível."))
    return redirect(url_for("index"))


@app.route("/pagar")
def pagar():
    """
    Finaliza a compra.
    Consulta o Carrinho (5012) para calcular o total e
    envia POST ao Pagamento (5013) para processar a transação.
    """
    carrinho = buscar_carrinho()
    if not carrinho:
        return redirect(url_for("index", erro="O carrinho está vazio."))
    total = sum(item["preco"] for item in carrinho)
    try:
        resposta = http.post(
            f"{PAGAMENTO_URL}/pagamento", json={"total": total}, timeout=3
        ).json()
    except http.exceptions.ConnectionError:
        return redirect(url_for("index", erro="Serviço de pagamento indisponível."))
    return render_template("pagamento.html", mensagem=resposta["mensagem"], total=total)


if __name__ == "__main__":
    app.run(port=5010, debug=True)
