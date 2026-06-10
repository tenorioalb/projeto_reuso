"""
API Gateway – Aplicação Livraria
Porta: 5010

Orquestra o catálogo específico da livraria e os serviços
compartilhados de plataforma (carrinho, pagamento e pedidos):

    Catálogo de Livros     → http://localhost:5011  (específico do domínio)
    Carrinho Compartilhado → http://localhost:5002  (namespace: livraria)
    Pagamento Compartilhado→ http://localhost:5003  (dominio: livraria)
    Pedidos Compartilhados → http://localhost:5004  (histórico persistido)

O uso dos serviços compartilhados (5002, 5003, 5004) demonstra o
conceito de Platform Services: lógica comum reutilizada por múltiplas
aplicações sem duplicação de código ou de processo.

Rotas
-----
GET  /                        → tela principal (catálogo + carrinho)
GET  /adicionar/<int:livro_id>→ adiciona livro ao carrinho
GET  /remover/<int:livro_id>  → remove livro do carrinho
GET  /pagar                   → finaliza compra, registra pedido, limpa carrinho
"""

import os
from flask import render_template, redirect, url_for, request
import requests as http

from shared.factory import criar_app

app = criar_app(__name__)

CATALOGO_URL  = os.environ.get("LIV_CATALOGO_URL", "http://localhost:5011")
CARRINHO_URL  = os.environ.get("CARRINHO_URL",     "http://localhost:5002")  # compartilhado
PAGAMENTO_URL = os.environ.get("PAGAMENTO_URL",    "http://localhost:5003")  # compartilhado
PEDIDO_URL    = os.environ.get("PEDIDO_URL",       "http://localhost:5004")  # compartilhado

# Namespace que identifica este gateway no carrinho compartilhado
CARRINHO_NS = os.environ.get("CARRINHO_NS", "livraria")


def buscar_livros() -> list:
    try:
        return http.get(f"{CATALOGO_URL}/livros", timeout=3).json()
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
    livros = buscar_livros()
    livro  = next((l for l in livros if l["id"] == livro_id), None)
    if not livro:
        return redirect(url_for("index", erro="Livro não encontrado."))
    try:
        http.post(
            f"{CARRINHO_URL}/carrinho",
            params={"ns": CARRINHO_NS},
            json=livro,
            timeout=3,
        )
    except http.exceptions.RequestException:
        return redirect(url_for("index", erro="Serviço de carrinho indisponível."))
    return redirect(url_for("index", msg=f'"{livro["nome"]}" adicionado ao carrinho!'))


@app.route("/remover/<int:livro_id>")
def remover(livro_id: int):
    try:
        http.delete(
            f"{CARRINHO_URL}/carrinho/{livro_id}",
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
    app.run(port=5010, debug=True)
