from app import db
from app.models import Usuario, Empresa, Indicacao, Conversa, Mensagem
from datetime import datetime, timezone, timedelta


def criar_usuario(nome, email, telefone, senha, skype=None, foto='default.png'):
    """Cria e salva um novo usuário. Retorna o usuário ou levanta exceção."""
    if Usuario.query.filter_by(email=email).first():
        raise ValueError('Este email já está cadastrado!')
    if Usuario.query.filter_by(telefone=telefone).first():
        raise ValueError('Este telefone já está cadastrado!')
    if skype and skype.strip():
        if Usuario.query.filter_by(skype=skype).first():
            raise ValueError('Este Skype já está cadastrado!')

    usuario = Usuario(
        nome=nome,
        email=email,
        telefone=telefone,
        skype=skype if skype and skype.strip() else None,
        foto=foto,
    )
    usuario.set_senha(senha)

    db.session.add(usuario)
    db.session.commit()
    return usuario


def criar_empresa(cnpj, dados):
    """Cria e salva uma nova empresa básica. Retorna a empresa."""
    empresa = Empresa(
        cnpj=cnpj,
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
        is_client=False,
        responsavel_id=None,
    )
    db.session.add(empresa)
    db.session.commit()
    return empresa


def vincular_bu_empresa(empresa, bu, acao, current_user):
    """Vincula um BU à empresa (venda) ou prepara indicação. Retorna (empresa, etapa)."""
    if acao == 'vender':
        empresa.is_client = True
        empresa.responsavel_id = current_user.id
        if empresa.contracted_business_units:
            empresa.contracted_business_units += f", {bu}"
        else:
            empresa.contracted_business_units = bu
        db.session.commit()
        return empresa, 'venda_concluida'
    return empresa, 'indicacao'


def criar_indicacao(empresa_id, usuario_id, bu, produtos, dados):
    """Cria uma indicação após verificar duplicidade. Retorna a indicação."""
    produtos_lista = produtos.split(", ") if produtos else []
    duplicados = verificar_duplicidade(Empresa.query.get(empresa_id).cnpj, produtos_lista)
    if duplicados:
        raise ValueError(f'Produtos já indicados recentemente (últimos 3 meses): {", ".join(duplicados)}')

    indicacao = Indicacao(
        empresa_id=empresa_id,
        usuario_id=usuario_id,
        bu_indicado=bu,
        produtos_escolhidos=produtos,
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

    produtos_duplicados = []
    for indicacao in indicacoes_recentes:
        for produto in produtos:
            if produto in (indicacao.produtos_escolhidos or ''):
                produtos_duplicados.append(produto)
    return produtos_duplicados


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


def criar_conversa(usuario1_id, usuario2_id):
    """Cria uma nova conversa entre dois usuários, se ainda não existir."""
    existente = Conversa.query.filter(
        ((Conversa.usuario1_id == usuario1_id) & (Conversa.usuario2_id == usuario2_id)) |
        ((Conversa.usuario1_id == usuario2_id) & (Conversa.usuario2_id == usuario1_id))
    ).first()
    if existente:
        return existente

    nova = Conversa(usuario1_id=usuario1_id, usuario2_id=usuario2_id)
    db.session.add(nova)
    db.session.commit()
    return nova


def marcar_mensagens_lidas(conversa_id, usuario_id):
    """Marca as mensagens não lidas de outros usuários como lidas."""
    mensagens = Mensagem.query.filter_by(conversa_id=conversa_id).all()
    alterou = False
    for m in mensagens:
        if m.remetente_id != usuario_id and not m.lida:
            m.lida = True
            alterou = True
    if alterou:
        db.session.commit()
    return mensagens
