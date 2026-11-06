from flask_wtf import FlaskForm
from wtforms import (
    StringField, SubmitField, PasswordField, SelectField,
    BooleanField, IntegerField, FloatField, TextAreaField,
    SelectMultipleField, FileField,
)
from wtforms.validators import DataRequired, Email, Length, Optional, EqualTo, ValidationError
from wtforms.widgets import ListWidget, CheckboxInput

import os
from werkzeug.utils import secure_filename

from app.models import Usuario, Empresa, Indicacao, Mensagem


class LoginForm(FlaskForm):
    usuario_login = StringField('Email, telefone ou Skype', validators=[DataRequired()])
    senha = PasswordField('Senha', validators=[DataRequired()])
    lembrar = BooleanField('Manter conectado', validators=[Optional()])
    btnSubmit = SubmitField('Entrar')


class CadastroUsuarioForm(FlaskForm):
    foto = FileField('Foto', validators=[Optional()])
    nome = StringField('Nome Completo*', validators=[DataRequired()])
    email = StringField('E-mail*', validators=[DataRequired(), Email()])
    telefone = StringField('Telefone*', validators=[DataRequired()])
    skype = StringField('Skype', validators=[Optional()])
    senha = PasswordField('Senha*', validators=[DataRequired(), Length(min=6)])
    confirmar_senha = PasswordField('Confirmar Senha*', validators=[DataRequired(), EqualTo('senha')])
    btnSubmit = SubmitField('Cadastrar')

    def validate_email(self, email):
        """Valida se o email já existe."""
        usuario = Usuario.query.filter_by(email=email.data).first()
        if usuario:
            raise ValidationError('Este email já está cadastrado!')

    def validate_telefone(self, telefone):
        """Valida se o telefone já existe."""
        usuario = Usuario.query.filter_by(telefone=telefone.data).first()
        if usuario:
            raise ValidationError('Este telefone já está cadastrado!')

    def validate_skype(self, skype):
        """Valida se o Skype já existe (apenas se preenchido)."""
        if skype.data and skype.data.strip():
            usuario = Usuario.query.filter_by(skype=skype.data).first()
            if usuario:
                raise ValidationError('Este Skype já está cadastrado!')

    def get_dados(self):
        """Retorna os dados validados para criação de usuário (sem salvar no banco)."""
        return {
            'nome': self.nome.data,
            'email': self.email.data,
            'telefone': self.telefone.data,
            'senha': self.senha.data,
            'skype': self.skype.data if self.skype.data and self.skype.data.strip() else None,
            'foto': self._processar_foto(),
        }

    def _processar_foto(self):
        foto = self.foto.data
        if foto and foto.filename:
            return secure_filename(foto.filename)
        return 'default.png'


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

    def get_dados(self):
        """Retorna os dados validados para criação de empresa (sem salvar no banco)."""
        return {
            'razao_social': self.razao_social.data,
            'cep': self.cep.data,
            'logradouro': self.logradouro.data,
            'numero': self.numero.data,
            'complemento': self.complemento.data,
            'bairro': self.bairro.data,
            'municipio': self.municipio.data,
            'estado': self.estado.data,
            'nome_contato': self.nome_contato.data,
            'email_contato': self.email_contato.data,
            'telefone_contato': self.telefone_contato.data,
            'cargo_contato': self.cargo_contato.data,
            'departamento_contato': self.departamento_contato.data,
            'celular_contato': self.celular_contato.data,
        }


class BUForm(FlaskForm):
    bu_escolhido = SelectField(
        'Qual BU você deseja indicar ou vender?*',
        choices=[('', 'Selecione'),
                 ('Combo', 'Combo'),
                 ('Edenred Pay', 'Edenred Pay'),
                 ('Golntegro', 'Golntegro'),
                 ('Punto', 'Punto'),
                 ('Repom', 'Repom'),
                 ('Ticket Log', 'Ticket Log'),
                 ('Ticket Serviços', 'Ticket Serviços')],
        validators=[DataRequired()],
    )
    acao = SelectField(
        'Qual ação deseja realizar?*',
        choices=[('', 'Selecione'), ('indicar', 'Indicar'), ('vender', 'Vender')],
        validators=[DataRequired()],
    )
    produtos = SelectMultipleField('Selecione os produtos disponíveis*', choices=[], validators=[])
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
    observacoes = TextAreaField('Observações (Quantidade máxima de caracteres 4.000)', validators=[Length(max=4000), Optional()])
    btnSubmitIndicacao = SubmitField('OK')

    def get_dados(self):
        """Retorna os dados validados para criação de indicação (sem salvar no banco)."""
        return {
            'quantidade_caminhoes': self.quantidade_caminhoes.data,
            'quantidade_funcionarios': self.quantidade_funcionarios.data,
            'quantidade_veiculos_pesados': self.quantidade_veiculos_pesados.data,
            'subsidia_combustivel': self.subsidia_combustivel.data,
            'quantidade_veiculos_leves': self.quantidade_veiculos_leves.data,
            'quantidade_veiculos': self.quantidade_veiculos.data,
            'previsao_volume': self.previsao_volume.data,
            'quantidade_cartoes': self.quantidade_cartoes.data,
            'observacoes': self.observacoes.data,
        }


class MensagemForm(FlaskForm):
    mensagem = TextAreaField('Mensagem', validators=[DataRequired(), Length(max=2000)])
    btnEnviar = SubmitField('Enviar')
