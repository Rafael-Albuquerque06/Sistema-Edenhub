import os

from dotenv import load_dotenv
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
import pytz

from app.config import get_config
from app.utils import formatar_data_brasil

load_dotenv('.env')

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'main.login'
login_manager.login_message = None


def create_app(config_name=None):
    app = Flask(__name__)
    app.config.from_object(get_config(config_name))

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # SocketIO por app (factory): evita compartilhar estado entre instâncias
    from flask_socketio import SocketIO
    socketio = SocketIO()
    socketio.init_app(app)
    app.extensions['chat_socketio'] = socketio
    from app.events import register_chat_events
    register_chat_events(socketio)

    @app.template_filter('formatar_data_brasil')
    def template_formatar_data_brasil(dt):
        return formatar_data_brasil(dt)

    from app.routes import main_bp
    app.register_blueprint(main_bp)

    @login_manager.user_loader
    def load_user(user_id):
        from app.models import Usuario
        return db.session.get(Usuario, int(user_id))

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        app.logger.error(f'Erro interno: {e}')
        return render_template('500.html'), 500

    return app
