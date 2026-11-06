import pytest

from app import db
from app.models import Usuario, Empresa, Conversa, Mensagem
from app.services import (
    criar_usuario,
    criar_empresa,
    vincular_bu_empresa,
    criar_indicacao,
    verificar_duplicidade,
    autenticar_usuario,
    consultar_empresa_por_cnpj,
    criar_conversa,
    enviar_mensagem,
    marcar_mensagens_lidas,
    contar_metricas,
    listar_outros_usuarios,
    listar_clientes,
    listar_mensagens,
)


# --- Usuários / autenticação ---

def test_criar_usuario_duplicados(app):
    """Serviço deve recusar email, telefone ou skype duplicados."""
    with app.app_context():
        criar_usuario('User', 'a@x.com', '11111111111', 'senha123', skype='skype1')

        with pytest.raises(ValueError, match='email'):
            criar_usuario('User2', 'a@x.com', '22222222222', 'senha123')
        with pytest.raises(ValueError, match='telefone'):
            criar_usuario('User2', 'b@x.com', '11111111111', 'senha123')
        with pytest.raises(ValueError, match='Skype'):
            criar_usuario('User2', 'b@x.com', '22222222222', 'senha123', skype='skype1')


def test_criar_usuario_normaliza_email_telefone(app):
    """Email deve ser salvo em minúsculas e telefone apenas com dígitos."""
    with app.app_context():
        u = criar_usuario('User', 'CAIXA@X.COM ', '(11) 98888-7777', 'senha123')
        assert u.email == 'caixa@x.com'
        assert u.telefone == '11988887777'

        # autentica pelo telefone mascarado (com dígitos normalizados)
        assert autenticar_usuario('(11) 98888-7777', 'senha123') is not None


def test_autenticar_usuario(app, usuario):
    """Autenticação correta e falha por credencial errada."""
    with app.app_context():
        assert autenticar_usuario('teste@exemplo.com', 'senha123') is not None
        assert autenticar_usuario('11999999999', 'senha123') is not None
        assert autenticar_usuario('teste_skype', 'senha123') is not None
        assert autenticar_usuario('teste@exemplo.com', 'errada') is None
        assert autenticar_usuario('inexistente@x.com', 'senha123') is None


# --- Empresas / Cross-selling ---

def test_consultar_empresa_por_cnpj(app, empresa):
    """Limpa o CNPJ, valida dígitos e busca a empresa. Inexistente retorna empresa None."""
    with app.app_context():
        resultado = consultar_empresa_por_cnpj('11.222.333/0001-81')
        assert resultado['valido'] is True
        assert resultado['empresa'] is not None
        assert resultado['empresa'].cnpj == '11222333000181'

        resultado = consultar_empresa_por_cnpj('99999999999999')
        assert resultado['valido'] is False  # DV inválido
        assert resultado['empresa'] is None

        resultado = consultar_empresa_por_cnpj('19131243000197')  # válido, sem cadastro
        assert resultado['valido'] is True
        assert resultado['empresa'] is None

        resultado = consultar_empresa_por_cnpj('123')
        assert resultado['valido'] is False
        assert resultado['empresa'] is None


def test_criar_empresa(app):
    """Serviço deve criar empresa limpando o CNPJ."""
    with app.app_context():
        dados = {
            'razao_social': 'Nova LTDA', 'cep': '12345-678', 'logradouro': 'Rua A',
            'numero': '10', 'complemento': None, 'bairro': 'B', 'municipio': 'M',
            'estado': 'SP', 'nome_contato': 'C', 'email_contato': 'c@x.com',
            'telefone_contato': '1133334444', 'cargo_contato': 'Gerente',
            'departamento_contato': 'Comercial', 'celular_contato': None,
        }
        empresa = criar_empresa('11.222.333/0001-81', dados)
        assert empresa.cnpj == '11222333000181'


def test_vincular_bu_venda(app, empresa, usuario):
    """Ação vender deve marcar como cliente, vincular responsável e BU (N:N)."""
    with app.app_context():
        e = db.session.get(Empresa, empresa['id'])
        u = db.session.get(Usuario, usuario['id'])
        e2, etapa = vincular_bu_empresa(e, 'Repom', 'vender', u)
        assert etapa == 'venda_concluida'
        assert e2.is_client is True
        assert e2.responsavel_id == u.id
        assert e2.bus_list == ['Repom']

        # repetir não duplica o BU
        e3, _ = vincular_bu_empresa(e2, 'Repom', 'vender', u)
        assert e3.bus_list == ['Repom']


def test_vincular_bu_indicacao_retorna_etapa(app, empresa, usuario):
    """Ação indicar não deve marcar como cliente."""
    with app.app_context():
        e = db.session.get(Empresa, empresa['id'])
        u = db.session.get(Usuario, usuario['id'])
        _, etapa = vincular_bu_empresa(e, 'Repom', 'indicar', u)
        assert etapa == 'indicacao'
        assert e.is_client is False
        assert e.bus_list == []


