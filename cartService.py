from flask import Flask, request, jsonify, render_template, url_for, redirect, flash
from flask_cors import CORS

# ==========================================
# 1. MODELO DE NEGÓCIO (ORIENTADO A OBJETOS)
# ==========================================
class Carrinho:
    """Classe responsável por gerenciar o estado e regras do carrinho de compras."""
    
    def __init__(self):
        self.itens = []

    def obter_total(self) -> float:
        """Calcula o valor total acumulado no carrinho."""
        return sum((float(item["preco"]) * int(item["quantidade"])) for item in self.itens)

    def adicionar(self, item_requisitado: dict) -> str:
        """Adiciona um item ou incrementa a quantidade se ele já existir."""
        # Garante a tipagem correta dos dados recebidos
        item_requisitado["id"] = int(item_requisitado["id"])
        item_requisitado["quantidade"] = int(item_requisitado["quantidade"])
        item_requisitado["preco"] = float(item_requisitado["preco"])

        for item in self.itens:
            if item["id"] == item_requisitado["id"]:
                item["quantidade"] += item_requisitado["quantidade"]
                return "Produto já estava no carrinho, quantidade incrementada."

        self.itens.append(item_requisitado)
        return "Produto novo adicionado ao carrinho."

    def alterar_quantidade(self, item_id: int, nova_qtd: int) -> str:
        """Altera a quantidade de um item específico se o valor for válido."""
        if nova_qtd >= 1:
            for item in self.itens:
                if item["id"] == int(item_id):
                    item["quantidade"] = int(nova_qtd)
                    return "Quantidade do item no carrinho foi alterada!"
            return "Item não encontrado no carrinho."
        return "A quantidade solicitada não é um valor válido (menor que 1)."

    def remover(self, item_id: int) -> str:
        """Remove um item do carrinho com base no ID."""
        self.itens = [item for item in self.itens if item["id"] != int(item_id)]
        return "Item removido do carrinho!"

    def esvaziar(self) -> str:
        """Remove todos os elementos do carrinho."""
        self.itens = []
        return "O carrinho foi esvaziado!"


# ==========================================
# 2. CONFIGURAÇÃO DA APLICAÇÃO E ROTAS
# ==========================================
class ServidorCarrinho:
    """Classe responsável por gerenciar a infraestrutura do Flask e rotas de rede."""
    
    # Constantes de URL centralizadas como atributos de classe
    URL_GATEWAY_LANDING = "http://localhost:5000/"
    URL_CATALOG_LANDING = "http://localhost:5001/"
    URL_PAYMENT_LANDING = "http://localhost:5003/"
    URL_FRONTEND_CART_CHECKOUT = URL_PAYMENT_LANDING + "pagar"
    
    URL_CART_LANDING = "/carrinho"
    URL_CART_CALLER_RTN = URL_CART_LANDING + "/retornar"
    URL_CART_CALLER_ADD_ITEM = URL_CART_LANDING + "/adicionar/item"
    URL_CART_CALLER_CHG_QTD = URL_CART_LANDING + "/alterar/quantidade"
    URL_CART_CALLER_REM_ITEM = URL_CART_LANDING + "/remover/item"
    URL_CART_CALLER_FLSH = URL_CART_LANDING + "/esvaziar"

    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)
        
        # OBRIGATÓRIO: Defina uma chave secreta qualquer para ativar o sistema de flash
        self.app.secret_key = "abc"

        # Instanciação do objeto de negócio (Substitui a antiga variável global)
        self.carrinho = Carrinho()
        
        # Vincula as rotas HTTP do Flask aos métodos da classe
        self._registrar_rotas()

    def _registrar_rotas(self):
        """Mapeia as URLs para as respectivas funções internas."""
        self.app.add_url_rule(self.URL_CART_LANDING.lower(), "mostrar_carrinho", self.mostrar_carrinho, methods=["GET"])
        self.app.add_url_rule(self.URL_CART_CALLER_RTN.lower(), "retornar_carrinho", self.retornar_carrinho, methods=["GET"])
        self.app.add_url_rule(self.URL_CART_CALLER_ADD_ITEM.lower(), "adicionar_ao_carrinho", self.adicionar_ao_carrinho, methods=["POST"])
        self.app.add_url_rule(self.URL_CART_CALLER_CHG_QTD.lower(), "alterar_quantidade_no_carrinho", self.alterar_quantidade_no_carrinho, methods=["POST"])
        self.app.add_url_rule(self.URL_CART_CALLER_REM_ITEM.lower(), "remover_do_carrinho", self.remover_do_carrinho, methods=["POST"])
        self.app.add_url_rule(self.URL_CART_CALLER_FLSH.lower(), "esvaziar_carrinho", self.esvaziar_carrinho, methods=["GET"])

    # --- Métodos de Controle (Handlers das Rotas) ---

    def mostrar_carrinho(self):
        return render_template(
            "cart.html", 
            frontend_carrinho=self.carrinho.itens, 
            frontend_total=self.carrinho.obter_total(),
            url_fronted_cart_chg_qtd=self.URL_CART_CALLER_CHG_QTD,
            url_fronted_cart_rem_item=self.URL_CART_CALLER_REM_ITEM,
            url_fronted_cart_flush=self.URL_CART_CALLER_FLSH,
            url_fronted_cart_checkout=self.URL_FRONTEND_CART_CHECKOUT,
            url_fronted_cart_go_to_gateway=self.URL_GATEWAY_LANDING,
            url_fronted_cart_go_to_catalog=self.URL_CATALOG_LANDING,
            url_fronted_cart_go_to_payment=self.URL_PAYMENT_LANDING
        )

    def retornar_carrinho(self):
        return jsonify(self.carrinho.itens)

    def adicionar_ao_carrinho(self):
        item_requisitado = request.json
        mensagem = self.carrinho.adicionar(item_requisitado)
        
        # Cria a mensagem temporária (categoria 'sucesso')
        flash(mensagem, "sucesso")
        return redirect(url_for("mostrar_carrinho"))

    def alterar_quantidade_no_carrinho(self):
        item_id = int(request.form.get("id"))
        quantidade = int(request.form.get("quantidade"))
        
        mensagem = self.carrinho.alterar_quantidade(item_id, quantidade)
        
        # Filtra se a mensagem foi de sucesso ou erro com base no retorno da classe
        categoria = "sucesso" if "alterada" in mensagem else "erro"
        flash(mensagem, categoria)
        
        return redirect(url_for("mostrar_carrinho"))

    def remover_do_carrinho(self):
        item_id = int(request.form.get("id"))
        mensagem = self.carrinho.remover(item_id)
        
        flash(mensagem, "sucesso")
        return redirect(url_for("mostrar_carrinho"))

    def esvaziar_carrinho(self):
        mensagem = self.carrinho.esvaziar()
        
        flash(mensagem, "sucesso")
        return redirect(url_for("mostrar_carrinho"))

    def iniciar(self, porta=5002):
        """Coloca o servidor em execução."""
        self.app.run(port=porta, debug=True)


# ==========================================
# 3. EXECUÇÃO DO MICROSSERVIÇO
# ==========================================
if __name__ == "__main__":
    servico = ServidorCarrinho()
    servico.iniciar(porta=5002)