import os

from flask import Blueprint, render_template, url_for, request, redirect, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename

from app import db
from app import presence
from app.models import Usuario, Empresa, Indicacao, Conversa
from app.forms import (
    LoginForm,
    CadastroUsuarioForm,
    CadastroBasicoForm,
    BUForm,
    IndicacaoForm,
    MensagemForm,
)
from app.services import (
    autenticar_usuario,
    consultar_empresa_por_cnpj,
    criar_usuario,
    criar_empresa,
    vincular_bu_empresa,
    criar_indicacao,
    enviar_mensagem,
    listar_mensagens,
    marcar_mensagens_lidas,
    criar_conversa,
    listar_conversas_do_usuario,
    listar_outros_usuarios,
    listar_clientes,
    contar_metricas,
    listar_portfolio,
)
from app.api_client import consultar_cnpj, consultar_cep

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
        usuario = autenticar_usuario(form.usuario_login.data, form.senha.data)
        if usuario:
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
        metricas = contar_metricas(current_user.id)
    except Exception:
        db.session.rollback()
        metricas = {'minhas_indicacoes': 0, 'minhas_pendentes': 0, 'total_clientes': 0}
        flash('Erro ao carregar pendências. Tente novamente.', 'error')
    return render_template('home.html', minhas_pendencias=metricas['minhas_pendentes'],
                           minhas_indicacoes=metricas['minhas_indicacoes'],
                           total_clientes=metricas['total_clientes'])


@main_bp.route('/portfolio')
@login_required
def portfolio():
    itens = listar_portfolio()
    return render_template('portfolio.html', itens=itens)


@main_bp.route('/crosselling', methods=['GET', 'POST'])
@login_required
def crosselling():
    etapa = request.args.get('etapa', 'cnpj')

    if etapa == 'cnpj':
        if request.method == 'POST':
            resultado = consultar_empresa_por_cnpj(request.form.get('cnpj', ''))
            if not resultado['valido']:
                flash('Digite um CNPJ válido (14 dígitos com dígitos verificadores corretos)!', 'error')
            else:
                if resultado['empresa']:
                    flash(f"Empresa {resultado['empresa'].razao_social} já cadastrada no sistema!", 'info')
                else:
                    flash('CNPJ validado! Prosseguindo para cadastro.', 'success')
                return redirect(url_for('main.crosselling', etapa='decisao', cnpj=resultado['cnpj']))
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

        resultado = consultar_empresa_por_cnpj(cnpj)
        empresa = resultado['empresa']
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
        cnpj = request.args.get('cnpj', '')
        resultado = consultar_empresa_por_cnpj(cnpj)
        if not resultado['valido']:
            flash('CNPJ inválido.', 'error')
            return redirect(url_for('main.crosselling'))

        form_basico = CadastroBasicoForm()
        # Prefill com ReceitaWS apenas no primeiro GET (falha = formulário manual)
        if request.method == 'GET':
            dados_receita = consultar_cnpj(cnpj) or {}
            dados_receita = {k: v for k, v in dados_receita.items() if k in form_basico._fields and v}
            if dados_receita:
                form_basico = CadastroBasicoForm(data=dados_receita)

        if request.method == 'POST' and form_basico.validate_on_submit():
            empresa = criar_empresa(cnpj, form_basico.get_dados())
            flash('Cadastro básico salvo com sucesso!', 'success')
            return redirect(url_for('main.crosselling', etapa='bu', empresa_id=empresa.id))
        return render_template(
            'crosselling.html', etapa='cadastro',
            form_basico=form_basico, cnpj=cnpj,
        )

    elif etapa == 'bu':
        empresa_id = request.args.get('empresa_id')
        empresa = db.session.get(Empresa, empresa_id)

        if not empresa:
            flash('Empresa não encontrada.', 'error')
            return redirect(url_for('main.crosselling'))

        form_bu = BUForm()

        if request.method == 'POST':
            produtos_selecionados = request.form.getlist('produtos')
            if not produto_form_valido():
                flash('Por favor, preencha todos os campos obrigatórios.', 'error')
                return render_template('crosselling.html', etapa='bu', empresa=empresa, form_bu=form_bu)
            try:
                empresa, etapa_saida = vincular_bu_empresa(
                    empresa, request.form.get('bu_escolhido', ''),
                    request.form.get('acao', ''), current_user,
                )
            except Exception:
                db.session.rollback()
                flash('Erro ao processar a venda. Tente novamente.', 'error')
                return render_template('crosselling.html', etapa='bu', empresa=empresa, form_bu=form_bu)
            if etapa_saida == 'venda_concluida':
                flash(f'Venda concluída com sucesso para a empresa: {empresa.razao_social}', 'success')
                return redirect(url_for('main.home'))
            return redirect(url_for(
                'main.crosselling', etapa='indicacao',
                empresa_id=empresa.id, bu=request.form['bu_escolhido'],
                produtos=', '.join(produtos_selecionados),
            ))
        return render_template('crosselling.html', etapa='bu', empresa=empresa, form_bu=form_bu)

    elif etapa == 'indicacao':
        form_indicacao = IndicacaoForm()
        empresa_id = request.args.get('empresa_id')
        bu = request.args.get('bu')
        produtos_str = request.args.get('produtos', '')
        produtos = [p for p in produtos_str.split(', ') if p]
        empresa = db.session.get(Empresa, empresa_id) if empresa_id else None

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
            except Exception:
                db.session.rollback()
                flash('Erro ao criar indicação. Tente novamente.', 'error')
        return render_template(
            'crosselling.html', etapa='indicacao',
            form_indicacao=form_indicacao, empresa=empresa, bu=bu, produtos=produtos_str,
        )


