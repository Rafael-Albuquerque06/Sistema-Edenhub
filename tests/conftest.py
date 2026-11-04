import os
import sys

# Garante que o pacote app seja importável
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from app import create_app, db


@pytest.fixture
def app():
    """Cria uma aplicação Flask configurada para testes com banco in-memory."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    app.config['DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Retorna um client de teste para a aplicação."""
    return app.test_client()


@pytest.fixture
def usuario(app):
    """Cria um usuário de teste no banco e retorna seus dados."""
    with app.app_context():
        from app.models import Usuario
        u = Usuario(
            nome='Usuario Teste',
            email='teste@exemplo.com',
            telefone='11999999999',
            skype='teste_skype',
            foto='default.png',
        )
        u.set_senha('senha123')
        db.session.add(u)
        db.session.commit()
        # Retorna dados primitivos para evitar DetachedInstanceError
        return {'id': u.id, 'email': u.email, 'nome': u.nome}


@pytest.fixture
def empresa(app, usuario):
    """Cria uma empresa de teste no banco e retorna seus dados."""
    with app.app_context():
        from app.models import Empresa, Usuario
        u = Usuario.query.get(usuario['id'])
        e = Empresa(
            cnpj='11222333000181',
            razao_social='Empresa Teste LTDA',
            cep='01234567',
            logradouro='Rua Teste',
            numero='123',
            bairro='Bairro Teste',
            municipio='São Paulo',
            estado='SP',
            nome_contato='Contato Teste',
            email_contato='contato@empresa.com',
            telefone_contato='1133334444',
            cargo_contato='Gerente',
            departamento_contato='Comercial',
            is_client=False,
            responsavel_id=u.id,
        )
        db.session.add(e)
        db.session.commit()
        # Retorna dados primitivos
        return {'id': e.id, 'cnpj': e.cnpj, 'razao_social': e.razao_social}
