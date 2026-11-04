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
- **Chat interno** entre usuários
- **Histórico completo** de conversas
- **Interface intuitiva** e responsiva

### 📊 Gestão de Dados
- **Consulta de clientes** com filtros
- **Dashboard de pendências**
- **Portfólio de produtos** organizado

## 🛠️ Tecnologias Utilizadas

- **Backend:** Python + Flask
- **Frontend:** HTML5 + Bootstrap 5 + JavaScript
- **Banco de Dados:** SQLAlchemy + SQLite
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
│   ├── __init__.py          # Application factory
│   ├── models.py            # Modelos do banco de dados
│   ├── services.py          # Lógica de negócio
│   ├── forms.py             # Formulários e validações
│   ├── routes.py            # Rotas da aplicação
│   ├── static/
│   │   ├── css/style.css    # Design system
│   │   ├── js/script.js     # Interatividade
│   │   ├── data/            # Uploads
│   │   └── img/             # Imagens
│   └── templates/           # Templates HTML
├── migrations/              # Migrações Alembic
├── tests/                   # Testes pytest
├── main.py                  # Arquivo principal
├── wsgi.py                  # Entry point para WSGI
├── sk_create.py             # Gerador de chave secreta
├── requirements.txt         # Dependências
├── .env.example             # Exemplo de variáveis de ambiente
├── .gitignore               # Arquivos ignorados
└── README.md
```

## 🔒 Segurança

- ✅ Senhas criptografadas com Bcrypt
- ✅ Proteção contra CSRF (Flask-WTF)
- ✅ Sessões seguras com Flask-Login
- ✅ Validação de dados em backend e frontend
- ✅ Autenticação requerida para rotas sensíveis
- ✅ Paginação de flash messages por categoria


## 👨‍💻 Autor

Developed by Rafael Albuquerque for Edenred Challenge.
