import re
from datetime import datetime, timezone, timedelta

import sqlalchemy as sa

from app import db
from app.models import (
    Usuario, Empresa, Indicacao, Conversa, Mensagem, BusinessUnit, Produto,
)
from app.utils import limpar_cnpj, validar_cnpj, formatar_cnpj

TELEFONE_DIGITOS = re.compile(r'\D')

def _get_or_create(modelo, nome):
    """Busca um registro pelo nome único ou cria um novo."""
    registro = db.session.scalar(sa.select(modelo).where(modelo.nome == nome))
    if registro is None:
        registro = modelo(nome=nome)
        db.session.add(registro)
        db.session.flush()  # garante id antes do commit
    return registro



def normalizar_telefone(telefone):
    """Deixa apenas os dígitos de um telefone."""
    return TELEFONE_DIGITOS.sub('', telefone or '')



# --- Usuários ---

def criar_usuario(nome, email, telefone, senha, skype=None, foto='default.png'):
    """Cria e salva um novo usuário. Retorna o usuário ou levanta exceção."""
    email = (email or '').strip().lower()
    telefone = normalizar_telefone(telefone)
    skype = skype if skype and skype.strip() else None

    if Usuario.query.filter_by(email=email).first():
        raise ValueError('Este email já está cadastrado!')
    if Usuario.query.filter_by(telefone=telefone).first():
        raise ValueError('Este telefone já está cadastrado!')
    if skype and Usuario.query.filter_by(skype=skype).first():
        raise ValueError('Este Skype já está cadastrado!')

    usuario = Usuario(nome=nome, email=email, telefone=telefone, skype=skype, foto=foto)
    usuario.set_senha(senha)

    db.session.add(usuario)
    db.session.commit()
    return usuario



def autenticar_usuario(login_info, senha):
    """Busca o usuário por email, telefone ou Skype e valida a senha."""
    login_info = (login_info or '').strip()
    usuario = Usuario.query.filter(
        (Usuario.email == login_info)
        | (Usuario.telefone == login_info)
        | (Usuario.telefone == normalizar_telefone(login_info))
        | (Usuario.skype == login_info)
    ).first()
    if usuario and usuario.check_senha(senha):
        return usuario
    return None



# --- Empresas / Cross-selling ---

def consultar_empresa_por_cnpj(cnpj_bruto):
    """Limpa e valida o CNPJ, depois busca a empresa. Retorna dict com empresa ou motivo."""
    cnpj = limpar_cnpj(cnpj_bruto)
    if not validar_cnpj(cnpj):
        return {'cnpj': cnpj, 'valido': False, 'empresa': None}
    empresa = Empresa.query.filter_by(cnpj=cnpj).first()
    return {'cnpj': cnpj, 'valido': True, 'empresa': empresa}



def criar_empresa(cnpj, dados):
    """Cria e salva uma nova empresa básica. Retorna a empresa."""
    dados = {k: (v.strip() if isinstance(v, str) else v) for k, v in dados.items()}
    empresa = Empresa(
        cnpj=limpar_cnpj(cnpj),
        razao_social=dados['razao_social'],
        cep=dados['cep'],
        logradouro=dados['logradouro'],
        numero=dados['numero'],
        complemento=dados.get('complemento'),
        bairro=dados['bairro'],
        municipio=dados['municipio'],
        estado=dados['estado'],
        nome_contato=dados['nome_contato'],
        email_contato=dados['email_contato'],
        telefone_contato=dados['telefone_contato'],
        cargo_contato=dados['cargo_contato'],
        departamento_contato=dados['departamento_contato'],
        celular_contato=dados.get('celular_contato'),
    )
    db.session.add(empresa)
    db.session.commit()
    return empresa



def vincular_bu_empresa(empresa, bu, acao, current_user):
    """Vincula um BU à empresa (venda) ou prepara indicação. Retorna (empresa, etapa)."""
    if acao == 'vender':
        bu_obj = _get_or_create(BusinessUnit, bu)
        if bu_obj not in empresa.business_units:
            empresa.business_units.append(bu_obj)
        empresa.is_client = True
        empresa.responsavel_id = current_user.id
        db.session.commit()
        return empresa, 'venda_concluida'
    return empresa, 'indicacao'



def criar_indicacao(empresa_id, usuario_id, bu, produtos, dados):
    """Cria uma indicação após verificar duplicidade. Retorna a indicação."""
    empresa = db.session.get(Empresa, empresa_id)
    produtos_lista = produtos or []
    duplicados = verificar_duplicidade(empresa.cnpj, produtos_lista)
    if duplicados:
        raise ValueError(
            f'Produtos já indicados recentemente (últimos 3 meses): {", ".join(duplicados)}'
        )

    indicacao = Indicacao(
        empresa_id=empresa_id,
        usuario_id=usuario_id,
        bu_indicado=bu,
        quantidade_caminhoes=dados.get('quantidade_caminhoes'),
        quantidade_funcionarios=dados.get('quantidade_funcionarios'),
        quantidade_veiculos_pesados=dados.get('quantidade_veiculos_pesados'),
        subsidia_combustivel=dados.get('subsidia_combustivel'),
        quantidade_veiculos_leves=dados.get('quantidade_veiculos_leves'),
        quantidade_veiculos=dados.get('quantidade_veiculos'),
        previsao_volume=dados.get('previsao_volume'),
        quantidade_cartoes=dados.get('quantidade_cartoes'),
        observacoes=dados.get('observacoes'),
        status='Pendente',
    )
    indicacao.produtos = [_get_or_create(Produto, nome) for nome in produtos_lista]
    db.session.add(indicacao)
    db.session.commit()
    return indicacao



