from Edenred import db,bcrypt
from datetime import datetime, timezone, timedelta
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    telefone = db.Column(db.String(20), unique=True)
    skype = db.Column(db.String(100), unique=True)
    senha_hash = db.Column(db.String(200), nullable=False)
    
    def set_senha(self, senha):
        #Define a senha usando bcrypt
        self.senha_hash = bcrypt.generate_password_hash(senha.encode('utf-8'))
    
    def check_senha(self, senha):
        return bcrypt.check_password_hash(self.senha_hash, senha.encode('utf-8'))

class Empresa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cnpj = db.Column(db.String(20), unique=True, nullable=False)
    razao_social = db.Column(db.String(200), nullable=False)
    cep = db.Column(db.String(10))
    logradouro = db.Column(db.String(200))
    numero = db.Column(db.String(10))
    complemento = db.Column(db.String(100))
    bairro = db.Column(db.String(100))
    municipio = db.Column(db.String(100))
    estado = db.Column(db.String(2))
    
    nome_contato = db.Column(db.String(100))
    email_contato = db.Column(db.String(100))
    telefone_contato = db.Column(db.String(20))
    cargo_contato = db.Column(db.String(100))
    departamento_contato = db.Column(db.String(100))
    celular_contato = db.Column(db.String(20))
    
    eh_cliente = db.Column(db.Boolean, default=False)
    bus_contratados = db.Column(db.String(500)) 
    data_cadastro = db.Column(db.DateTime, default=datetime.now(timezone.utc))

class Indicacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresa.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    bu_indicado = db.Column(db.String(100), nullable=False)
    produtos_escolhidos = db.Column(db.String(500))
    
    #Depende do BU indicado. Exemplo: para Ticket Log.
    quantidade_caminhoes = db.Column(db.Integer)
    quantidade_funcionarios = db.Column(db.Integer)
    quantidade_veiculos_pesados = db.Column(db.Integer)
    subsidia_combustivel = db.Column(db.Boolean)
    quantidade_veiculos_leves = db.Column(db.Integer)
    quantidade_veiculos = db.Column(db.Integer)
    previsao_volume = db.Column(db.Float)
    quantidade_cartoes = db.Column(db.Integer)
    observacoes = db.Column(db.Text)
    
    status = db.Column(db.String(20), default='Pendente')  
    data_indicacao = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    
    empresa = db.relationship('Empresa', backref=db.backref('indicacoes', lazy=True))
    usuario = db.relationship('Usuario', backref=db.backref('indicacoes', lazy=True))
    
    def verificar_duplicidade(cnpj_empresa, produtos, periodo_meses=3):
        
        #Verifica se já existe indicação para o mesmo CNPJ e produtos dentro do período especificado
        
        # Calcula a data limite (Período considerado recente)
        data_limite = datetime.now(timezone.utc) - timedelta(days=periodo_meses*30)
        
        # Busca todas as indicações recentes para este CNPJ
        indicacoes_recentes = Indicacao.query.join(Empresa).filter(
            Empresa.cnpj == cnpj_empresa,
            Indicacao.data_indicacao >= data_limite
        ).all()
        
        # Verifica se algum produto já foi indicado
        produtos_duplicados = []
        for indicacao in indicacoes_recentes:
            for produto in produtos:
                if produto in indicacao.produtos_escolhidos:
                    produtos_duplicados.append(produto)
        
        return produtos_duplicados

