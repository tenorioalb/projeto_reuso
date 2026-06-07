from flask import Flask, render_template, request, redirect, url_for, jsonify
import requests

app = Flask(__name__)

CATALOGO_URL = "http://localhost:5001/produtos"
CARRINHO_URL = "http://localhost:5002/carrinho"
PAGAMENTO_URL = "http://localhost:5003/pagamento"

@app.route("/")
def index():
    produtos = requests.get(CATALOGO_URL).json()
    #carrinho = requests.get(CARRINHO_URL).json()
    #total = sum((float(item["preco"])*(int(item["quantidade"]))) for item in carrinho)
    #return render_template("index.html", produtos=produtos, carrinho=carrinho, total=total)
    return render_template("index.html", produtos=produtos, url_cart_landpage=CARRINHO_URL)

#@app.route("/adicionar/<int:produto_id>")
#def adicionar(produto_id):
#    produto = next(p for p in requests.get(CATALOGO_URL).json() if p["id"] == produto_id)
#    requests.post(CARRINHO_URL, json=produto)
#    return redirect(url_for("index"))

#@app.route("/remover/<int:item_id>")
#def remover(item_id):
#    produto = next(p for p in requests.get(CARRINHO_URL).json() if p["id"] == item_id)
#    requests.post(CARRINHO_URL+"/remover", json=produto)
#    return redirect(url_for("index"))

@app.route("/adicionar", methods=["POST"])
def adicionar():
    
    dados_do_formulario = {"id":str(request.form["id"]), "quantidade":str(request.form["quantidade"])}
    
    produto_requisitado = next(product for product in requests.get(CATALOGO_URL).json() if product["id"] == int(dados_do_formulario["id"]))
    produto_requisitado["quantidade"] = int(dados_do_formulario["quantidade"])
    
    print("o produto requisitado é: ", produto_requisitado["nome"])
    print("a quantidade requisitada é: ", produto_requisitado["quantidade"])

    requests.post(CARRINHO_URL+"/adicionar/item", json=produto_requisitado)
    return redirect(url_for("index"))

@app.route("/alterar", methods=["POST"])
def alterar_quantidade():
    dados_do_formulario = {"id_produto":str(request.form["id_produto"]), "quantidade":str(request.form["quantidade"])}
    requests.post(CARRINHO_URL+"/alterar", json=dados_do_formulario)
    return redirect(url_for("index"))

@app.route("/remover", methods=["POST"])
def remover_do_carrinho():
    dados_do_formulario = {"id_produto":str(request.form["id_produto"])}
    requests.post(CARRINHO_URL+"/remover", json=dados_do_formulario)
    return redirect(url_for("index"))

@app.route("/esvaziar", methods=["GET"])
def esvaziar_o_carrinho():
    requests.get(CARRINHO_URL+"/esvaziar")
    return redirect(url_for("index"))

@app.route("/pagamento/confirmado", methods=["GET"])
def pagar():
    # total = float(request.form.get("custo_total"))
    # resposta = requests.post(PAGAMENTO_URL, json={"total": total}).json()
    requests.get(CARRINHO_URL+"/esvaziar")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(port=5000)