def verificar_duplicidade(cnpj_empresa, produtos, periodo_meses=3):
    """Verifica se já existe indicação para o mesmo CNPJ e produtos dentro do período."""
    data_limite = datetime.now(timezone.utc) - timedelta(days=periodo_meses * 30)
    indicacoes_recentes = Indicacao.query.join(Empresa).filter(
        Empresa.cnpj == cnpj_empresa,
        Indicacao.data_indicacao >= data_limite,
    ).all()

    produtos_buscados = set(produtos)
    duplicados = set()
    for indicacao in indicacoes_recentes:
        duplicados.update(produtos_buscados & set(indicacao.produtos_lista))
    return sorted(duplicados)



# --- Consulta / Dashboard ---

def listar_clientes(pesquisa=''):
    """Lista empresas cliente (com responsável + contagem de pendências)."""
    query = Empresa.query.filter_by(is_client=True)

    if pesquisa:
        query = query.filter(
            (Empresa.razao_social.contains(pesquisa))
            | (Empresa.cnpj.contains(pesquisa))
            | (Empresa.municipio.contains(pesquisa))
            | (Empresa.responsavel.has(Usuario.nome.contains(pesquisa)))
        )

    clientes = query.options(db.joinedload(Empresa.responsavel)).order_by(Empresa.razao_social).all()

    pendentes_map = dict(
        db.session.query(Indicacao.empresa_id, sa.func.count(Indicacao.id))
        .filter_by(status='Pendente')
        .group_by(Indicacao.empresa_id)
        .all()
    )
    for cliente in clientes:
        cliente.indicacoes_pendentes = pendentes_map.get(cliente.id, 0)
    return clientes


def listar_conversas_do_usuario(usuario_id):
    """Lista conversas do usuário com a última mensagem e contagem de não lidas."""

    conversas = Conversa.query.filter(
        (Conversa.usuario1_id == usuario_id) | (Conversa.usuario2_id == usuario_id)
    ).all()

    resultado = []
    for conversa in conversas:
        outra_id = conversa.usuario2_id if conversa.usuario1_id == usuario_id else conversa.usuario1_id
        ultima = Mensagem.query.filter_by(conversa_id=conversa.id).order_by(Mensagem.data_envio.desc()).first()
        nao_lidas = Mensagem.query.filter(
            Mensagem.conversa_id == conversa.id,
            Mensagem.remetente_id != usuario_id,
            Mensagem.lida == False,  # noqa: E712
        ).count()
        resultado.append({
            'conversa': conversa,
            'outro_usuario': db.session.get(Usuario, outra_id),
            'ultima_mensagem': ultima,
            'nao_lidas': nao_lidas,
        })

    resultado.sort(key=lambda item: item['ultima_mensagem'].data_envio if item['ultima_mensagem'] else item['conversa'].data_criacao, reverse=True)
    return resultado


def listar_outros_usuarios(usuario_id):
    """Lista todos os usuários, exceto o próprio."""
    return Usuario.query.filter(Usuario.id != usuario_id).order_by(Usuario.nome).all()



def contar_metricas(usuario_id):
    """Métricas do dashboard do usuário: minhas indicações, pendentes e clientes."""
    minhas = Indicacao.query.filter_by(usuario_id=usuario_id)
    return {
        'minhas_indicacoes': minhas.count(),
        'minhas_pendentes': minhas.filter_by(status='Pendente').count(),
        'total_clientes': Empresa.query.filter_by(is_client=True).count(),
    }



# --- Comunicação (chat) ---

def enviar_mensagem(conversa_id, remetente_id, texto):
    """Envia uma mensagem em uma conversa. Retorna a mensagem criada."""
    mensagem = Mensagem(
        conversa_id=conversa_id,
        remetente_id=remetente_id,
        mensagem=texto,
    )
    db.session.add(mensagem)
    db.session.commit()
    return mensagem


def listar_mensagens(conversa_id):
    """Lista mensagens de uma conversa ordenadas por envio."""
    return Mensagem.query.filter_by(conversa_id=conversa_id).order_by(Mensagem.data_envio).all()


def marcar_mensagens_lidas(conversa_id, usuario_id):
    """Marca como lidas as mensagens não lidas enviadas por outros usuários."""
    mensagens = Mensagem.query.filter_by(conversa_id=conversa_id).all()
    alterou = False
    for m in mensagens:
        if m.remetente_id != usuario_id and not m.lida:
            m.lida = True
            alterou = True
    if alterou:
        db.session.commit()

    return listar_mensagens(conversa_id)



def criar_conversa(usuario1_id, usuario2_id):
    """Cria uma nova conversa entre dois usuários, se ainda não existir."""
    existente = Conversa.query.filter(
        ((Conversa.usuario1_id == usuario1_id) & (Conversa.usuario2_id == usuario2_id))
        | ((Conversa.usuario1_id == usuario2_id) & (Conversa.usuario2_id == usuario1_id))
    ).first()
    if existente:
        return existente

    nova = Conversa(usuario1_id=usuario1_id, usuario2_id=usuario2_id)
    db.session.add(nova)
    db.session.commit()
    return nova