def test_criar_indicacao_duplicidade(app, empresa, usuario):
    """Criar indicação com produto repetido em menos de 3 meses deve falhar."""
    with app.app_context():
        criar_indicacao(
            empresa_id=empresa['id'], usuario_id=usuario['id'],
            bu='Ticket Log', produtos=['Gestão de Abastecimento'],
            dados={'quantidade_cartoes': 10},
        )
        with pytest.raises(ValueError, match='Gestão de Abastecimento'):
            criar_indicacao(
                empresa_id=empresa['id'], usuario_id=usuario['id'],
                bu='Repom', produtos=['Gestão de Abastecimento'],
                dados={'quantidade_cartoes': 5},
            )

        # produtos distintos passam
        indicacao = criar_indicacao(
            empresa_id=empresa['id'], usuario_id=usuario['id'],
            bu='Repom', produtos=['Controle de Abastecimento'],
            dados={'quantidade_cartoes': 5},
        )
        assert 'Controle de Abastecimento' in indicacao.produtos_lista
        assert verificar_duplicidade(
            empresa['cnpj'], ['Controle de Abastecimento']
        ) == ['Controle de Abastecimento']


# --- Comunicação ---

def test_criar_conversa_idempotente(app):
    """Conversa já existente deve ser reutilizada, independentemente da ordem."""
    with app.app_context():
        criar_usuario('A', 'a@x.com', '11111111111', 'senha123')
        criar_usuario('B', 'b@x.com', '22222222222', 'senha123')
        a = Usuario.query.filter_by(email='a@x.com').first()
        b = Usuario.query.filter_by(email='b@x.com').first()

        c1 = criar_conversa(a.id, b.id)
        c2 = criar_conversa(b.id, a.id)
        assert c1.id == c2.id
        assert Conversa.query.count() == 1


def test_enviar_e_marcar_lidas(app):
    """Mensagens do próprio usuário não são mantidas; dos outros são marcadas."""
    with app.app_context():
        criar_usuario('A', 'a@x.com', '11111111111', 'senha123')
        criar_usuario('B', 'b@x.com', '22222222222', 'senha123')
        a = Usuario.query.filter_by(email='a@x.com').first()
        b = Usuario.query.filter_by(email='b@x.com').first()
        conversa = criar_conversa(a.id, b.id)

        enviar_mensagem(conversa.id, a.id, 'oi')
        enviar_mensagem(conversa.id, b.id, 'olá')

        mensagens = marcar_mensagens_lidas(conversa.id, a.id)
        por_remetente = {(m.remetente_id, m.lida) for m in mensagens}
        assert (a.id, False) in por_remetente  # do próprio, inalterada
        assert (b.id, True) in por_remetente   # do outro, lida


def test_listar_mensagens_ordenado(app):
    """Mensagens devem vir ordenadas por data de envio."""
    with app.app_context():
        criar_usuario('A', 'a@x.com', '11111111111', 'senha123')
        criar_usuario('B', 'b@x.com', '22222222222', 'senha123')
        a = Usuario.query.filter_by(email='a@x.com').first()
        b = Usuario.query.filter_by(email='b@x.com').first()
        conversa = criar_conversa(a.id, b.id)

        enviar_mensagem(conversa.id, a.id, 'primeira')
        enviar_mensagem(conversa.id, b.id, 'segunda')

        mensagens = listar_mensagens(conversa.id)
        assert [m.mensagem for m in mensagens] == ['primeira', 'segunda']


def test_sem_mensagens_marcar_lidas_vazia(app):
    """Conversa sem mensagens deve retornar lista vazia sem erro."""
    with app.app_context():
        criar_usuario('A', 'a@x.com', '11111111111', 'senha123')
        criar_usuario('B', 'b@x.com', '22222222222', 'senha123')
        a = Usuario.query.filter_by(email='a@x.com').first()
        b = Usuario.query.filter_by(email='b@x.com').first()
        conversa = criar_conversa(a.id, b.id)

        assert marcar_mensagens_lidas(conversa.id, a.id) == []


def test_listar_outros_usuarios(app, usuario):
    """Deve excluir o próprio usuário da lista."""
    with app.app_context():
        criar_usuario('Outro', 'b@x.com', '22222222222', 'senha123')
        lista = listar_outros_usuarios(usuario['id'])
        ids = [u.id for u in lista]
        assert usuario['id'] not in ids
        assert len(ids) == 1


# --- Métricas / Consulta ---

def test_contar_metricas(app, empresa, usuario):
    """Métricas devem refletir indicações próprias e clientes cadastrados."""
    with app.app_context():
        e = db.session.get(Empresa, empresa['id'])
        u = db.session.get(Usuario, usuario['id'])

        criar_indicacao(
            empresa_id=e.id, usuario_id=u.id, bu='Repom',
            produtos=['Gestão de Frotas'], dados={'quantidade_cartoes': 3},
        )

        metricas = contar_metricas(u.id)
        assert metricas == {'minhas_indicacoes': 1, 'minhas_pendentes': 1, 'total_clientes': 0}


def test_listar_clientes_filtro(app, empresa, usuario):
    """Consulta de clientes deve filtrar por razão social e contar pendências."""
    with app.app_context():
        e = db.session.get(Empresa, empresa['id'])
        u = db.session.get(Usuario, usuario['id'])
        from app.services import vincular_bu_empresa
        vincular_bu_empresa(e, 'Repom', 'vender', u)

        criar_indicacao(
            empresa_id=e.id, usuario_id=u.id, bu='Repom',
            produtos=['Gestão de Frotas'], dados={'quantidade_cartoes': 3},
        )

        clientes_por_nome = listar_clientes('Empresa Teste')
        assert len(clientes_por_nome) == 1
        assert clientes_por_nome[0].bus_list == ['Repom']

        # pendência atribuída à empresa
        assert clientes_por_nome[0].indicacoes_pendentes >= 1

        assert listar_clientes('inexistente-xyz') == []
