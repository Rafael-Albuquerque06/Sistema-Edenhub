import os

from flask import Blueprint, render_template, url_for, request, redirect, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename

from app import db
from app.models import Usuario, Empresa, Indicacao, Conversa, Mensagem
from app.forms import (
    LoginForm,
    CadastroUsuarioForm,
    CadastroBasicoForm,
    BUForm,
    IndicacaoForm,
    MensagemForm,
)
from app.services import (
    criar_usuario,
    criar_empresa,
    vincular_bu_empresa,
    criar_indicacao,
    verificar_duplicidade,
    enviar_mensagem,
    criar_conversa,
    marcar_mensagens_lidas,
)

main_bp = Blueprint('main', __name__)


def _salvar_foto(foto_file):
    """Salva uma foto de upload e retorna o nome seguro do arquivo."""
    if not foto_file or not foto_file.filename:
        return 'default.png'
    nome_seguro = secure_filename(foto_file.filename)
    upload_dir = os.path.join(current_app.root_path, current_app.config['UPLOAD_FILES'], 'img_user')
    os.makedirs(upload_dir, exist_ok=True)
    foto_file.save(os.path.join(upload_dir, nome_seguro))
    return nome_seguro


@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        login_info = form.usuario_login.data
        senha = form.senha.data

        usuario = Usuario.query.filter(
            (Usuario.email == login_info) |
            (Usuario.telefone == login_info) |
            (Usuario.skype == login_info)
        ).first()

        if usuario and usuario.check_senha(senha):
            login_user(usuario)
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('main.home'))
        flash('Login ou senha incorretos!', 'error')
    return render_template('login.html', form=form)


@main_bp.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    form = CadastroUsuarioForm()
    if form.validate_on_submit():
        try:
            dados = form.get_dados()
            dados['foto'] = _salvar_foto(form.foto.data)
            criar_usuario(
                nome=dados['nome'],
                email=dados['email'],
                telefone=dados['telefone'],
                senha=dados['senha'],
                skype=dados['skype'],
                foto=dados['foto'],
            )
            flash('Cadastro realizado com sucesso! Faça login para continuar.', 'success')
            return redirect(url_for('main.login'))
        except ValueError as e:
            db.session.rollback()
            flash(str(e), 'error')
        except Exception:
            db.session.rollback()
            flash('Erro ao cadastrar usuário. Tente novamente.', 'error')
    return render_template('cadastro.html', form=form)


@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))


@main_bp.route('/')
def index():
    """Página pública (landing) — sem login."""
    return render_template('index.html')


@main_bp.route('/health')
def health():
    """Endpoint de diagnóstico para verificar se o banco está acessível."""
    try:
        db.session.execute(db.text('SELECT 1'))
        return {'status': 'ok', 'database': 'conectado'}, 200
    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500


@main_bp.route('/home')
@login_required
def home():
    try:
        minhas_pendencias_count = Indicacao.query.filter_by(
            usuario_id=current_user.id,
            status='Pendente',
        ).count()
    except Exception:
        db.session.rollback()
        minhas_pendencias_count = 0
        flash('Erro ao carregar pendências. Tente novamente.', 'error')
    return render_template('home.html', minhas_pendencias=minhas_pendencias_count)


@main_bp.route('/portfolio')
@login_required
def portfolio():
    bus = ['Edenred Pay', 'Ticket Log', 'Ticket Serviços']
    return render_template('portfolio.html', bus=bus)


