from flask import Flask, request, jsonify, render_template, url_for, redirect
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# constantes das urls #
# url da landingpage do carrinho
URL_CART_LANDING = "/carrinho"

# url das 'VIEWS' do backend (funções python 'CALLERS')
URL_CART_CALLER_RTN = URL_CART_LANDING + "/retornar"
URL_CART_CALLER_ADD_ITEM = URL_CART_LANDING + "/adicionar/item"
URL_CART_CALLER_CHG_QTD = URL_CART_LANDING + "/alterar/quantidade"
URL_CART_CALLER_REM_ITEM = URL_CART_LANDING + "/remover/item"
URL_CART_CALLER_FLSH = URL_CART_LANDING + "/esvaziar"

carrinho = []

## CALLERS ###
@app.route(URL_CART_LANDING.lower(), methods=["GET"])
def mostrar_carrinho():
    global carrinho
    total = sum((float(item["preco"])*(int(item["quantidade"]))) for item in carrinho)
    return render_template("cart.html", frontend_carrinho=carrinho, frontend_total=total,
                           url_fronted_cart_chg_qtd=URL_CART_CALLER_CHG_QTD,
                           url_fronted_cart_rem_item=URL_CART_CALLER_REM_ITEM,
                           url_fronted_cart_flush=URL_CART_CALLER_FLSH)

@app.route(URL_CART_CALLER_RTN.lower(), methods=["GET"])
def retornar_carrinho():
    return jsonify(carrinho)

@app.route(URL_CART_CALLER_ADD_ITEM.lower(), methods=["POST"])
def adicionar_ao_carrinho():
    
    item_requisitado = request.json
    status = add_to_cart(item_requisitado).json
    print("adicionar ao carrinho caller: " + status["mensagem"])
    return redirect(url_for("mostrar_carrinho"))
    
    

@app.route(URL_CART_CALLER_CHG_QTD.lower(), methods=["POST"])
def alterar_quantidade_no_carrinho():

    dados_recebidos_do_formulario_html = {"id": request.form.get("id"),
                                          "quantidade": request.form.get("quantidade")}
    
    status = change_qtd_into_cart(dados_recebidos_do_formulario_html["id"],
                                  dados_recebidos_do_formulario_html["quantidade"]).json
    
    print("alterar quantidade no carrinho caller: " + status["mensagem"])
    return redirect(url_for("mostrar_carrinho"))
    

@app.route(URL_CART_CALLER_REM_ITEM.lower(), methods=["POST"])
def remover_do_carrinho():
    
    dados_recebidos_do_formulario_html = request.form.get("id")
    status = rem_from_cart(dados_recebidos_do_formulario_html).json
    print("remover do carrinho caller: " + status["mensagem"])
    return redirect(url_for("mostrar_carrinho"))
    

@app.route(URL_CART_CALLER_FLSH.lower(), methods=["GET"])
def esvaziar_carrinho():
    status = flush_cart().json
    print("esvaziar o carrinho caller: " + status["mensagem"])
    return redirect(url_for("mostrar_carrinho"))

### Handlers ###

def add_to_cart(item_requisitado):
    
    global carrinho
    
    print("id do produto que quer adicionar é: ", item_requisitado["id"])
    print("nome do produto que quer adicionar é: ", item_requisitado["nome"])
    print("o preço do produto que quer adicionar é: ", item_requisitado["preco"])
    print("a quantidade de itens que quer adicionar é: ", item_requisitado["quantidade"])

    if(len(carrinho)==0):
        carrinho.append(item_requisitado)
        print("carrinho vazio, produto adicionado")
    else:
        print("carrinho não está vazio")
        produto_existe = False
        
        for item in carrinho:
            if item["id"]==item_requisitado["id"]:
                item["quantidade"] = item["quantidade"]+item_requisitado["quantidade"]
                produto_existe = True
                print("produto já estava no carrinho")

        if not produto_existe:
            carrinho.append(item_requisitado)
            print("produto não estava no carrinho")

    
    return jsonify({"mensagem":"item adicionado ao carrinho!"})

def change_qtd_into_cart(item_id, new_qtd):
    
    global carrinho
    
    id_do_item = int(item_id)
    quantidade_requisitada = int(new_qtd)

    if (quantidade_requisitada>=1):
        print("a quantidade solicitada é um valor válido")
        for item in carrinho:
            if item["id"] == id_do_item:
                print("produto encontrado no carrinho")
                item["quantidade"] = quantidade_requisitada
    else:
        print("a quantidade solicitada não é um valor válido")
        
    return jsonify({"mensagem": "Quantidade do item no carrinho foi alterada!"})

def rem_from_cart(item_id):
    global carrinho
    id_do_item = int(item_id)
    carrinho = [item for item in carrinho if item["id"] != id_do_item]
    return jsonify({"mensagem": "Item removido do carrinho!"})

def flush_cart():
    global carrinho
    carrinho = []
    return jsonify({"mensagem": "O carrinho foi esvaziado!"})

if __name__ == "__main__":
    app.run(port=5002)