"""Presença de usuários (online/offline) em memória.

Para o modo threading do SocketIO o servidor roda em um único
processo, então um dicionário em memória com lock é suficiente.
"""

import threading

_lock = threading.Lock()
_sids = {}  # {sid: user_id}



def entrar(sid, user_id):
    """Registra uma conexão (sid) de um usuário."""
    with _lock:
        _sids[sid] = user_id



def sair(sid):
    """Remove uma conexão. Retorna o user_id associado, se houver."""
    with _lock:
        return _sids.pop(sid, None)



def ids_online():
    """Retorna o conjunto de user_ids com pelo menos uma conexão ativa."""
    with _lock:
        return set(_sids.values())



def usuario_online(user_id):
    """Verifica se um usuário tem conexão ativa."""
    with _lock:
        return user_id in _sids.values()
