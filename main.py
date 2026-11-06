from app import create_app, db
from app.models import Usuario, Empresa

app = create_app()


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # Servidor de desenvolvimento; em produção usa gunicorn + wsgi.py
    socketio = app.extensions['chat_socketio']
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
