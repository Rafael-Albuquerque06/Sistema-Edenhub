"""Testes do chat em tempo real (SocketIO + persistência em services)."""

import pytest

from app import db
from app.models import Usuario, Conversa, Mensagem
from app.services import criar_usuario, criar_conversa, enviar_mensagem, autenticar_usuario


def _socketio_do(app):
    """Devolve a instância de SocketIO criada pela application factory."""
    return app.extensions['chat_socketio']


@pytest.fixture
def dois_usuarios(app):
    """Cria usuário A, usuário B e uma conversa entre eles."""
    with app.app_context():
        criar_usuario('Usuario A', 'a@x.com', '11111111111', 'senha123')
        criar_usuario('Usuario B', 'b@x.com', '22222222222', 'senha123')
        a = Usuario.query.filter_by(email='a@x.com').first()
        b = Usuario.query.filter_by(email='b@x.com').first()
        conversa = criar_conversa(a.id, b.id)
        return {
            'a': {'id': a.id, 'email': a.email},
            'b': {'id': b.id, 'email': b.email},
            'conversa_id': conversa.id,
        }


def _emit_ack(socket_client, evento, dados):
    """Emite um evento com ack e retorna o valor devolvido pelo servidor."""
    resultado = socket_client.emit(evento, dados, callback=True)
    if isinstance(resultado, list) and len(resultado) == 1:
        return resultado[0]
    return resultado


def _conectar_logado(app, client, email):
    """Faz login pelo client HTTP e conecta o socket com a mesma sessão."""
    client.post('/login', data={'usuario_login': email, 'senha': 'senha123'})
    return _socketio_do(app).test_client(app, flask_test_client=client)


def test_conecta_logado(app, client, dois_usuarios):
    """Usuário autenticado deve conseguir se conectar via socket."""
    socket_client = _conectar_logado(app, client, dois_usuarios['a']['email'])
    assert socket_client.is_connected()
    eventos = socket_client.get_received()
    assert any(e['name'] == 'user_status' for e in eventos)
    socket_client.disconnect()


def test_recusa_conexao_sem_login(app, dois_usuarios):
    """Sem autenticação a conexão deve ser recusada."""
    socket_client = _socketio_do(app).test_client(app)
    assert not socket_client.is_connected()


def test_entrar_e_enviar_mensagem(app, client, dois_usuarios):
    """Mensagem enviada via socket deve persistir e chegar ao participante."""
    socket_a = _conectar_logado(app, client, dois_usuarios['a']['email'])
    resposta = _emit_ack(socket_a, 'entrar', {'conversa_id': dois_usuarios['conversa_id']})
    assert resposta['ok'] is True

    ack = _emit_ack(socket_a, 'mensagem',
                    {'conversa_id': dois_usuarios['conversa_id'], 'texto': 'olá do A'})
    assert ack['ok'] is True

    with app.app_context():
        mensagem = Mensagem.query.filter_by(mensagem='olá do A').first()
        assert mensagem is not None
        assert mensagem.remetente_id == dois_usuarios['a']['id']


def test_mensagem_nao_participante_rejeitada(app, client, dois_usuarios):
    """Usuário fora da conversa não pode enviar mensagem (nem entrar)."""
    with app.app_context():
        criar_usuario('Intruso', 'c@x.com', '33333333333', 'senha123')
    socket_c = _conectar_logado(app, client, 'c@x.com')

    resposta = _emit_ack(socket_c, 'entrar', {'conversa_id': dois_usuarios['conversa_id']})
    assert resposta['ok'] is False

    ack = _emit_ack(socket_c, 'mensagem',
                    {'conversa_id': dois_usuarios['conversa_id'], 'texto': 'mensagem intrusa'})
    assert ack['ok'] is False

    with app.app_context():
        assert Mensagem.query.filter_by(mensagem='mensagem intrusa').first() is None


def test_mensagem_vazia_rejeitada(app, client, dois_usuarios):
    """Texto vazio/só espaços não deve criar mensagem."""
    socket_a = _conectar_logado(app, client, dois_usuarios['a']['email'])
    ack = _emit_ack(socket_a, 'mensagem',
                    {'conversa_id': dois_usuarios['conversa_id'], 'texto': '   '})
    assert ack['ok'] is False

    with app.app_context():
        assert Mensagem.query.filter_by(conversa_id=dois_usuarios['conversa_id']).count() == 0


def test_digitando_repassado_para_participante(app, client, dois_usuarios):
    """Evento digitando deve chegar ao outro participante exceto ao remetente."""
    socket_a = _conectar_logado(app, client, dois_usuarios['a']['email'])
    client_b = app.test_client()
    socket_b = _conectar_logado(app, client_b, dois_usuarios['b']['email'])

    for yours in (socket_a, socket_b):
        _emit_ack(yours, 'entrar', {'conversa_id': dois_usuarios['conversa_id']})
        yours.get_received()  # limpa buffer de user_status/ack

    socket_a.emit('digitando', {'conversa_id': dois_usuarios['conversa_id'], 'digitando': True})

    eventos_b = socket_b.get_received()
    nomes = [e['name'] for e in eventos_b]
    assert 'digitando' in nomes

    socket_a.disconnect()
    socket_b.disconnect()
