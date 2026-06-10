# Framework de Microsserviços para E-commerce

Disciplina **ECOM189 – Reuso de Software e Metodologias Ágeis** · UFAL 2026-1

---

## Visão Geral

Este projeto implementa um **framework orientado a objetos** para construção de microsserviços Flask, demonstrando os conceitos de reuso de software através de dois domínios distintos:

| Aplicação | Domínio | Portas |
|-----------|---------|--------|
| E-commerce | Catálogo de eletrônicos, carrinho e pagamento | 5000, 5001 |
| Livraria | Catálogo de livros, carrinho e pagamento | 5010, 5011 |
| **Platform Services** | Carrinho, Pagamento e Pedidos **compartilhados** | 5002, 5003, 5004 |

Ambas as aplicações são construídas **sem duplicar código de infraestrutura**, reutilizando o framework definido em `shared/`. Os serviços de plataforma (5002–5004) são compartilhados pelos dois domínios via namespace e configuração por dados.

---

## Arquitetura do Framework

### Padrão de Projeto: Template Method

O núcleo do framework é a classe abstrata `MicroserviceBase` (`shared/base_microservico.py`), que implementa o padrão **Template Method** (Gamma et al., 1994).

O método `inicializar()` define a **sequência fixa** de montagem de qualquer microsserviço:

```
inicializar()
 ├─ _criar_flask_app()    ← Frozen Spot
 ├─ _configurar_cors()    ← Frozen Spot
 ├─ _registrar_health()   ← Frozen Spot
 ├─ _registrar_rotas()    ← Hotspot OBRIGATÓRIO (abstract)
 └─ _configurar_extras()  ← Hotspot OPCIONAL (hook vazio)
```

### Frozen Spots vs. Hotspots

Segundo **Fayad & Schmidt (1997)**, um framework OO é composto por:
- **Frozen spots**: partes fixas que implementam funcionalidades comuns a todas as aplicações.
- **Hotspots**: pontos de variação onde cada aplicação implementa seu comportamento específico.

| Método | Tipo | Responsabilidade |
|--------|------|-----------------|
| `_criar_flask_app()` | Frozen Spot | Instancia o objeto Flask com o nome do serviço |
| `_configurar_cors()` | Frozen Spot | Habilita CORS para comunicação entre origens |
| `_registrar_health()` | Frozen Spot | Registra `GET /health` padrão de monitoramento |
| `_registrar_rotas()` | **Hotspot obrigatório** | Cada serviço define suas rotas de negócio |
| `_configurar_extras()` | **Hotspot opcional** | Subclasses adicionam logging, persistência, etc. |

### Componentes Compartilhados

```
shared/
├── base_microservico.py  ← Classe abstrata MicroserviceBase (Template Method)
├── repositorio.py        ← BaseRepository (ABC), MemoryRepository, JsonRepository
└── factory.py            ← Função criar_app() usada pelos API Gateways
```

`repositorio.py` implementa o padrão **Repository + Strategy**: `BaseRepository` define a interface ABC; `MemoryRepository` e `JsonRepository` são estratégias intercambiáveis.

`factory.py` é utilizado pelos API Gateways, que orquestram serviços mas não são microsserviços de negócio — portanto não precisam do Template Method completo, apenas da criação Flask+CORS.

---

## Platform Services — Serviços Compartilhados

Em vez de duplicar Carrinho e Pagamento para cada domínio, o projeto utiliza **Platform Services**: serviços únicos que atendem múltiplas aplicações com isolamento por namespace/configuração.

### Carrinho Compartilhado (porta 5002)

Mantém um `MemoryRepository` **por namespace**, isolando o estado de cada domínio:

```
GET  /carrinho?ns=ecommerce   → carrinho da Loja Didática
GET  /carrinho?ns=livraria    → carrinho da Livraria
POST /carrinho?ns=ecommerce   → adiciona produto (Loja)
POST /carrinho?ns=livraria    → adiciona livro (Livraria)
```

Demonstra o **hotspot opcional** `_configurar_extras()` com logging estruturado por namespace.

### Pagamento Compartilhado (porta 5003)

Mensagem de confirmação configurada por **dados** (dicionário `_MENSAGENS`), sem subclasses:

```python
_MENSAGENS = {
    "ecommerce": "Pagamento de R${total:.2f} realizado com sucesso!",
    "livraria":  "Compra de livros no valor de R${total:.2f} confirmada! Bons estudos!",
}
```

### Pedidos (porta 5004)

Registra o histórico de compras de todas as aplicações usando `JsonRepository` para persistência real (sobrevive a reinicializações). Demonstra `_configurar_extras()` como ponto de escolha da estratégia de persistência.

```
POST /pedidos               → cria pedido {total, dominio, itens}
GET  /pedidos               → lista todos os pedidos
GET  /pedidos?dominio=liv.. → filtra por domínio
GET  /pedidos/<id>          → detalha um pedido
```

---

## Duas Aplicações, Um Framework

### O que foi 100% reutilizado (Frozen Spots)

