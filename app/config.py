"""Configuração da aplicação por classes de ambiente."""

import os

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))



class Config:
    """Base compartilhada por todos os ambientes."""
    SECRET_KEY = os.getenv('SECRET_KEY')
    # Caminhos sqlite relativos são prefixados com instance_path pelo
    # Flask-SQLAlchemy: 'sqlite:///edenred.db' -> instance/edenred.db
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI') or 'sqlite:///edenred.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FILES = 'static/data'
    WTF_CSRF_ENABLED = True



class DevelopmentConfig(Config):
    DEBUG = True
    SECRET_KEY = os.getenv('SECRET_KEY') or 'chave-de-desenvolvimento-nao-usar-em-producao'



class ProductionConfig(Config):
    pass



class TestingConfig(Config):
    TESTING = True
    DEBUG = False
    SECRET_KEY = 'chave-de-teste'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False



CONFIGS = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
}



def get_config(nome=None):
    """Resolve a classe de configuração pelo nome, APP_CONFIG ou FLASK_ENV."""
    nome = nome or os.getenv('APP_CONFIG') or os.getenv('FLASK_ENV') or 'development'
    return CONFIGS.get(nome, DevelopmentConfig)
