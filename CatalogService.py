from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Lista de produtos simulada
produtos = [
    {"id": 1, "nome": "Notebook", "preco": 3500},
    {"id": 2, "nome": "Smartphone", "preco": 1800},
    {"id": 3, "nome": "Fone de ouvido", "preco": 250}
]

@app.route("/produtos")
def listar_produtos():
    return jsonify(produtos)

if __name__ == "__main__":
    app.run(port=5001)