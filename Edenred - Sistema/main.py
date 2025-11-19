from Edenred import app, db
from Edenred.models import Usuario, Empresa

def criar_dados_mock():
   
    if not Usuario.query.first():
        
        admin = Usuario(
            nome="administrador",
            email="admin@edenred.com",
            telefone="11999999999",
            skype="admin.edenred",
        )
        admin.set_senha("admin123")
        db.session.add(admin)
        
        empresas_mock = [
            {
                'cnpj': '12345678000195',
                'razao_social': 'Empresa Teste 1 Ltda',
                'cep': '01234000',
                'logradouro': 'Rua Teste 1',
                'numero': '123',
                'bairro': 'Centro',
                'municipio': 'São Paulo',
                'estado': 'SP',
                'eh_cliente': True,
                'bus_contratados': 'Ticket Log, Edenred Pay'
            },
            {
                'cnpj': '98765432000110',
                'razao_social': 'Empresa Teste 2 S/A',
                'cep': '04567000',
                'logradouro': 'Av Teste 2',
                'numero': '456',
                'bairro': 'Jardins',
                'municipio': 'São Paulo',
                'estado': 'SP',
                'eh_cliente': True,
                'bus_contratados': 'Combo'
            }
        ]
        
        for emp_data in empresas_mock:
            empresa = Empresa(**emp_data)
            db.session.add(empresa)
        
        db.session.commit()
        print("Dados mockados criados")
        
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        criar_dados_mock()
    
    app.run(debug=True)