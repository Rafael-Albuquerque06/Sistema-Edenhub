from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField, BooleanField, IntegerField, FloatField, TextAreaField, SelectMultipleField, widgets
from wtforms.validators import DataRequired, Email, Length, Optional
from Edenred.models import Usuario, Empresa, Indicacao
from Edenred import db
from wtforms.widgets import ListWidget, CheckboxInput

class LoginForm(FlaskForm):
    login = StringField('Email, telefone ou Skype', validators=[DataRequired()])
    senha = PasswordField('Senha', validators=[DataRequired()])
    btnSubmit = SubmitField('Avançar')

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

# REMOVA completamente a classe MultiCheckboxField e BUForm existente
# E SUBSTITUA por estas novas classes:

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