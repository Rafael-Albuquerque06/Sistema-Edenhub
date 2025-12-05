from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import os
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt

load_dotenv('.env')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['UPLOAD_FILES'] = r'static/data'

import pytz
from datetime import datetime, timezone

@app.template_filter('formatar_data_brasil')
def formatar_data_brasil(dt):
    """Converte UTC para horário de Brasília e formata"""
    if not dt:
        return ""
    
    try:
        # Se não tem timezone, assume que é UTC
        if dt.tzinfo is None:
            dt = pytz.utc.localize(dt)
        
        # Converter para São Paulo (Brasília)
        tz_brasil = pytz.timezone('America/Sao_Paulo')
        dt_brasil = dt.astimezone(tz_brasil)
        
        # Formatar
        return dt_brasil.strftime('%d/%m/%Y %H:%M')
    except Exception:
        # Fallback: formata sem conversão
        return dt.strftime('%d/%m/%Y %H:%M')

db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)

# Configuração do Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = None

from Edenred.models import Usuario
from Edenred.views import *

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))