def produto_form_valido():
    """Valida a etapa BU: BU, ação e produtos obrigatórios."""
    return all([
        request.form.get('bu_escolhido'),
        request.form.get('acao'),
        request.form.getlist('produtos'),
    ])


@main_bp.route('/consulta_clientes')
@login_required
def consulta_clientes():
    pesquisa = request.args.get('pesquisa', '')
    try:
        clientes = listar_clientes(pesquisa)
    except Exception:
        db.session.rollback()
        clientes = []
        flash('Erro ao carregar clientes. Tente novamente.', 'error')
    return render_template('consulta_clientes.html', clientes=clientes, pesquisa=pesquisa)


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
        conversas = listar_conversas_do_usuario(current_user.id)
        outros_usuarios = listar_outros_usuarios(current_user.id)
    except Exception:
        db.session.rollback()
        conversas = []
        outros_usuarios = []
        flash('Erro ao carregar conversas. Tente novamente.', 'error')
    return render_template(
        'comunicacao.html',
        conversas=conversas,
        outros_usuarios=outros_usuarios,
        usuarios_online=presence.ids_online(),
    )


@main_bp.route('/comunicacao/<int:conversa_id>', methods=['GET', 'POST'])
@login_required
def ver_conversa(conversa_id):
    conversa = db.session.get(Conversa, conversa_id)
    if not conversa or current_user.id not in [conversa.usuario1_id, conversa.usuario2_id]:
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
    except Exception:
        db.session.rollback()
        mensagens = []
        flash('Erro ao carregar mensagens. Tente novamente.', 'error')

    outro_usuario_id = (
        conversa.usuario2_id if conversa.usuario1_id == current_user.id else conversa.usuario1_id
    )
    outro_usuario = db.session.get(Usuario, outro_usuario_id)
    if not outro_usuario:
        flash('Usuário da conversa não encontrado.', 'error')
        return redirect(url_for('main.comunicacao'))

    return render_template(
        'ver_conversa.html',
        conversa=conversa, mensagens=mensagens,
        outro_usuario=outro_usuario, form=form,
        outro_online=presence.usuario_online(outro_usuario.id),
    )


@main_bp.route('/comunicacao/nova/<int:usuario_id>')
@login_required
def nova_conversa(usuario_id):
    usuario_destino = db.session.get(Usuario, usuario_id)
    if not usuario_destino:
        flash('Usuário não encontrado.', 'error')
        return redirect(url_for('main.comunicacao'))
    if usuario_destino.id == current_user.id:
        flash('Não é possível iniciar conversa consigo mesmo!', 'error')
        return redirect(url_for('main.comunicacao'))

    conversa = criar_conversa(current_user.id, usuario_id)
    return redirect(url_for('main.ver_conversa', conversa_id=conversa.id))


@main_bp.route('/api/cep/<string:cep>')
@login_required
def api_cep(cep):
    """Retorna endereço (ViaCEP) em JSON para preenchimento automático."""
    dados = consultar_cep(cep)
    if not dados:
        return {'erro': 'CEP não encontrado'}, 404
    return dados, 200
