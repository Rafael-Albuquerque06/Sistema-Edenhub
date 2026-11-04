import pytest
from app import db
from app.models import Usuario, Empresa, Indicacao


def test_criar_usuario(app, usuario):
    """Deve criar um usuário com senha criptografada."""
    with app.app_context():
        u = Usuario.query.get(usuario['id'])
        assert u is not None
        assert u.nome == 'Usuario Teste'
        assert u.email == 'teste@exemplo.com'
        assert u.check_senha('senha123') is True
        assert u.check_senha('senha_errada') is False


def test_email_unico(app):
    """Não deve permitir email duplicado."""
    with app.app_context():
        u1 = Usuario(nome='User 1', email='dup@exemplo.com', telefone='11111111111')
        u1.set_senha('senha123')
        db.session.add(u1)
        db.session.commit()

        u2 = Usuario(nome='User 2', email='dup@exemplo.com', telefone='22222222222')
        u2.set_senha('senha123')
        db.session.add(u2)
        with pytest.raises(Exception):
            db.session.commit()


def test_criar_empresa(app, empresa):
    """Deve criar uma empresa associada a um usuário."""
    with app.app_context():
        e = Empresa.query.get(empresa['id'])
        assert e is not None
        assert e.cnpj == '11222333000181'
        assert e.razao_social == 'Empresa Teste LTDA'
        assert e.responsavel_id is not None


def test_bus_list_propriedade(app, empresa):
    """A propriedade bus_list deve retornar uma lista de BUs."""
    with app.app_context():
        e = Empresa.query.get(empresa['id'])
        e.contracted_business_units = 'Edenred Pay, Ticket Log'
        db.session.commit()
        assert e.bus_list == ['Edenred Pay', 'Ticket Log']

        e.contracted_business_units = None
        db.session.commit()
        assert e.bus_list == []

        e.contracted_business_units = ''
        db.session.commit()
        assert e.bus_list == []


def test_criar_indicacao(app, empresa, usuario):
    """Deve criar uma indicação associando empresa e usuário."""
    with app.app_context():
        e = Empresa.query.get(empresa['id'])
        u = Usuario.query.get(usuario['id'])
        indicacao = Indicacao(
            empresa_id=e.id,
            usuario_id=u.id,
            bu_indicado='Edenred Pay',
            produtos_escolhidos='Cartão Corporativo, Pagamento Digital',
            quantidade_cartoes=100,
            status='Pendente',
        )
        db.session.add(indicacao)
        db.session.commit()

        assert indicacao.id is not None
        assert indicacao.bu_indicado == 'Edenred Pay'
        assert indicacao.status == 'Pendente'
        assert indicacao.empresa_id == e.id
        assert indicacao.usuario_id == u.id


def test_verificar_duplicidade(app, empresa, usuario):
    """A verificação de duplicidade deve retornar produtos duplicados."""
    with app.app_context():
        e = Empresa.query.get(empresa['id'])
        u = Usuario.query.get(usuario['id'])

        # Cria uma indicação existente
        indicacao_existente = Indicacao(
            empresa_id=e.id,
            usuario_id=u.id,
            bu_indicado='Ticket Log',
            produtos_escolhidos='Gestão de Abastecimento, Abastecimento',
            quantidade_cartoes=50,
            status='Pendente',
        )
        db.session.add(indicacao_existente)
        db.session.commit()

        from app.services import verificar_duplicidade
        duplicados = verificar_duplicidade(
            e.cnpj, ['Gestão de Abastecimento']
        )
        assert 'Gestão de Abastecimento' in duplicados
