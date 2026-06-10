"""
API Gateway – Aplicação E-commerce (Loja Didática)
Porta: 5000

Orquestra os serviços compartilhados de plataforma:

    Catálogo de Produtos   → http://localhost:5001  (específico do domínio)
    Carrinho Compartilhado → http://localhost:5002  (namespace: ecommerce)
    Pagamento Compartilhado→ http://localhost:5003  (dominio: ecommerce)
    Pedidos Compartilhados → http://localhost:5004  (histórico persistido)

Rotas
-----
GET  /                           → tela principal (catálogo + carrinho)
GET  /adicionar/<int:produto_id> → adiciona produto ao carrinho
GET  /remover/<int:produto_id>   → remove produto do carrinho
GET  /pagar                      → finaliza compra, registra pedido, limpa carrinho
"""

import os
from flask import render_template, redirect, url_for, request
import requests as http

from shared.factory import criar_app

app = criar_app(__name__)

CATALOGO_URL  = os.environ.get("CATALOGO_URL",  "http://localhost:5001")
CARRINHO_URL  = os.environ.get("CARRINHO_URL",  "http://localhost:5002")
PAGAMENTO_URL = os.environ.get("PAGAMENTO_URL", "http://localhost:5003")
PEDIDO_URL    = os.environ.get("PEDIDO_URL",    "http://localhost:5004")

# Namespace que identifica este gateway no carrinho compartilhado
CARRINHO_NS = os.environ.get("CARRINHO_NS", "ecommerce")


def buscar_produtos() -> list:
    try:
        return http.get(f"{CATALOGO_URL}/produtos", timeout=3).json()
    except http.exceptions.RequestException:
        return []


def buscar_carrinho() -> list:
    try:
        return http.get(
            f"{CARRINHO_URL}/carrinho", params={"ns": CARRINHO_NS}, timeout=3
        ).json()
    except http.exceptions.RequestException:
        return []


@app.route("/")
def index():
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
    produtos = buscar_produtos()
    produto  = next((p for p in produtos if p["id"] == produto_id), None)
    if not produto:
        return redirect(url_for("index", erro="Produto não encontrado."))
    try:
        http.post(
            f"{CARRINHO_URL}/carrinho",
            params={"ns": CARRINHO_NS},
            json=produto,
            timeout=3,
        )
    except http.exceptions.RequestException:
        return redirect(url_for("index", erro="Serviço de carrinho indisponível."))
    return redirect(url_for("index", msg=f'"{produto["nome"]}" adicionado ao carrinho!'))


@app.route("/remover/<int:produto_id>")
def remover(produto_id: int):
    try:
        http.delete(
            f"{CARRINHO_URL}/carrinho/{produto_id}",
            params={"ns": CARRINHO_NS},
            timeout=3,
        )
    except http.exceptions.RequestException:
        return redirect(url_for("index", erro="Serviço de carrinho indisponível."))
    return redirect(url_for("index"))


@app.route("/pedidos")
def historico_pedidos():
    try:
        pedidos = http.get(
            f"{PEDIDO_URL}/pedidos", params={"dominio": CARRINHO_NS}, timeout=3
        ).json()
    except http.exceptions.RequestException:
        pedidos = None
    return render_template("pedidos.html", pedidos=pedidos)


@app.route("/pagar")
def pagar():
    carrinho = buscar_carrinho()
    if not carrinho:
        return redirect(url_for("index", erro="O carrinho está vazio."))
    total = sum(item["preco"] for item in carrinho)

    # 1. Processar pagamento
    try:
        resposta = http.post(
            f"{PAGAMENTO_URL}/pagamento",
            json={"total": total, "dominio": CARRINHO_NS},
            timeout=3,
        ).json()
    except http.exceptions.RequestException:
        return redirect(url_for("index", erro="Serviço de pagamento indisponível."))

    # 2. Registrar pedido e capturar ID gerado
    pedido = None
    try:
        pedido = http.post(
            f"{PEDIDO_URL}/pedidos",
            json={"total": total, "dominio": CARRINHO_NS, "itens": carrinho},
            timeout=3,
        ).json()
    except http.exceptions.RequestException:
        pass

    # 3. Limpar carrinho após confirmação
    try:
        http.post(
            f"{CARRINHO_URL}/carrinho/limpar",
            params={"ns": CARRINHO_NS},
            timeout=3,
        )
    except http.exceptions.RequestException:
        pass

    return render_template(
        "pagamento.html",
        mensagem=resposta["mensagem"],
        total=total,
        pedido=pedido,
        itens=carrinho,
    )


if __name__ == "__main__":
    app.run(port=5000, debug=True)
