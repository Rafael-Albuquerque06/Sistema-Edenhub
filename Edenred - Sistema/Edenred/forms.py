from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField, BooleanField, IntegerField, FloatField, TextAreaField, SelectMultipleField, widgets
from wtforms.validators import DataRequired, Email, Length, Optional, equal_to,ValidationError
from Edenred.models import Usuario, Empresa, Indicacao
from Edenred import db, bcrypt
from wtforms.widgets import ListWidget, CheckboxInput

class LoginForm(FlaskForm):
    usuario_login = StringField('Email, telefone ou Skype', validators=[DataRequired()])
    senha = PasswordField('Senha', validators=[DataRequired()])
    btnSubmit = SubmitField('Avançar')
    
    

class CadastroUsuarioForm(FlaskForm):
    nome = StringField('Nome Completo*', validators=[DataRequired()])
    email = StringField('E-mail*', validators=[DataRequired(), Email()])
    telefone = StringField('Telefone*', validators=[DataRequired()])
    skype = StringField('Skype', validators=[Optional()])
    senha = PasswordField('Senha*', validators=[DataRequired(), Length(min=6)])
    confirmar_senha = PasswordField('Confirmar Senha*', validators=[DataRequired(), equal_to('senha')])
    btnSubmit = SubmitField('Cadastrar')
    
    def validate_email(self, email):
        """Valida se o email já existe"""
        usuario = Usuario.query.filter_by(email=email.data).first()
        if usuario:
            raise ValidationError('Este email já está cadastrado!')
    
    def validate_telefone(self, telefone):
        """Valida se o telefone já existe"""
        usuario = Usuario.query.filter_by(telefone=telefone.data).first()
        if usuario:
            raise ValidationError('Este telefone já está cadastrado!')
    
    def validate_skype(self, skype):
        """Valida se o Skype já existe (apenas se preenchido)"""
        if skype.data:  # Só valida se o campo não estiver vazio
            usuario = Usuario.query.filter_by(skype=skype.data).first()
            if usuario:
                raise ValidationError('Este Skype já está cadastrado!')
    
    
    def save(self):
        """Cria e salva um novo usuário - MESMA LÓGICA DO MATERIAL DE ESTUDO"""
        usuario = Usuario(
            nome=self.nome.data,
            email=self.email.data,
            telefone=self.telefone.data,
            skype=self.skype.data
        )
        # 🔥 AGORA USA O MÉTODO set_senha COM BCRYPT (igual material de estudo)
        usuario.set_senha(self.senha.data)
        
        db.session.add(usuario)
        db.session.commit()
        return usuario
    

class CadastroBasicoForm(FlaskForm):
    razao_social = StringField('Razão Social*', validators=[DataRequired()])
    cep = StringField('CEP*', validators=[DataRequired()])
    logradouro = StringField('Logradouro*', validators=[DataRequired()])
    numero = StringField('Número*', validators=[DataRequired()])
    complemento = StringField('Complemento', validators=[Optional()])
    bairro = StringField('Bairro*', validators=[DataRequired()])
    municipio = StringField('Município*', validators=[DataRequired()])
    estado = StringField('Estado*', validators=[DataRequired(), Length(max=2)])
    
    nome_contato = StringField('Nome Completo*', validators=[DataRequired()])
    email_contato = StringField('E-mail*', validators=[DataRequired(), Email()])
    telefone_contato = StringField('Telefone*', validators=[DataRequired()])
    cargo_contato = StringField('Cargo*', validators=[DataRequired()])
    departamento_contato = StringField('Departamento*', validators=[DataRequired()])
    celular_contato = StringField('Celular', validators=[Optional()])
    
    btnSubmitBasico = SubmitField('ok')

    def save(self, cnpj):
            empresa = Empresa(
                cnpj=cnpj,
                razao_social=self.razao_social.data,
                cep=self.cep.data,
                logradouro=self.logradouro.data,
                numero=self.numero.data,
                complemento=self.complemento.data,
                bairro=self.bairro.data,
                municipio=self.municipio.data,
                estado=self.estado.data,
                nome_contato=self.nome_contato.data,
                email_contato=self.email_contato.data,
                telefone_contato=self.telefone_contato.data,
                cargo_contato=self.cargo_contato.data,
                departamento_contato=self.departamento_contato.data,
                celular_contato=self.celular_contato.data,
                eh_cliente=False
            )
            
            db.session.add(empresa)
            db.session.commit()
            return empresa

class BUForm(FlaskForm):
    bu_escolhido = SelectField('Qual BU você deseja indicar ou vender?*', 
                              choices=[('', 'Selecione'),
                                      ('Combo', 'Combo'),
                                      ('Edenred Pay', 'Edenred Pay'),
                                      ('Golntegro', 'Golntegro'),
                                      ('Punto', 'Punto'),
                                      ('Repom', 'Repom'),
                                      ('Ticket Log', 'Ticket Log'),
                                      ('Ticket Serviços', 'Ticket Serviços')],
                              validators=[DataRequired()])
    
    acao = SelectField('Qual ação deseja realizar?*',
                      choices=[('', 'Selecione'),
                              ('indicar', 'Indicar'),
                              ('vender', 'Vender')],
                      validators=[DataRequired()])

    # validar manualmente na view
    produtos = SelectMultipleField('Selecione os produtos disponíveis*',
                                   choices=[], 
                                   validators=[])
    
    btnSubmitBU = SubmitField('Continuar')

class IndicacaoForm(FlaskForm):
    quantidade_caminhoes = IntegerField('Quantidade de caminhões?', default=0, validators=[Optional()])
    quantidade_funcionarios = IntegerField('Quantos funcionários possui?', default=0, validators=[Optional()])
    quantidade_veiculos_pesados = IntegerField('Quantos veículos pesados (caminhões ou ônibus)?', default=0, validators=[Optional()])
    subsidia_combustivel = BooleanField('A empresa subsidia combustível a colaboradores?', default=False)
    quantidade_veiculos_leves = IntegerField('Quantos veículos leves (automóveis, picapes ou motocicletas)?', default=0, validators=[Optional()])
    quantidade_veiculos = IntegerField('Quantidade de veículos', default=0, validators=[Optional()])
    previsao_volume = FloatField('Previsão de volume (R$):', default=0.0, validators=[Optional()])
    quantidade_cartoes = IntegerField('Quantidade de cartões*', default=0, validators=[DataRequired()])
    observacoes = TextAreaField('Observações (Quantidade máxima de caracteres 4.000)', 
                               validators=[Length(max=4000), Optional()])
    btnSubmitIndicacao = SubmitField('OK')
    
    def save(self, empresa_id, usuario_id, bu, produtos):
        indicacao = Indicacao(
            empresa_id=empresa_id,
            usuario_id=usuario_id,
            bu_indicado=bu,
            produtos_escolhidos=produtos,
            quantidade_caminhoes=self.quantidade_caminhoes.data,
            quantidade_funcionarios=self.quantidade_funcionarios.data,
            quantidade_veiculos_pesados=self.quantidade_veiculos_pesados.data,
            subsidia_combustivel=self.subsidia_combustivel.data,
            quantidade_veiculos_leves=self.quantidade_veiculos_leves.data,
            quantidade_veiculos=self.quantidade_veiculos.data,
            previsao_volume=self.previsao_volume.data,
            quantidade_cartoes=self.quantidade_cartoes.data,
            observacoes=self.observacoes.data,
            status='Pendente'
        )
        
        db.session.add(indicacao)
        db.session.commit()
        return indicacao