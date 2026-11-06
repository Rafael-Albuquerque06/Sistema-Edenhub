# 🏢 Edenhub - Sistema de Gestão Comercial

Sistema completo para gestão de cross-selling e comunicação interna, desenvolvido para otimizar processos comerciais e facilitar a colaboração entre equipes.

**Acesse online:** https://sistema-edenhub-rafael.onrender.com

## 🚀 Funcionalidades Principais

### 🤝 Gestão de Cross-Selling
- **Consulta e cadastro de empresas** por CNPJ
- **Seleção inteligente de BUs** (Business Units)
- **Catálogo dinâmico de produtos** por BU
- **Indicação e venda** com dados estruturados
- **Prevenção de duplicidades** automática

### 💬 Sistema de Comunicação
- **Chat interno em tempo real** (Flask-SocketIO) com indicador "digitando..." e status online/offline
- **Histórico completo** de conversas com contador de não lidas
- **Interface intuitiva** e responsiva

### 📊 Gestão de Dados
- **Consulta de clientes** com filtros
- **Dashboard com métricas reais** (indicações, pendências, clientes)
- **Portfólio de produtos** organizado

### 🔍 Validação e Integrações
- **Validação de CNPJ** com dígitos verificadores (antes do cadastro)
- **Prefill via ReceitaWS**: dados cadastrais preenchidos automaticamente por CNPJ (fallback manual)
- **Endereço via ViaCEP**: forma do CEP com máscara + preenchimento automático (fallback manual)
- **Máscaras de entrada** para CNPJ, telefone e CEP

## 🛠️ Tecnologias Utilizadas

- **Backend:** Python + Flask + Flask-SocketIO (chat em tempo real)
- **Frontend:** HTML5 + Bootstrap 5 + JavaScript (máscaras e validação client-side)
- **Banco de Dados:** SQLAlchemy + SQLite (PostgreSQL em produção)
- **Autenticação:** Flask-Login + Bcrypt
- **Forms:** Flask-WTF + WTForms
- **Migrações:** Flask-Migrate (Alembic)
- **Testes:** pytest

## 📋 Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes do Python)
- Git

## 🚀 Instalação e Configuração

### 1. Clone o repositório

```bash
git clone https://github.com/Rafael-Albuquerque06/Sistema-Edenhub.git
cd Sistema-Edenhub
```

### 2. Crie um ambiente virtual

**Usando venv:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Ou usando uv (recomendado):**
```bash
uv venv
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto com base no `.env.example`:

```bash
cp .env.example .env
```

Edite o `.env` com seus valores:

```env
SECRET_KEY=sua_chave_secreta_muito_segura_aqui
DATABASE_URI=sqlite:///edenred.db
```

### 5. Inicialize o banco de dados

```bash
flask db upgrade
```

### 6. Execute o Sistema

```bash
python main.py
```

Acesse: `http://localhost:5000`

## 🧪 Executando os Testes

```bash
pip install pytest
python3 -m pytest tests/ -v
```

## 🐳 Usando Docker (opcional)

```bash
docker build -t edenhub .
docker run -p 5000:5000 edenhub
```

## 📁 Estrutura do Projeto

```
edenhub/
├── app/
│   ├── __init__.py          # Application factory (cria app + SocketIO por instância)
│   ├── config.py            # Config por ambiente (development/production/testing)
│   ├── models.py            # Modelos (N:N: BusinessUnit, Produto + associações)
│   ├── services.py          # Lógica de negócio (usuários, empresas, chat, métricas)
│   ├── routes.py            # Rotas (apenas request/response)
│   ├── forms.py             # Formulários e validações
│   ├── utils.py             # Helpers puros: CNPJ (validar/formatar), máscaras, datas
│   ├── api_client.py        # Integrações externas: ViaCEP e ReceitaWS (fallback manual)
│   ├── events.py            # Eventos SocketIO do chat (mensagens, digitando, presença)
│   ├── presence.py          # Presença online/offline em memória (threading)
│   ├── static/
│   │   ├── css/style.css    # Design system
│   │   ├── js/app.js        # Máscaras, ViaCEP, toasts e feedback de envio
│   │   ├── js/script.js     # Catálogo dinâmico de produtos no cross-selling
│   │   ├── data/            # Uploads
│   │   └── img/             # Imagens
│   └── templates/           # Templates HTML
├── migrations/              # Migrações Alembic
├── tests/                   # Testes pytest (modelos, rotas, serviços, APIs, chat)
├── main.py                  # Servidor de desenvolvimento (socketio.run)
├── wsgi.py                  # Entry point para gunicorn
├── sk_create.py             # Gerador de chave secreta
├── requirements.txt         # Dependências
├── .env.example             # Exemplo de variáveis de ambiente
├── .gitignore               # Arquivos ignorados
└── README.md
```

## 🚀 Deploy (gunicorn)

O chat em tempo real exige um único processo do gunicorn:

```bash
gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --worker-class gthread wsgi:app
```

No Render (render.yaml): `flask db upgrade` roda antes do start, e a `DATABASE_URI` não vem versionada (configure no dashboard).

## 🔒 Segurança

- ✅ Senhas criptografadas com Bcrypt
- ✅ Proteção contra CSRF (Flask-WTF)
- ✅ Sessões seguras com Flask-Login
- ✅ Validação de dados em backend e frontend
- ✅ Autenticação requerida para rotas sensíveis
- ✅ Paginação de flash messages por categoria


## 👨‍💻 Autor

Developed by Rafael Albuquerque for Edenred Challenge.