@main_bp.route('/crosselling', methods=['GET', 'POST'])
@login_required
def crosselling():
    etapa = request.args.get('etapa', 'cnpj')

    if etapa == 'cnpj':
        if request.method == 'POST':
            cnpj = request.form.get('cnpj', '').replace('.', '').replace('/', '').replace('-', '')
            if len(cnpj) == 14 and cnpj.isdigit():
                empresa = Empresa.query.filter_by(cnpj=cnpj).first()
                if empresa:
                    flash(f'Empresa {empresa.razao_social} já cadastrada no sistema!', 'info')
                else:
                    flash('CNPJ validado! Prosseguindo para cadastro.', 'success')
                return redirect(url_for('main.crosselling', etapa='decisao', cnpj=cnpj))
            flash('Digite exatamente 14 números para o CNPJ!', 'error')
        return render_template('crosselling.html', etapa='cnpj')

    elif etapa == 'decisao':
        cnpj = request.args.get('cnpj', '')
        acao = request.args.get('acao', '')

        if acao == 'segue':
            empresa_existente = Empresa.query.filter_by(cnpj=cnpj).first()
            if empresa_existente:
                return redirect(url_for('main.crosselling', etapa='bu', empresa_id=empresa_existente.id))
            return redirect(url_for('main.crosselling', etapa='cadastro', cnpj=cnpj))
        elif acao == 'corrige':
            return redirect(url_for('main.crosselling', etapa='cnpj'))
        elif acao == 'cancela':
            flash('Processo cancelado!', 'info')
            return redirect(url_for('main.home'))

        empresa = Empresa.query.filter_by(cnpj=cnpj).first()
        if not empresa:
            flash('Empresa não encontrada.', 'error')
            return redirect(url_for('main.crosselling'))
        responsavel_info = None
        if empresa.is_client and empresa.responsavel:
            responsavel_info = {
                'nome': empresa.responsavel.nome,
                'email': empresa.responsavel.email,
                'telefone': empresa.responsavel.telefone,
                'foto': empresa.responsavel.foto,
            }
        return render_template(
            'crosselling.html', etapa='decisao', cnpj=cnpj,
            empresa=empresa, responsavel=responsavel_info,
        )

    elif etapa == 'cadastro':
        form_basico = CadastroBasicoForm()
        cnpj = request.args.get('cnpj', '')
        if request.method == 'POST' and form_basico.validate_on_submit():
            empresa = criar_empresa(cnpj, form_basico.get_dados())
            flash('Cadastro básico salvo com sucesso!', 'success')
            return redirect(url_for('main.crosselling', etapa='bu', empresa_id=empresa.id))
        return render_template(
            'crosselling.html', etapa='cadastro',
            form_basico=form_basico, cnpj=cnpj,
        )

    elif etapa == 'bu':
        form_bu = BUForm()
        empresa_id = request.args.get('empresa_id')
        empresa = Empresa.query.get(empresa_id)

        if not empresa:
            flash('Empresa não encontrada.', 'error')
            return redirect(url_for('main.crosselling'))

        if request.method == 'POST':
            produtos_selecionados = request.form.getlist('produtos')
            if not form_bu.bu_escolhido.data or not form_bu.acao.data or not produtos_selecionados:
                flash('Por favor, preencha todos os campos obrigatórios.', 'error')
                return render_template(
                    'crosselling.html', etapa='bu',
                    form_bu=form_bu, empresa=empresa,
                )

            produtos_str = ', '.join(produtos_selecionados)
            try:
                empresa, etapa_saida = vincular_bu_empresa(
                    empresa, form_bu.bu_escolhido.data, form_bu.acao.data, current_user,
                )
            except Exception:
                db.session.rollback()
                flash('Erro ao processar a venda. Tente novamente.', 'error')
                return render_template(
                    'crosselling.html', etapa='bu',
                    form_bu=form_bu, empresa=empresa,
                )
            if etapa_saida == 'venda_concluida':
                flash(f'Venda concluída com sucesso para a empresa: {empresa.razao_social}', 'success')
                return redirect(url_for('main.home'))
            return redirect(url_for(
                'main.crosselling', etapa='indicacao',
                empresa_id=empresa.id, bu=form_bu.bu_escolhido.data, produtos=produtos_str,
            ))
        return render_template(
            'crosselling.html', etapa='bu',
            form_bu=form_bu, empresa=empresa,
        )

    elif etapa == 'indicacao':
        form_indicacao = IndicacaoForm()
        empresa_id = request.args.get('empresa_id')
        bu = request.args.get('bu')
        produtos = request.args.get('produtos', '')
        empresa = Empresa.query.get(empresa_id) if empresa_id else None

        if not empresa:
            flash('Empresa não encontrada.', 'error')
            return redirect(url_for('main.crosselling'))

        if request.method == 'POST' and form_indicacao.validate_on_submit():
            try:
                criar_indicacao(
                    empresa_id=empresa.id,
                    usuario_id=current_user.id,
                    bu=bu,
                    produtos=produtos,
                    dados=form_indicacao.get_dados(),
                )
                flash(
                    'Solicitação encaminhada com sucesso! '
                    'Em breve você será informado do parecer da análise. Obrigado!',
                    'success',
                )
                return redirect(url_for('main.home'))
            except ValueError as e:
                flash(str(e), 'error')
                return render_template(
                    'crosselling.html', etapa='indicacao',
                    form_indicacao=form_indicacao, empresa=empresa, bu=bu, produtos=produtos,
                )
            except Exception:
                db.session.rollback()
                flash('Erro ao criar indicação. Tente novamente.', 'error')
        return render_template(
            'crosselling.html', etapa='indicacao',
            form_indicacao=form_indicacao, empresa=empresa, bu=bu, produtos=produtos,
        )


