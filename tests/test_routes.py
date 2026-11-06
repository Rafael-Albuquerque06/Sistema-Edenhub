import pytest


def test_pagina_inicial_publica(client):
    """A página inicial deve ser acessível sem login."""
    resp = client.get('/')
    assert resp.status_code == 200


def test_pagina_login_publica(client):
    """A página de login deve ser acessível sem login."""
    resp = client.get('/login')
    assert resp.status_code == 200


def test_pagina_cadastro_publica(client):
    """A página de cadastro deve ser acessível sem login."""
    resp = client.get('/cadastro')
    assert resp.status_code == 200


def test_paginas_protegidas_redirecionam_sem_login(client):
    """Páginas protegidas devem redirecionar para login quando não autenticado."""
    for url in ['/home', '/portfolio', '/crosselling', '/consulta_clientes',
                '/comunicacao', '/minhas_pendencias']:
        resp = client.get(url)
        assert resp.status_code == 302


def test_cadastro_usuario(client):
    """Deve cadastrar um novo usuário com sucesso."""
    resp = client.post('/cadastro', data={
        'nome': 'Novo Usuario',
        'email': 'novo@exemplo.com',
        'telefone': '11988887777',
        'senha': 'senha123',
        'confirmar_senha': 'senha123',
    })
    assert resp.status_code == 302  # redirect para /login


def test_login_sucesso(client):
    """Deve fazer login com credenciais válidas."""
    # Primeiro cadastra
    client.post('/cadastro', data={
        'nome': 'Usuario Login',
        'email': 'login@exemplo.com',
        'telefone': '11977776666',
        'senha': 'senha123',
        'confirmar_senha': 'senha123',
    })

    # Depois faz login
    resp = client.post('/login', data={
        'usuario_login': 'login@exemplo.com',
        'senha': 'senha123',
    }, follow_redirects=True)
    assert resp.status_code == 200


def test_login_senha_errada(client):
    """Não deve fazer login com senha incorreta."""
    client.post('/cadastro', data={
        'nome': 'Usuario Senha',
        'email': 'senha@exemplo.com',
        'telefone': '11966665555',
        'senha': 'senha123',
        'confirmar_senha': 'senha123',
    })

    resp = client.post('/login', data={
        'usuario_login': 'senha@exemplo.com',
        'senha': 'senha_errada',
    })
    assert resp.status_code == 200  # fica na página de login com erro


def test_pagina_404(client):
    """Deve retornar 404 para rota inexistente."""
    resp = client.get('/rota-inexistente')
    assert resp.status_code == 404


def test_pagina_portfolio(app, client):
    """Portfólio deve listar as BUs do catálogo com imagem, CTA e compartilhamento."""
    client.post('/cadastro', data={
        'nome': 'Usuario Portfolio',
        'email': 'port@exemplo.com',
        'telefone': '11955554444',
        'senha': 'senha123',
        'confirmar_senha': 'senha123',
    })
    resp = client.post('/login', data={
        'usuario_login': 'port@exemplo.com',
        'senha': 'senha123',
    }, follow_redirects=True)
    assert resp.status_code == 200

    html = client.get('/portfolio').data.decode()
    assert 'Catálogo de Produtos/Serviços' in html
    assert 'Edenred Pay' in html
    assert 'Ticket Log' in html
    assert 'Ticket Serviços' in html
    assert 'portfolio-img' in html
    assert 'whatsapp-share' in html
