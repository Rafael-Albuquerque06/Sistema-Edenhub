from app import db, bcrypt
from datetime import datetime, timezone
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
        """Define a senha usando bcrypt para criptografar.

        generate_password_hash pode retornar bytes; em Postgres os bytes
        viram um dump hex (`\\x...`) no varchar e o login falha com
        "Invalid salt". Sempre convertemos para str.
        """
        hash_gerado = bcrypt.generate_password_hash(senha.encode('utf-8'))
        if isinstance(hash_gerado, bytes):
            hash_gerado = hash_gerado.decode('ascii')
        self.senha_hash = hash_gerado

    def check_senha(self, senha):
        try:
            return bcrypt.check_password_hash(self.senha_hash, senha.encode('utf-8'))
        except (ValueError, TypeError):
            # Hash legado/corrompido: trata como senha incorreta (sem 500)
            return False



class BusinessUnit(db.Model):
    """BU (Business Unit) do catálogo Edenred."""
    __tablename__ = 'business_unit'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)



class Produto(db.Model):
    """Produto comercializável, vinculado a BUs nas indicações."""
    __tablename__ = 'produto'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)



empresa_bus = db.Table(
    'empresa_bus',
    db.Column('empresa_id', db.Integer, db.ForeignKey('empresa.id'), primary_key=True),
    db.Column('business_unit_id', db.Integer, db.ForeignKey('business_unit.id'), primary_key=True),
)

indicacao_produtos = db.Table(
    'indicacao_produtos',
    db.Column('indicacao_id', db.Integer, db.ForeignKey('indicacao.id'), primary_key=True),
    db.Column('produto_id', db.Integer, db.ForeignKey('produto.id'), primary_key=True),
)



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
    data_cadastro = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    responsavel = db.relationship('Usuario', backref=db.backref('empresas_responsavel', lazy=True))
    business_units = db.relationship('BusinessUnit', secondary=empresa_bus, backref='empresas')

    @property
    def bus_list(self):
        """Retorna a lista de nomes de BUs contratados."""
        return [bu.nome for bu in self.business_units]



class Indicacao(db.Model):
    __tablename__ = 'indicacao'

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresa.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    bu_indicado = db.Column(db.String(100), nullable=False)

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
    produtos = db.relationship('Produto', secondary=indicacao_produtos, backref='indicacoes')

    @property
    def produtos_lista(self):
        """Retorna a lista de nomes de produtos indicados."""
        return [p.nome for p in self.produtos]



class Conversa(db.Model):
    __tablename__ = 'conversa'

    id = db.Column(db.Integer, primary_key=True)
    usuario1_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    usuario2_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    usuario1 = db.relationship('Usuario', foreign_keys=[usuario1_id], backref=db.backref('conversas_iniciadas', lazy=True))
    usuario2 = db.relationship('Usuario', foreign_keys=[usuario2_id], backref=db.backref('conversas_recebidas', lazy=True))

    @property
    def room(self):
        """Nome da sala SocketIO para esta conversa."""
        return f'conversa_{self.id}'



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
