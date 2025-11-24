from Edenred import app, db
from flask import render_template, url_for, request, redirect, flash, jsonify
from Edenred.models import Usuario, Empresa, Indicacao
from Edenred.forms import LoginForm, CadastroBasicoForm, BUForm, IndicacaoForm, CadastroUsuarioForm
from flask_login import login_user, logout_user, login_required, current_user


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    
    if form.validate_on_submit():
        login_info = form.usuario_login.data
        senha = form.senha.data
        
        # Buscar usuário por email, telefone ou Skype - MESMA LÓGICA DO MATERIAL
        usuario = Usuario.query.filter(
            (Usuario.email == login_info) | 
            (Usuario.telefone == login_info) | 
            (Usuario.skype == login_info)
        ).first()
        
        # 🔥 VERIFICAÇÃO COM BCRYrypt (igual material de estudo)
        if usuario and usuario.check_senha(senha):
            login_user(usuario)
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login ou senha incorretos!', 'error')
    
    return render_template('login.html', form=form)

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    form = CadastroUsuarioForm()
    
    if form.validate_on_submit():
        try:
            # 🔥 AGORA USA O save() QUE USA BCRYPT (igual material de estudo)
            usuario = form.save()
            
            flash('Cadastro realizado com sucesso! Faça login para continuar.', 'success')
            return redirect(url_for('login'))
        
        except Exception as e:
            db.session.rollback()
            flash('Erro ao cadastrar usuário. Tente novamente.', 'error')
    
    return render_template('cadastro.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@app.route('/home')
@login_required
def home():
    # Contar indicações pendentes do usuário
    minhas_pendencias_count = Indicacao.query.filter_by(
        usuario_id=current_user.id, 
        status='Pendente'
    ).count()
    
    return render_template('home.html', minhas_pendencias=minhas_pendencias_count)
    
@app.route('/portfolio')
@login_required
def portfolio():
    # Catálogo de BU's
    bus = ['Edenred Pay','Ticket Log', 'Ticket Serviços']
    return render_template('portfolio.html', bus=bus)

@app.route('/crosselling', methods=['GET', 'POST'])
@login_required
def crosselling():
    etapa = request.args.get('etapa', 'cnpj')
    
    if etapa == 'cnpj':
        if request.method == 'POST':
            cnpj = request.form.get('cnpj', '').replace('.', '').replace('/', '').replace('-', '')
            
            # QUALQUER 14 dígitos inicia o processo
            if len(cnpj) == 14 and cnpj.isdigit():
                # Verificar se a empresa já existe
                empresa = Empresa.query.filter_by(cnpj=cnpj).first()
                if empresa:
                    flash(f'Empresa {empresa.razao_social} já cadastrada no sistema!', 'info')
                else:
                    flash('CNPJ validado! Prosseguindo para cadastro.', 'success')
                
                # SEMPRE vai para a etapa de decisão, independente se existe ou não
                return redirect(url_for('crosselling', etapa='decisao', cnpj=cnpj))
            else:
                flash('Digite exatamente 14 números para o CNPJ!', 'error')
        
        return render_template('crosselling.html', etapa='cnpj')
    
    elif etapa == 'decisao':
        cnpj = request.args.get('cnpj', '')
        acao = request.args.get('acao', '')
        
        if acao == 'segue':
            # Verificar se a empresa já existe
            empresa_existente = Empresa.query.filter_by(cnpj=cnpj).first()
            if empresa_existente:
                # Se já existe, vai direto para escolha do BU
                return redirect(url_for('crosselling', etapa='bu', empresa_id=empresa_existente.id))
            else:
                # Se não existe, vai para cadastro básico
                return redirect(url_for('crosselling', etapa='cadastro', cnpj=cnpj))
        elif acao == 'corrige':
            return redirect(url_for('crosselling', etapa='cnpj'))
        elif acao == 'cancela':
            flash('Processo cancelado!', 'info')
            return redirect(url_for('home'))
        
        # Buscar empresa para mostrar na tela (quando não há ação ainda)
        empresa = Empresa.query.filter_by(cnpj=cnpj).first()
        return render_template('crosselling.html', etapa='decisao', cnpj=cnpj, empresa=empresa)
    
    elif etapa == 'cadastro':
        form_basico = CadastroBasicoForm()
        cnpj = request.args.get('cnpj', '')
        
        if request.method == 'POST':
            if form_basico.validate_on_submit():
                # 🔥 AGORA É SUPER SIMPLES: apenas chamar .save() no formulário
                empresa = form_basico.save(cnpj)
                
                flash('Cadastro básico salvo com sucesso!', 'success')
                return redirect(url_for('crosselling', etapa='bu', empresa_id=empresa.id))
            else:
                flash('Por favor, corrija os erros no formulário.', 'error')
        
        return render_template('crosselling.html', etapa='cadastro', form_basico=form_basico, cnpj=cnpj)
    
    elif etapa == 'bu':
        form_bu = BUForm()
        empresa_id = request.args.get('empresa_id')
        empresa = Empresa.query.get(empresa_id)
        
        if request.method == 'POST':
            # VALIDAÇÃO MANUAL dos produtos (já que removemos DataRequired)
            produtos_selecionados = request.form.getlist('produtos')
            
            # Verifica se todos os campos obrigatórios estão preenchidos
            if (not form_bu.bu_escolhido.data or 
                not form_bu.acao.data or 
                not produtos_selecionados):
                
                flash('Por favor, preencha todos os campos obrigatórios.', 'error')
                return render_template('crosselling.html', etapa='bu', form_bu=form_bu, empresa=empresa)
            
            # Se chegou aqui, todos os campos estão preenchidos
            produtos_str = ", ".join(produtos_selecionados)
            
            if form_bu.acao.data == 'vender':
                # Marcar empresa como cliente e adicionar BU
                empresa.eh_cliente = True
                if empresa.bus_contratados:
                    empresa.bus_contratados += f", {form_bu.bu_escolhido.data}"
                else:
                    empresa.bus_contratados = form_bu.bu_escolhido.data
                db.session.commit()
                flash(f'Venda concluída com sucesso para a empresa: {empresa.razao_social}', 'success')
                return redirect(url_for('home'))
            else:
                # Redirecionar para indicação
                return redirect(url_for('crosselling', etapa='indicacao', empresa_id=empresa_id, bu=form_bu.bu_escolhido.data, produtos=produtos_str))
        
        return render_template('crosselling.html', etapa='bu', form_bu=form_bu, empresa=empresa)
    
    elif etapa == 'indicacao':
        form_indicacao = IndicacaoForm()
        empresa_id = request.args.get('empresa_id')
        bu = request.args.get('bu')
        produtos = request.args.get('produtos', '')
        empresa = Empresa.query.get(empresa_id)
        
        if request.method == 'POST':
            if form_indicacao.validate_on_submit():
                # Verificação de duplicidade (mantém igual)
                produtos_lista = produtos.split(", ")
                produtos_duplicados = Indicacao.verificar_duplicidade(
                    empresa.cnpj, 
                    produtos_lista
                )
                
                if produtos_duplicados:
                    flash('Indicação bloqueada! Produtos já indicados recentemente (ultimos 3 meses).', 'error')
                    return render_template('crosselling.html', etapa='indicacao', form_indicacao=form_indicacao, empresa=empresa, bu=bu, produtos=produtos)
                
                # 🔥 AGORA É SUPER SIMPLES: apenas chamar .save() no formulário
                form_indicacao.save(empresa_id, current_user.id, bu, produtos)
                
                flash('Solicitação encaminhada com sucesso! Em breve você será informado do parecer da análise. Obrigado!', 'success')
                return redirect(url_for('home'))
            else:
                flash('Por favor, preencha pelo menos a quantidade de cartões.', 'error')
        
        return render_template('crosselling.html', etapa='indicacao', form_indicacao=form_indicacao, empresa=empresa, bu=bu, produtos=produtos)

@app.route('/consulta_clientes')
@login_required
def consulta_clientes():
    pesquisa = request.args.get('pesquisa', '')
        
        # Buscar apenas empresas que são clientes
    query = Empresa.query.filter_by(eh_cliente=True)
        
    if pesquisa:
            query = query.filter(
                (Empresa.razao_social.contains(pesquisa)) |
                (Empresa.cnpj.contains(pesquisa)) |
                (Empresa.municipio.contains(pesquisa))
            )
        
    clientes = query.order_by(Empresa.razao_social).all()
        
        # Adicionar informações de indicações pendentes
    for cliente in clientes:
        indicacoes_pendentes = Indicacao.query.filter_by(
            empresa_id=cliente.id, 
            status='Pendente'
        ).all()
        cliente.indicacoes_pendentes = len(indicacoes_pendentes)
        cliente.bus_list = cliente.bus_contratados.split(', ') if cliente.bus_contratados else []
        
    return render_template('consulta_clientes.html', clientes=clientes, pesquisa=pesquisa)

@app.route('/minhas_pendencias')
@login_required
def minhas_pendencias():
    # Buscar indicações pendentes do usuário atual
    indicacoes = Indicacao.query.filter_by(
        usuario_id=current_user.id, 
        status='Pendente'
    ).order_by(Indicacao.data_indicacao.desc()).all()
    
    return render_template('minhas_pendencias.html', indicacoes=indicacoes)

