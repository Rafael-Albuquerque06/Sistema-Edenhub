# 🏢 EdenHub - Sistema de Gestão Comercial

Sistema completo para gestão de cross-selling e comunicação interna, desenvolvido para otimizar processos comerciais e facilitar a colaboração entre equipes.

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
- **Mensagens em tempo real**

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

## 📋 Pré-requisitos

Antes de começar, certifique-se de ter instalado:

- Python 3.8 ou superior
- pip (gerenciador de pacotes do Python)
- Git

## 🚀 Instalação e Configuração

### 1. Clone o repositório

```bash
git clone https://github.com/Rafael-Albuquerque06/Sistema-Edenhub.git
cd Sistema-Edenhub
```

### 2. Crie um ambiente virtual (recomendado)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
# Chave secreta para segurança das sessões
SECRET_KEY=sua_chave_secreta_muito_segura_aqui

# Configuração do banco de dados (SQLite para desenvolvimento)
DATABASE_URI=sqlite:///edenred.db

```

**💡 Dica:** Para gerar uma chave secreta segura, execute:
```bash
python sk_create.py
```

### 5. Inicialize o banco de dados

```bash
# Execute o arquivo principal para criar as tabelas
python main.py
```

**Ou usando Flask-Migrate:**
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

## 🎯 Executando o Sistema

### Opção 1: Execução direta
```bash
python main.py
```

### Opção 2: Usando Flask
```bash
flask run
```

### Opção 3: Modo desenvolvimento
```bash
flask run --debug
```

Após executar, acesse no navegador:
```
http://localhost:5000
```

## 👤 Primeiro Acesso

1. **Acesse a página de cadastro:**
   ```
   http://localhost:5000/cadastro
   ```

2. **Crie seu usuário:**
   - Preencha todos os campos obrigatórios
   - Use um email válido
   - Senha mínima de 6 caracteres

3. **Faça login:**
   ```
   http://localhost:5000/login
   ```
   - Use email, telefone ou Skype para login

## 📁 Estrutura do Projeto

```
edenhub/
├── Edenred/
│   ├── __init__.py          # Configuração do Flask
│   ├── models.py            # Modelos do banco de dados
│   ├── views.py             # Rotas e lógica da aplicação
│   ├── forms.py             # Formulários e validações
│   └── templates/           # Templates HTML
│       ├── base.html        # Template base
│       ├── home.html        # Página inicial
│       ├── login.html       # Página de login
│       ├── cadastro.html    # Página de cadastro
│       ├── crosselling.html # Gestão de cross-selling
│       ├── comunicacao.html # Sistema de chat
│       └── ...
├── static/
│   ├── css/                 # Estilos CSS
│   ├── js/                  # JavaScript
│   └── data/                # Uploads e arquivos
├── requirements.txt         # Dependências do projeto
├── main.py                 # Arquivo principal
├── sk_create.py            # Gerador de chave secreta
└── .gitignore              # Arquivos ignorados pelo Git
```

## 🐛 Solução de Problemas Comuns

### Erro: "ModuleNotFoundError"
```bash
# Reinstale as dependências
pip install -r requirements.txt
```

### Erro: "Address already in use"
```bash
# Use uma porta diferente
flask run --port 5001
```

### Erro de banco de dados
```bash
# Recrie as tabelas
python main.py
# Ou
flask db upgrade
```

### Problemas com ambiente virtual
```bash
# Desative e reative o ambiente
deactivate
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

## 📝 Comandos Úteis

### Desenvolvimento
```bash
# Executar em modo debug
flask run --debug

# Ver rotas disponíveis
flask routes

# Executar testes (se houver)
python -m pytest
```

### Banco de Dados
```bash
# Criar nova migração
flask db migrate -m "descricao_da_mudanca"

# Aplicar migrações
flask db upgrade

# Reverter migração
flask db downgrade
```

### Administração
```bash
# Acessar shell do Flask
flask shell

# Verificar dependências
pip list
```

## 🔒 Segurança

- ✅ Senhas criptografadas com Bcrypt
- ✅ Proteção contra CSRF
- ✅ Sessões seguras
- ✅ Validação de dados em backend e frontend
- ✅ Autenticação requerida para rotas sensíveis


## 📞 Suporte

Encontrou problemas? 

1. Verifique a seção "Solução de Problemas Comuns"
2. Confirme que todas as dependências estão instaladas
3. Certifique-se de que o banco de dados foi inicializado
4. Verifique os logs do servidor para mensagens de erro


**🎉 Pronto! Seu sistema EdenHub está rodando localmente!**

Acesse `http://localhost:5000` e comece a explorar as funcionalidades. Para qualquer dúvida, consulte a documentação acima ou entre em contato comigo rafaalbuquerque1279@gmail.com.

Developed by Rafael Albuquerque.
