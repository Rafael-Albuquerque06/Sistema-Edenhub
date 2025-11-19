from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'DCAMÇKVDSVNLADVDNVLJSNL!!MCKÇASNCAKÇ-JDSN648484AADSDSADASDA'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

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