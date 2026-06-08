# Framework de Microsserviços para E-commerce

Projeto acadêmico desenvolvido para a disciplina **Reuso de Software e Metodologias Ágeis – UFAL**.

Implementa um **framework reutilizável de microsserviços** baseado no padrão de projeto **Template Method**, demonstrando técnicas de reuso de software por meio de duas aplicações independentes construídas sobre a mesma base.

---

## Visão Geral da Arquitetura

O núcleo do framework é a classe abstrata `MicroserviceBase` (`shared/base_microservico.py`), que define a sequência fixa de inicialização de qualquer microsserviço Flask — criação da app, CORS, health-check — como **frozen spots**, enquanto delega os pontos de variação do negócio às subclasses por meio de **hotspots**:

| Método | Tipo | Descrição |
|---|---|---|
| `inicializar()` | Template Method (frozen) | Sequência fixa de inicialização |
| `_criar_flask_app()` | Frozen spot | Instancia o objeto Flask |
| `_configurar_cors()` | Frozen spot | Habilita CORS |
| `_registrar_health()` | Frozen spot | Registra `GET /health` |
| `_registrar_rotas()` | **Hotspot obrigatório** | Subclasse define as rotas do domínio |
| `_configurar_extras()` | **Hotspot opcional** | Extensões, banco de dados, etc. |

### Aplicações desenvolvidas

| Aplicação | Descrição | Portas |
|---|---|---|
| **E-commerce** (Loja Didática) | Vende produtos eletrônicos | 5000 – 5003 |
| **Livraria Didática** | Vende livros técnicos | 5010 – 5013 |

Ambas reutilizam o mesmo `MicroserviceBase` sem alterar uma linha do framework; apenas os hotspots são adaptados para cada domínio.

---

## Estrutura do Projeto

```
.
├── shared/
│   ├── base_microservico.py   # Framework: classe abstrata MicroserviceBase
│   └── factory.py             # Utilitário: fábrica Flask com CORS
│
├── catalogo/                  # E-commerce: microsserviço catálogo (:5001)
│   ├── app.py                 # CatalogoService — hotspot: GET /produtos
│   └── dados.py               # Lista de produtos eletrônicos
├── carrinho/                  # E-commerce: microsserviço carrinho (:5002)
│   └── app.py                 # CarrinhoService — hotspot: GET/POST /carrinho
├── pagamento/                 # E-commerce: microsserviço pagamento (:5003)
│   └── app.py                 # PagamentoService — hotspot: POST /pagamento
├── gateway/                   # E-commerce: API Gateway + interface web (:5000)
│   ├── app.py
│   └── templates/
│       ├── index.html         # Tela principal (catálogo + carrinho)
│       └── pagamento.html     # Confirmação de pagamento
│
└── livraria/                  # Aplicação 2 — reuso do framework
    ├── catalogo/              # Catálogo de livros (:5011)
    │   ├── app.py             # CatalogoLivrariaService — hotspot: GET /livros
    │   └── dados.py           # Lista de livros com autor, gênero, capa, etc.
    ├── carrinho/              # Carrinho de livros (:5012)
    │   └── app.py             # CarrinhoLivrariaService — GET/POST/DELETE /carrinho
    ├── pagamento/             # Pagamento de livros (:5013)
    │   └── app.py             # PagamentoLivrariaService — POST /pagamento
    └── gateway/               # API Gateway Livraria + interface web (:5010)
        ├── app.py
        └── templates/
            ├── index.html
            └── pagamento.html
```

---

## Pré-requisitos

- Python 3.10+
- pip

---

## Instalação

```bash
pip install -r requirements.txt
```

---

## Executando as Aplicações

Execute todos os comandos a partir da **raiz do projeto**.

### Aplicação 1 — E-commerce (http://localhost:5000)

```bash
# Terminal 1
python catalogo/app.py

# Terminal 2
python carrinho/app.py

# Terminal 3
python pagamento/app.py

# Terminal 4
python gateway/app.py
```

### Aplicação 2 — Livraria (http://localhost:5010)

```bash
# Terminal 1
python livraria/catalogo/app.py

# Terminal 2
python livraria/carrinho/app.py

# Terminal 3
python livraria/pagamento/app.py

# Terminal 4
python livraria/gateway/app.py
```

As duas aplicações usam portas distintas e podem rodar simultaneamente.

### Health-check dos microsserviços

| Serviço | URL |
|---|---|
| Catálogo E-commerce | http://localhost:5001/health |
| Carrinho E-commerce | http://localhost:5002/health |
| Pagamento E-commerce | http://localhost:5003/health |
| Catálogo Livraria | http://localhost:5011/health |
| Carrinho Livraria | http://localhost:5012/health |
| Pagamento Livraria | http://localhost:5013/health |

---

## Variáveis de Ambiente

As URLs dos microsserviços podem ser sobrescritas sem alterar o código:

```bash
# E-commerce
CATALOGO_URL=http://localhost:5001  python gateway/app.py
CARRINHO_URL=http://localhost:5002  python gateway/app.py
PAGAMENTO_URL=http://localhost:5003 python gateway/app.py

# Livraria (prefixo LIV_ evita conflito ao rodar as duas apps juntas)
LIV_CATALOGO_URL=http://localhost:5011  python livraria/gateway/app.py
LIV_CARRINHO_URL=http://localhost:5012  python livraria/gateway/app.py
LIV_PAGAMENTO_URL=http://localhost:5013 python livraria/gateway/app.py
```

---

## Criando uma Nova Aplicação com o Framework

Basta herdar `MicroserviceBase` e implementar o hotspot obrigatório:

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from flask import jsonify
from shared.base_microservico import MicroserviceBase

MEUS_ITENS = [
    {"id": 1, "nome": "Item A", "preco": 50.00},
]

class MeuCatalogoService(MicroserviceBase):
    def _registrar_rotas(self) -> None:
        @self.app.route("/itens")
        def listar():
            return jsonify(MEUS_ITENS)

if __name__ == "__main__":
    servico = MeuCatalogoService(__name__, porta=5021)
    servico.executar()
```

O framework injeta automaticamente CORS, `GET /health` e toda a configuração Flask — sem nenhuma linha extra.

---

## Tecnologias

| Tecnologia | Versão | Uso |
|---|---|---|
| Python | 3.10+ | Linguagem principal |
| Flask | 3.x | Framework web dos microsserviços |
| Flask-CORS | 4.x | CORS entre serviços |
| Requests | 2.x | Comunicação HTTP entre gateway e microsserviços |
| Bootstrap | 5.3 | Interface web |
| Bootstrap Icons | 1.11 | Ícones da interface da Livraria |

---

## Disciplina

Reuso de Software e Metodologias Ágeis — Universidade Federal de Alagoas (UFAL)