| Funcionalidade | Onde está | Reutilizado por |
|----------------|-----------|-----------------|
| Inicialização Flask | `_criar_flask_app()` | 7 microsserviços |
| Configuração CORS | `_configurar_cors()` | 7 microsserviços + 2 gateways |
| Endpoint `/health` | `_registrar_health()` | 7 microsserviços |
| Método `executar()` | `MicroserviceBase.executar()` | 7 microsserviços |
| Criação Flask+CORS | `criar_app()` em `factory.py` | 2 API Gateways |
| Interface Repository | `BaseRepository(ABC)` | CarrinhoCompartilhado + PedidoService |

### O que variou por domínio (Hotspots)

| Serviço | `_registrar_rotas()` | `_configurar_extras()` |
|---------|----------------------|------------------------|
| `CatalogoService` | `GET /produtos` → eletrônicos | — |
| `CatalogoLivrariaService` | `GET /livros` → livros | — |
| `CarrinhoCompartilhado` | `GET/POST/DELETE /carrinho` + namespace | **Logging por namespace** |
| `PagamentoCompartilhado` | `POST /pagamento` → mensagem por domínio | — |
| `PedidoService` | `POST/GET /pedidos` com filtro por domínio | **Instancia JsonRepository** |

---

## Estrutura do Projeto

```
projeto_reuso/
├── shared/                          ← Framework reutilizável
│   ├── base_microservico.py         ← MicroserviceBase (Template Method)
│   ├── repositorio.py               ← BaseRepository, MemoryRepository, JsonRepository
│   └── factory.py                   ← Fábrica Flask+CORS para gateways
│
├── carrinho/                        ┐
│   └── app.py   (porta 5002)        │ Platform Services
├── pagamento/                       │ compartilhados
│   └── app.py   (porta 5003)        │ entre todas as
├── pedido/                          │ aplicações
│   └── app.py   (porta 5004)        ┘
│
├── catalogo/                        ┐
│   ├── app.py   (porta 5001)        │ Aplicação 1
│   └── dados.py                     │ E-commerce
├── gateway/                         │
│   ├── app.py   (porta 5000)        │
│   └── templates/                   ┘
│
├── livraria/                        ┐
│   ├── catalogo/                    │ Aplicação 2
│   │   ├── app.py   (porta 5011)    │ Livraria
│   │   └── dados.py                 │
│   ├── carrinho/  [DEPRECADO]       │ (substituído por :5002)
│   ├── pagamento/ [DEPRECADO]       │ (substituído por :5003)
│   └── gateway/                     │
│       ├── app.py   (porta 5010)    │
│       └── templates/               ┘
│
├── dados/                           ← Gerado em runtime
│   └── pedidos.json                 ← Persistência do PedidoService
│
├── Como executar.txt
├── README.md
└── requirements.txt
```

---

## Como Executar

### Pré-requisito

```bash
pip install -r requirements.txt
```

Execute todos os comandos a partir da **raiz do projeto** (`projeto_reuso/`).

### Ambas as aplicações simultaneamente (7 terminais)

```bash
# Serviços compartilhados (obrigatórios para ambas as apps)
python -m carrinho.app           # Terminal 1 → :5002
python -m pagamento.app          # Terminal 2 → :5003
python -m pedido.app             # Terminal 3 → :5004

# E-commerce
python -m catalogo.app           # Terminal 4 → :5001
python -m gateway.app            # Terminal 5 → :5000  http://localhost:5000

# Livraria
python -m livraria.catalogo.app  # Terminal 6 → :5011
python -m livraria.gateway.app   # Terminal 7 → :5010  http://localhost:5010
```

### Aplicação 1 – E-commerce isolada (5 terminais)

```bash
python -m carrinho.app     # :5002
python -m pagamento.app    # :5003
python -m pedido.app       # :5004
python -m catalogo.app     # :5001
python -m gateway.app      # :5000 → http://localhost:5000
```

### Aplicação 2 – Livraria isolada (5 terminais)

```bash
python -m carrinho.app              # :5002
python -m pagamento.app             # :5003
python -m pedido.app                # :5004
python -m livraria.catalogo.app     # :5011
python -m livraria.gateway.app      # :5010 → http://localhost:5010
```

### Health Checks

| Serviço | URL |
|---------|-----|
| Carrinho Compartilhado | http://localhost:5002/health |
| Pagamento Compartilhado | http://localhost:5003/health |
| Pedidos | http://localhost:5004/health |
| Catálogo E-commerce | http://localhost:5001/health |
| Catálogo Livraria | http://localhost:5011/health |

### Inspecionar pedidos

```bash
# Todos os pedidos (ambos os domínios)
curl http://localhost:5004/pedidos

# Filtrar por domínio
curl "http://localhost:5004/pedidos?dominio=ecommerce"
curl "http://localhost:5004/pedidos?dominio=livraria"
```

---

## Referências

1. **Fayad, M. E.; Schmidt, D. C.** Object-Oriented Application Frameworks. *Communications of the ACM*, v. 40, n. 10, 1997. — Base teórica de frozen spots e hotspots.
2. **Gamma, E.; Helm, R.; Johnson, R.; Vlissides, J.** *Design Patterns*. Addison-Wesley, 1994. — Padrão Template Method.
3. **Fowler, M.; Lewis, J.** Microservices. 2014. — Arquitetura de microsserviços.
4. **Azevedo, L. G.** Desenvolvimento de Soluções com Serviços: SOA, Cloud e Microsserviços. SBSI 2020.
5. **Sommerville, I.** *Engenharia de Software*. Pearson, 10ª ed., 2018.
