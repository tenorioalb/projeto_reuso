import qrcode
from IPython.display import display
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/pagamento", methods=["POST"])
def realizar_pagamento():
    dados = request.json
    total = dados.get("total", 0)

    qr = qrcode.QRCode(version=1, box_size=8, border=4)
    qr.add_data(total)
    qr.make(fit=True)
    imagem_qr = qr.make_image(fill_color="black", back_color="white")
    display(imagem_qr)
    return jsonify({"mensagem": f"Pagamento de R${total:.2f} realizado com sucesso!"})

if __name__ == "__main__":
    app.run(port=5003)