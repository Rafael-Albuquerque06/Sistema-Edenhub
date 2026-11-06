import pytest
from app import db
from app.models import Usuario, Empresa, Indicacao, BusinessUnit, Produto


def test_criar_usuario(app, usuario):
    """Deve criar um usuário com senha criptografada."""
    with app.app_context():
        u = db.session.get(Usuario, usuario['id'])
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
        e = db.session.get(Empresa, empresa['id'])
        assert e is not None
        assert e.cnpj == '11222333000181'
        assert e.razao_social == 'Empresa Teste LTDA'
        assert e.responsavel_id is not None


def test_bus_list_propriedade(app, empresa):
    """A propriedade bus_list deve retornar a lista de BUs vinculados (N:N)."""
    with app.app_context():
        e = db.session.get(Empresa, empresa['id'])
        e.business_units.append(BusinessUnit(nome='Edenred Pay'))
        e.business_units.append(BusinessUnit(nome='Ticket Log'))
        db.session.commit()
        assert e.bus_list == ['Edenred Pay', 'Ticket Log']

        e.business_units.clear()
        db.session.commit()
        assert e.bus_list == []


def test_criar_indicacao(app, empresa, usuario):
    """Deve criar uma indicação associando empresa e usuário com produtos (N:N)."""
    with app.app_context():
        e = db.session.get(Empresa, empresa['id'])
        u = db.session.get(Usuario, usuario['id'])
        indicacao = Indicacao(
            empresa_id=e.id,
            usuario_id=u.id,
            bu_indicado='Edenred Pay',
            quantidade_cartoes=100,
            status='Pendente',
        )
        indicacao.produtos = [Produto(nome='Cartão Corporativo'), Produto(nome='Pagamento Digital')]
        db.session.add(indicacao)
        db.session.commit()

        assert indicacao.id is not None
        assert indicacao.bu_indicado == 'Edenred Pay'
        assert indicacao.status == 'Pendente'
        assert indicacao.empresa_id == e.id
        assert indicacao.usuario_id == u.id
        assert indicacao.produtos_lista == ['Cartão Corporativo', 'Pagamento Digital']


def test_verificar_duplicidade(app, empresa, usuario):
    """A verificação de duplicidade deve retornar produtos duplicados."""
    from app.services import criar_indicacao, verificar_duplicidade

    with app.app_context():
        criar_indicacao(
            empresa_id=empresa['id'],
            usuario_id=usuario['id'],
            bu='Ticket Log',
            produtos=['Gestão de Abastecimento', 'Abastecimento'],
            dados={'quantidade_cartoes': 50},
        )

        duplicados = verificar_duplicidade(
            empresa['cnpj'], ['Gestão de Abastecimento']
        )
        assert 'Gestão de Abastecimento' in duplicados


def test_verificar_duplicidade_periodo(app, empresa, usuario):
    """Produtos indicados fora do período não devem ser considerados duplicados."""
    with app.app_context():
        from app.services import criar_indicacao, verificar_duplicidade
        from datetime import datetime, timezone, timedelta

        indicacao = Indicacao(
            empresa_id=empresa['id'],
            usuario_id=usuario['id'],
            bu_indicado='Ticket Log',
            data_indicacao=datetime.now(timezone.utc) - timedelta(days=120),
            status='Pendente',
        )
        indicacao.produtos = [Produto(nome='Gestão de Abastecimento')]
        db.session.add(indicacao)
        db.session.commit()

        duplicados = verificar_duplicidade(empresa['cnpj'], ['Gestão de Abastecimento'])
        assert duplicados == []
