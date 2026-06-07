import io
import base64
import random
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_cors import CORS
import qrcode # Garanta que tem instalado: pip install qrcode pillow

# ==========================================
# 1. MODELO DE NEGÓCIO: PROCESSADOR DE PAGAMENTO
# ==========================================
class ProcessadorPagamento:
    def __init__(self):
        self.historico_transacoes = []

    def gerar_qr_code_base64(self, valor: float) -> str:
        """Sua função genQR adaptada para retornar Base64 limpo para o Jinja2."""
        pix_key = "http://localhost:5000/gateway-pagamento-ficticio"
        dados_pix = f"VALOR:{valor:.2f}|CHAVE:{pix_key}"
        
        qr = qrcode.QRCode(version=1, box_size=6, border=2)
        qr.add_data(dados_pix)
        qr.make(fit=True)
        
        imagem_qr = qr.make_image(fill_color="black", back_color="white")
        
        # Salva a imagem em um buffer de memória em vez de criar um arquivo no disco
        buffer = io.BytesIO()
        imagem_qr.save(buffer, format="PNG")
        qrcode_bytes = buffer.getvalue()
        
        # Converte para string Base64 que qualquer tag <img> lê nativamente
        qrcode_base64 = base64.b64encode(qrcode_bytes).decode('utf-8')
        return f"data:image/png;base64,{qrcode_base64}"

    def gerar_codigo_barras_ficticio(self) -> str:
        """Gera uma sequência numérica fictícia simulando um boleto bancário."""
        bloco1 = f"34191.{random.randint(10000, 99999)}"
        bloco2 = f"{random.randint(10000, 99999)}.{random.randint(10000, 99999)}"
        bloco3 = f"{random.randint(10000, 99999)}.{random.randint(10000, 99999)}"
        bloco4 = f"{random.randint(1, 9)}"
        bloco5 = f"{random.randint(10000000000000, 99999999999999)}"
        return f"{bloco1} {bloco2} {bloco3} {bloco4} {bloco5}"

    def processar_transacao(self, valor: float, metodo: str, dados_extras: dict = None) -> dict:
        """Processa e valida as regras de negócio."""
        if valor <= 0:
            return {"sucesso": False, "mensagem": "Valor inválido para pagamento."}
        
        # Validação específica se for cartão
        if metodo == "Cartão de Crédito" and dados_extras:
            num_cartao = dados_extras.get("numero_cartao", "").replace(" ", "")
            if len(num_cartao) < 16:
                return {"sucesso": False, "mensagem": "Pagamento recusado: Número do cartão inválido."}

        transacao = {
            "id": len(self.historico_transacoes) + 1,
            "valor": valor,
            "metodo": metodo,
            "status": "Aprovado"
        }
        self.historico_transacoes.append(transacao)
        return {"sucesso": True, "mensagem": f"Pagamento de R$ {valor:.2f} processado via {metodo}!"}


# ==========================================
# 2. SERVIDOR DO MICROSSERVIÇO DE PAGAMENTO
# ==========================================
class ServidorPagamento:
    URL_GATEWAY_LANDING = "http://localhost:5000/"
    URL_CATALOG_LANDING = "http://localhost:5001/"
    URL_CART_LANDING = "http://localhost:5002/carrinho"

    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)
        self.app.secret_key = "chave_secreta_do_modulo_de_pagamentos"
        self.processador = ProcessadorPagamento()
        self._registrar_rotas()

    def _registrar_rotas(self):
        self.app.add_url_rule("/pagar", "iniciar_pagamento", self.iniciar_pagamento, methods=["POST"])
        self.app.add_url_rule("/confirmar", "confirmar_pagamento", self.confirmar_pagamento, methods=["POST"])

    def iniciar_pagamento(self):
        custo_total_raw = request.form.get("custo_total")
        if not custo_total_raw:
            return "Erro: Custo total não informado.", 400
            
        try:
            custo_total = float(custo_total_raw)
        except ValueError:
            return "Erro: Formato de valor inválido.", 400

        # Pré-gera os dados fictícios dinamicamente para passar à tela
        qr_code_src = self.processador.gerar_qr_code_base64(custo_total)
        codigo_barras = self.processador.gerar_codigo_barras_ficticio()

        return render_template("checkout.html", 
                               total_pagamento=custo_total,
                               qr_code_img=qr_code_src,
                               boleto_linha=codigo_barras,
                               url_retornar_carrinho=self.URL_CART_LANDING)

    def confirmar_pagamento(self):
        valor = float(request.form.get("valor_final"))
        metodo = request.form.get("metodo_pagamento")
        
        dados_cartao = {
            "numero_cartao": request.form.get("numero_cartao"),
            "nome_titular": request.form.get("nome_titular")
        }

        resultado = self.processador.processar_transacao(valor, metodo, dados_cartao)

        if resultado["sucesso"]:
            # CASO DE SUCESSO: Renderiza uma tela intermediária com a mensagem e a URL de destino
            return render_template("checkout-success.html", 
                                   mensagem_sucesso=resultado["mensagem"],
                                   url_destino=self.URL_GATEWAY_LANDING+"pagamento/confirmado")
        else:
            # CASO DE ERRO: Permanece no checkout (Mantido)
            flash(resultado["mensagem"], "erro")
            qr_code_src = self.processador.gerar_qr_code_base64(valor)
            codigo_barras = self.processador.gerar_codigo_barras_ficticio()
            
            return render_template("checkout.html", 
                                   total_pagamento=valor,
                                   qr_code_img=qr_code_src,
                                   boleto_linha=codigo_barras,
                                   url_retornar_carrinho=self.URL_CART_LANDING)

    def iniciar(self, porta=5003):
        self.app.run(port=porta, debug=True)

if __name__ == "__main__":
    servico_pagamento = ServidorPagamento()
    servico_pagamento.iniciar(porta=5003)