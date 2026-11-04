from app import db, bcrypt
from datetime import datetime, timezone, timedelta
from flask_login import UserMixin


class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuario'

    id = db.Column(db.Integer, primary_key=True)
    foto = db.Column(db.String, nullable=True, default='default.png')
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    telefone = db.Column(db.String(20), unique=True)
    skype = db.Column(db.String(100), unique=True, nullable=True)
    senha_hash = db.Column(db.String(200), nullable=False)

    def set_senha(self, senha):
        """Define a senha usando bcrypt para criptografar."""
        self.senha_hash = bcrypt.generate_password_hash(senha.encode('utf-8'))

    def check_senha(self, senha):
        return bcrypt.check_password_hash(self.senha_hash, senha.encode('utf-8'))


class Empresa(db.Model):
    __tablename__ = 'empresa'

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

    responsavel_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=True)
    is_client = db.Column('eh_cliente', db.Boolean, default=False)
    contracted_business_units = db.Column('bus_contratados', db.String(500))
    data_cadastro = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    responsavel = db.relationship('Usuario', backref=db.backref('empresas_responsavel', lazy=True))

    @property
    def bus_list(self):
        """Retorna a lista de BUs contratados como lista de strings."""
        if not self.contracted_business_units:
            return []
        return [bu.strip() for bu in self.contracted_business_units.split(',') if bu.strip()]


class Indicacao(db.Model):
    __tablename__ = 'indicacao'

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresa.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    bu_indicado = db.Column(db.String(100), nullable=False)
    produtos_escolhidos = db.Column(db.String(500))

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


class Conversa(db.Model):
    __tablename__ = 'conversa'

    id = db.Column(db.Integer, primary_key=True)
    usuario1_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    usuario2_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    usuario1 = db.relationship('Usuario', foreign_keys=[usuario1_id], backref=db.backref('conversas_iniciadas', lazy=True))
    usuario2 = db.relationship('Usuario', foreign_keys=[usuario2_id], backref=db.backref('conversas_recebidas', lazy=True))


class Mensagem(db.Model):
    __tablename__ = 'mensagem'

    id = db.Column(db.Integer, primary_key=True)
    conversa_id = db.Column(db.Integer, db.ForeignKey('conversa.id'), nullable=False)
    remetente_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    mensagem = db.Column(db.Text, nullable=False)
    data_envio = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    lida = db.Column(db.Boolean, default=False)

    conversa = db.relationship('Conversa', backref=db.backref('mensagens', lazy=True))
    remetente = db.relationship('Usuario', backref=db.backref('mensagens_enviadas', lazy=True))
