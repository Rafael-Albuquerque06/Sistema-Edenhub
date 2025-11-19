from Edenred import db
from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    telefone = db.Column(db.String(20))
    skype = db.Column(db.String(100))
    senha_hash = db.Column(db.String(200), nullable=False)
    
    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)
    
    def check_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)

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