@main_bp.route('/consulta_clientes')
@login_required
def consulta_clientes():
    try:
        pesquisa = request.args.get('pesquisa', '')

        query = Empresa.query.filter_by(is_client=True)

        if pesquisa:
            query = query.filter(
                (Empresa.razao_social.contains(pesquisa)) |
                (Empresa.cnpj.contains(pesquisa)) |
                (Empresa.municipio.contains(pesquisa)) |
                (Empresa.responsavel.has(Usuario.nome.contains(pesquisa)))
            )

        # Eager load para evitar N+1 no responsável
        clientes = query.options(db.joinedload(Empresa.responsavel)).order_by(Empresa.razao_social).all()

        # Contar indicações pendentes por empresa (evita N+1 com uma query agregada)
        from sqlalchemy import func
        pendentes_count = (
            db.session.query(Indicacao.empresa_id, func.count(Indicacao.id).label('qtd'))
            .filter_by(status='Pendente')
            .group_by(Indicacao.empresa_id)
            .all()
        )
        pendentes_map = {empresa_id: qtd for empresa_id, qtd in pendentes_count}

        for cliente in clientes:
            cliente.indicacoes_pendentes = pendentes_map.get(cliente.id, 0)

        return render_template(
            'consulta_clientes.html', clientes=clientes, pesquisa=pesquisa,
        )
    except Exception:
        db.session.rollback()
        flash('Erro ao carregar clientes. Tente novamente.', 'error')
        return render_template(
            'consulta_clientes.html', clientes=[], pesquisa=pesquisa,
        )


@main_bp.route('/minhas_pendencias')
@login_required
def minhas_pendencias():
    try:
        indicacoes = Indicacao.query.filter_by(
            usuario_id=current_user.id,
            status='Pendente',
        ).order_by(Indicacao.data_indicacao.desc()).all()
    except Exception:
        db.session.rollback()
        indicacoes = []
        flash('Erro ao carregar pendências. Tente novamente.', 'error')
    return render_template('minhas_pendencias.html', indicacoes=indicacoes)


@main_bp.route('/comunicacao')
@login_required
def comunicacao():
    try:
        conversas = Conversa.query.filter(
            (Conversa.usuario1_id == current_user.id) |
            (Conversa.usuario2_id == current_user.id)
        ).all()
        outros_usuarios = Usuario.query.filter(Usuario.id != current_user.id).all()
    except Exception:
        db.session.rollback()
        conversas = []
        outros_usuarios = []
        flash('Erro ao carregar conversas. Tente novamente.', 'error')
    return render_template(
        'comunicacao.html', conversas=conversas, outros_usuarios=outros_usuarios,
    )


@main_bp.route('/comunicacao/<int:conversa_id>', methods=['GET', 'POST'])
@login_required
def ver_conversa(conversa_id):
    conversa = Conversa.query.get_or_404(conversa_id)
    if current_user.id not in [conversa.usuario1_id, conversa.usuario2_id]:
        flash('Acesso não autorizado!', 'error')
        return redirect(url_for('main.comunicacao'))

    form = MensagemForm()
    if form.validate_on_submit():
        try:
            enviar_mensagem(conversa.id, current_user.id, form.mensagem.data)
            flash('Mensagem enviada!', 'success')
        except Exception:
            db.session.rollback()
            flash('Erro ao enviar mensagem. Tente novamente.', 'error')
        return redirect(url_for('main.ver_conversa', conversa_id=conversa.id))

    try:
        mensagens = marcar_mensagens_lidas(conversa.id, current_user.id)
        mensagens = sorted(mensagens, key=lambda m: m.data_envio)
    except Exception:
        db.session.rollback()
        mensagens = []
        flash('Erro ao carregar mensagens. Tente novamente.', 'error')

    outro_usuario = conversa.usuario2 if conversa.usuario1_id == current_user.id else conversa.usuario1
    return render_template(
        'ver_conversa.html',
        conversa=conversa, mensagens=mensagens,
        outro_usuario=outro_usuario, form=form,
    )


@main_bp.route('/comunicacao/nova/<int:usuario_id>')
@login_required
def nova_conversa(usuario_id):
    usuario_destino = Usuario.query.get_or_404(usuario_id)
    if usuario_destino.id == current_user.id:
        flash('Não é possível iniciar conversa consigo mesmo!', 'error')
        return redirect(url_for('main.comunicacao'))

    conversa = criar_conversa(current_user.id, usuario_id)
    return redirect(url_for('main.ver_conversa', conversa_id=conversa.id))
