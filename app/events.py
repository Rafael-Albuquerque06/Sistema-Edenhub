"""Eventos SocketIO do chat (mensagens, "digitando...", presença).

Namespace raiz. Persistência das mensagens continua em services (SQLite).
Validação de pertencimento à conversa é feita em todos os eventos.

Os handlers são registrados em register_chat_events(), chamada pela
application factory para cada instância de SocketIO.
"""

from flask import request
from flask_login import current_user
from flask_socketio import emit, join_room

from app import presence
from app import db
from app.models import Conversa
from app.services import enviar_mensagem
from app.utils import formatar_data_brasil

MAX_MENSAGEM = 2000



def _conversa_do_usuario(conversa_id):
    """Retorna a conversa se o usuário atual for participante; None caso contrário."""
    conversa = db.session.get(Conversa, conversa_id)
    if not conversa or current_user.id not in (conversa.usuario1_id, conversa.usuario2_id):
        return None
    return conversa



def register_chat_events(socketio):
    """Registra os eventos do chat em uma instância de SocketIO."""

    @socketio.on('connect')
    def on_connect():
        """Recusa conexão sem login e registra presença."""
        if not current_user.is_authenticated:
            return False  # rejeita a conexão
        presence.entrar(request.sid, current_user.id)
        emit('user_status', {'user_id': current_user.id, 'online': True}, broadcast=True)

    @socketio.on('disconnect')
    def on_disconnect():
        """Libera a conexão e avisa offline quando não há outras conexões."""
        user_id = presence.sair(request.sid)
        if user_id is not None and user_id not in presence.ids_online():
            emit('user_status', {'user_id': user_id, 'online': False}, broadcast=True)

    @socketio.on('entrar')
    def on_entrar(data):
        """Cliente entra na sala da conversa (validando participação)."""
        conversa = _conversa_do_usuario((data or {}).get('conversa_id'))
        if not conversa:
            return {'ok': False}
        join_room(conversa.room)
        return {'ok': True, 'usuario': current_user.id}

    @socketio.on('digitando')
    def on_digitando(data):
        """Repassa o estado "digitando..." para o outro participante."""
        data = data or {}
        conversa = _conversa_do_usuario(data.get('conversa_id'))
        if not conversa:
            return
        emit('digitando', {
            'user_id': current_user.id,
            'nome': current_user.nome,
            'digitando': bool(data.get('digitando')),
        }, room=conversa.room, include_self=False)

    @socketio.on('mensagem')
    def on_mensagem(data):
        """Persiste a mensagem e distribui para a sala (inclui o remetente)."""
        data = data or {}
        conversa = _conversa_do_usuario(data.get('conversa_id'))
        texto = str(data.get('texto') or '').strip()
        if not conversa or not texto:
            return {'ok': False}
        texto = texto[:MAX_MENSAGEM]

        mensagem = enviar_mensagem(conversa.id, current_user.id, texto)
        emit('nova_mensagem', {
            'conversa_id': conversa.id,
            'id': mensagem.id,
            'texto': mensagem.mensagem,
            'remetente_id': mensagem.remetente_id,
            'remetente_nome': current_user.nome,
            'data': formatar_data_brasil(mensagem.data_envio),
        }, room=conversa.room)
        return {'ok': True}

    return socketio

