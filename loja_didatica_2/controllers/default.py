# -*- coding: utf-8 -*-
# =============================================================================
#  CONTROLLER default — páginas públicas, login/registro e perfil
#  Cada função "def nome():" é uma action acessível em /app/default/nome
# =============================================================================


def index():
    """Catálogo — a grade de produtos é renderizada pelo componente React
    <Catalogo/> (static/js/componentes/catalogo.jsx), que consome api/produtos."""
    categorias = db(db.categoria).select(orderby=db.categoria.nome)
    return dict(categorias=categorias, busca=request.vars.q or '')

def produto():
    """Detalhe de um produto com galeria de imagens."""
    p = db.produto(request.args(0, cast=int)) if request.args else None
    if not p or (not p.ativo and not tem_papel('vendedor', 'operador', 'administrador')):
        avisar('erro', 'Produto não encontrado.')
        redirect(URL('index'))

    # Lista de imagens do produto
    galeria = []

    # Imagem principal cadastrada no banco
    if p.imagem and os.path.isfile(caminho_imagem(p.imagem)):
        galeria.append(p.imagem)

    # Imagens adicionais: PRD-10001_2.jpg, PRD-10001_3.jpg etc.
    numero = 2
    while numero <= 20:
        nome_imagem = '{}_{}.jpg'.format(p.codigo, numero)
        if os.path.isfile(caminho_imagem(nome_imagem)):
            galeria.append(nome_imagem)
        numero += 1
    return dict(
        p=p,
        galeria=galeria,
        no_carrinho=quantidade_carrinho(auth.user_id))    

def sobre():
    """Página que explica a arquitetura do projeto (material de aula)."""
    return dict()

def imagem():
    """Serve as imagens dos produtos, que ficam em <RAIZ>/imagens/ (ao lado do .py),
    fora da pasta static/. Ex.: /default/imagem/PRD-10001_min.jpg?v=123"""
    nome = request.args(0) if request.args else ''
    if not nome or not RE_NOME_IMAGEM.match(nome):
        raise HTTP(404, 'Imagem não encontrada.')
    caminho = caminho_imagem(nome)
    if not os.path.isfile(caminho):
        raise HTTP(404, 'Imagem não encontrada.')
    response.headers['Cache-Control'] = 'public, max-age=86400'
    return response.stream(caminho, chunk_size=64 * 1024, request=request)


# -----------------------------------------------------------------------------
#  Autenticação — formulários próprios usando o Auth do web2py por baixo
# -----------------------------------------------------------------------------
def login():
    if auth.user:
        redirect(pagina_inicial_do_papel())
    erro = ''
    if request.env.request_method == 'POST':
        exigir_post_seguro()
        email = (request.vars.email or '').strip().lower()
        senha = request.vars.senha or ''
        usuario = auth.login_bare(email, senha) if email and senha else None
        if usuario:
            MEUS_PAPEIS.update(papeis_de(usuario.id))
            destino = session.proximo or pagina_inicial_do_papel()
            session.proximo = None
            avisar('ok', 'Bem-vindo(a), %s!' % usuario.first_name)
            redirect(destino)
        erro = 'E-mail ou senha incorretos.'
    return dict(erro=erro, email=request.vars.email or '')


def registrar():
    """Autocadastro: cria o usuário no auth_user e o coloca no grupo 'cliente'."""
    if auth.user:
        redirect(URL('index'))
    campos = dict(nome='', sobrenome='', email='', telefone='')
    erros = {}
    if request.env.request_method == 'POST':
        exigir_post_seguro()
        for k in campos:
            campos[k] = (request.vars.get(k) or '').strip()
        senha, senha2 = request.vars.senha or '', request.vars.senha2 or ''
        email2 = (request.vars.email2 or '').strip()
        if not campos['nome']:
            erros['nome'] = 'Informe seu nome.'
        if IS_EMAIL()(campos['email'])[1] is not None:
            erros['email'] = 'E-mail inválido.'
        elif campos['email'].lower() != email2.lower():
            erros['email2'] = 'Os e-mails não coincidem.'
        elif db(db.auth_user.email == campos['email'].lower()).count():
            erros['email'] = 'Já existe uma conta com este e-mail.'
        if not telefone_ok(campos['telefone']):
            erros['telefone'] = 'Telefone inválido. Ex.: (11) 99999-9999'
        if len(senha) < 6:
            erros['senha'] = 'A senha deve ter pelo menos 6 caracteres.'
        elif senha != senha2:
            erros['senha2'] = 'As senhas não coincidem.'
        if not erros:
            uid = db.auth_user.insert(first_name=campos['nome'], last_name=campos['sobrenome'],
                                      email=campos['email'].lower(), telefone=campos['telefone'],
                                      password=db.auth_user.password.validate(senha)[0])
            auth.add_membership(auth.id_group('cliente'), uid)
            auth.login_user(db.auth_user[uid])
            MEUS_PAPEIS.add('cliente')
            avisar('ok', 'Conta criada! Boas compras, %s.' % campos['nome'])
            redirect(URL('index'))
    return dict(campos=campos, erros=erros)


def logout():
    auth.logout_bare()
    session.csrf_token = None
    avisar('info', 'Você saiu da sua conta.')
    redirect(URL('index'))


@auth.requires_login()
def perfil():
    """Edição dos próprios dados; troca de senha opcional."""
    u = db.auth_user[auth.user_id]
    erros = {}
    if request.env.request_method == 'POST':
        exigir_post_seguro()
        nome = (request.vars.nome or '').strip()
        sobrenome = (request.vars.sobrenome or '').strip()
        email = (request.vars.email or '').strip().lower()
        telefone = (request.vars.telefone or '').strip()
        senha, senha2 = request.vars.senha or '', request.vars.senha2 or ''
        if not nome:
            erros['nome'] = 'Informe seu nome.'
        if IS_EMAIL()(email)[1] is not None:
            erros['email'] = 'E-mail inválido.'
        elif db((db.auth_user.email == email) & (db.auth_user.id != u.id)).count():
            erros['email'] = 'Este e-mail já é usado por outra conta.'
        if not telefone_ok(telefone):
            erros['telefone'] = 'Telefone inválido.'
        if senha or senha2:
            if len(senha) < 6:
                erros['senha'] = 'A nova senha deve ter pelo menos 6 caracteres.'
            elif senha != senha2:
                erros['senha2'] = 'As senhas não coincidem.'
        if not erros:
            dados = dict(first_name=nome, last_name=sobrenome, email=email, telefone=telefone)
            if senha:
                dados['password'] = db.auth_user.password.validate(senha)[0]
            u.update_record(**dados)
            auth.user.update(first_name=nome, last_name=sobrenome, email=email,
                             telefone=telefone)
            avisar('ok', 'Dados atualizados.')
            redirect(URL('perfil'))
    return dict(u=u, erros=erros)


def sem_permissao():
    response.status = 403
    return dict()
