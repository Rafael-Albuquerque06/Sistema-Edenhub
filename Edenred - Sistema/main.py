from Edenred import app, db
from Edenred.models import Usuario, Empresa
        
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    app.run(debug=True)