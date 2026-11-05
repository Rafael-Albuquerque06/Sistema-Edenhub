import os
from dotenv import load_dotenv
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
import pytz
from datetime import datetime, timezone

load_dotenv('.env')

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'main.login'
login_manager.login_message = None


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['UPLOAD_FILES'] = 'static/data'

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    @app.template_filter('formatar_data_brasil')
    def formatar_data_brasil(dt):
        """Converte UTC para horário de Brasília e formata."""
        if not dt:
            return ""
        try:
            if dt.tzinfo is None:
                dt = pytz.utc.localize(dt)
            tz_brasil = pytz.timezone('America/Sao_Paulo')
            dt_brasil = dt.astimezone(tz_brasil)
            return dt_brasil.strftime('%d/%m/%Y %H:%M')
        except Exception:
            return dt.strftime('%d/%m/%Y %H:%M')

    from app.routes import main_bp
    app.register_blueprint(main_bp)

    @login_manager.user_loader
    def load_user(user_id):
        from app.models import Usuario
        return Usuario.query.get(int(user_id))

    @app.errorhandler(404)
    def page_not_found(e):
        return (
            "<html><body><h1>404 - Página não encontrada</h1>"
            "<p>A página que você procura não existe.</p>"
            "<a href='/'>Voltar ao início</a></body></html>",
            404,
        )

    @app.errorhandler(500)
    def internal_server_error(e):
        return (
            "<html><body><h1>500 - Erro interno do servidor</h1>"
            "<p>Ocorreu um erro interno. Tente novamente mais tarde.</p>"
            "<a href='/'>Voltar ao início</a></body></html>",
            500,
        )

    # Garantir que as tabelas sejam criadas no primeiro acesso
    with app.app_context():
        try:
            db.create_all()
            app.logger.info('Banco de dados inicializado com sucesso')
        except Exception as e:
            app.logger.error(f'Erro ao criar tabelas: {e}')

    return app
