"""
API Gateway – Aplicação E-commerce (Loja Didática)
Porta: 5000

Único ponto de entrada do usuário para a aplicação E-commerce.
Orquestra os três microsserviços via chamadas HTTP internas:

    Catálogo de Produtos → http://localhost:5001
    Carrinho de Compras  → http://localhost:5002
    Pagamento            → http://localhost:5003

O gateway não estende MicroserviceBase pois é o orquestrador da
aplicação, não um microsserviço de negócio.  Ele é responsável por
renderizar as views (templates HTML) e compor as respostas dos serviços.

Rotas
-----
GET  /                           → tela principal (catálogo + carrinho)
GET  /adicionar/<int:produto_id> → adiciona produto ao carrinho
GET  /pagar                      → finaliza compra via microsserviço pagamento
"""

import os
from flask import Flask, render_template, redirect, url_for, request
import requests as http

app = Flask(__name__)

# URLs configuráveis por variável de ambiente (sem alterar código)
CATALOGO_URL  = os.environ.get("CATALOGO_URL",  "http://localhost:5001")
CARRINHO_URL  = os.environ.get("CARRINHO_URL",  "http://localhost:5002")
PAGAMENTO_URL = os.environ.get("PAGAMENTO_URL", "http://localhost:5003")


def buscar_produtos() -> list:
    """Consulta o microsserviço Catálogo e retorna a lista de produtos."""
    try:
        return http.get(f"{CATALOGO_URL}/produtos", timeout=3).json()
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
    Tela principal da loja.
    Agrega dados do Catálogo (5001) e do Carrinho (5002) para
    exibição unificada em uma única página.
    """
    msg      = request.args.get("msg")
    erro     = request.args.get("erro")
    produtos = buscar_produtos()
    carrinho = buscar_carrinho()
    total    = sum(item["preco"] for item in carrinho)
    return render_template(
        "index.html",
        produtos=produtos,
        carrinho=carrinho,
        total=total,
        msg=msg,
        erro=erro,
    )


@app.route("/adicionar/<int:produto_id>")
def adicionar(produto_id: int):
    """
    Adiciona produto ao carrinho.
    Consulta o Catálogo (5001) para validar o produto e
    envia POST ao Carrinho (5002) para persistir o item.
    """
    produtos = buscar_produtos()
    produto  = next((p for p in produtos if p["id"] == produto_id), None)
    if not produto:
        return redirect(url_for("index", erro="Produto não encontrado."))
    try:
        http.post(f"{CARRINHO_URL}/carrinho", json=produto, timeout=3)
    except http.exceptions.ConnectionError:
        return redirect(url_for("index", erro="Serviço de carrinho indisponível."))
    return redirect(url_for("index", msg=f'"{produto["nome"]}" adicionado ao carrinho!'))


@app.route("/pagar")
def pagar():
    """
    Finaliza a compra.
    Consulta o Carrinho (5002) para calcular o total e
    envia POST ao Pagamento (5003) para processar a transação.
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
    app.run(port=5000, debug=True)
