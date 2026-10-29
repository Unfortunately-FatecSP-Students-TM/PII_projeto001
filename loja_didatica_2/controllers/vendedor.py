# -*- coding: utf-8 -*-
# =============================================================================
#  CONTROLLER vendedor — CRUD de produtos (com upload de imagem), estoque e vendas
#  Vendedores mexem só nos próprios produtos; o administrador, em todos.
# =============================================================================


def _produtos_visiveis():
    """Query dos produtos que este usuário pode administrar."""
    if eh_admin():
        return db.produto.id > 0
    return db.produto.vendedor == auth.user_id


def _meu_produto():
    p = db.produto(request.args(0, cast=int)) if request.args else None
    if not p or not (eh_admin() or p.vendedor == auth.user_id):
        avisar('erro', 'Produto não encontrado.')
        redirect(URL('index'))
    return p


def _converter_preco(texto):
    """Aceita '49,90', '1.234,56' ou '49.90' e devolve float com 2 casas."""
    texto = (texto or '').strip().replace('R$', '').strip()
    if ',' in texto:
        texto = texto.replace('.', '').replace(',', '.')
    return round(float(texto), 2)


def _ler_formulario_produto(p=None):
    """Lê e valida os campos do formulário; devolve (dados, erros)."""
    v = request.vars
    # começa com os textos digitados (para reexibir o formulário em caso de erro)
    dados = dict(nome=(v.nome or '').strip(), descricao=(v.descricao or '').strip(),
                 categoria=v.categoria or None, ativo=bool(v.ativo),
                 preco=(v.preco or '').strip(), prazo_dias=(v.prazo_dias or '').strip(),
                 estoque_inicial=(v.estoque_inicial or '0').strip())
    erros = {}
    if not dados['nome']:
        erros['nome'] = 'Informe o nome do produto.'
    try:
        dados['preco'] = _converter_preco(v.preco)
        if dados['preco'] < 0:
            raise ValueError
    except ValueError:
        erros['preco'] = 'Preço inválido. Ex.: 49,90'
    try:
        dados['prazo_dias'] = int(v.prazo_dias or '')
        if not 1 <= dados['prazo_dias'] <= 365:
            raise ValueError
    except ValueError:
        erros['prazo_dias'] = 'Prazo entre 1 e 365 dias.'
    if p is None:                       # estoque inicial só no cadastro
        try:
            dados['estoque_inicial'] = int(v.estoque_inicial or 0)
            if dados['estoque_inicial'] < 0:
                raise ValueError
        except ValueError:
            erros['estoque_inicial'] = 'Estoque inicial inválido.'
    if dados['categoria'] and not db.categoria(dados['categoria']):
        erros['categoria'] = 'Categoria inválida.'
    return dados, erros


@requer_papel('vendedor')
def index():
    produtos = db(_produtos_visiveis()).select(orderby=db.produto.codigo)
    return dict(produtos=produtos)


@requer_papel('vendedor')
def novo():
    """Cadastro de produto com upload da imagem (multipart/form-data)."""
    response.view = 'vendedor/form.html'
    categorias = db(db.categoria).select(orderby=db.categoria.nome)
    dados, erros = dict(nome='', descricao='', categoria=None, preco='', prazo_dias=5,
                        estoque_inicial=0, ativo=True), {}
    if request.env.request_method == 'POST':
        exigir_post_seguro()
        dados, erros = _ler_formulario_produto()
        envio = arquivo_enviado('imagem')
        if not erros:
            pid = db.produto.insert(codigo=gerar_codigo_produto(), nome=dados['nome'],
                                    descricao=dados['descricao'], categoria=dados['categoria'],
                                    preco=dados['preco'], estoque=0,
                                    prazo_dias=dados['prazo_dias'], ativo=dados['ativo'],
                                    vendedor=auth.user_id)
            p = db.produto[pid]
            if dados['estoque_inicial']:
                registrar_movimento(pid, 'entrada', dados['estoque_inicial'],
                                    motivo='Estoque inicial')
            if envio:
                try:
                    salvar_imagem_produto(p, envio[1])
                except ErroDeNegocio as e:
                    db.commit()             # produto fica salvo, só a imagem falhou
                    avisar('alerta', 'Produto %s cadastrado, mas a imagem foi rejeitada: %s'
                                     % (p.codigo, e))
                    redirect(URL('editar', args=[pid]))
            avisar('ok', 'Produto %s cadastrado.' % p.codigo)
            redirect(URL('index'))
    return dict(p=None, dados=dados, erros=erros, categorias=categorias)


@requer_papel('vendedor')
def editar():
    response.view = 'vendedor/form.html'
    p = _meu_produto()
    categorias = db(db.categoria).select(orderby=db.categoria.nome)
    dados = dict(nome=p.nome, descricao=p.descricao, categoria=p.categoria,
                 preco=('%.2f' % p.preco).replace('.', ','), prazo_dias=p.prazo_dias,
                 ativo=p.ativo)
    erros = {}
    if request.env.request_method == 'POST':
        exigir_post_seguro()
        dados, erros = _ler_formulario_produto(p)
        if not erros:
            p.update_record(nome=dados['nome'], descricao=dados['descricao'],
                            categoria=dados['categoria'], preco=dados['preco'],
                            prazo_dias=dados['prazo_dias'], ativo=dados['ativo'])
            if request.vars.remover_imagem:
                remover_imagem_produto(p)
            envio = arquivo_enviado('imagem')
            if envio:
                try:
                    info = salvar_imagem_produto(p, envio[1])
                    avisar('ok', 'Produto atualizado. Imagem %s de %d×%d convertida para '
                                 'JPEG %d×%d.' % (info['formato'], info['largura'],
                                                  info['altura'], IMAGEM_W, IMAGEM_H))
                except ErroDeNegocio as e:
                    avisar('alerta', 'Dados salvos, mas a imagem foi rejeitada: %s' % e)
                redirect(URL('index'))
            avisar('ok', 'Produto %s atualizado.' % p.codigo)
            redirect(URL('index'))
    return dict(p=p, dados=dados, erros=erros, categorias=categorias)


@requer_papel('vendedor')
def excluir():
    """Só exclui produtos nunca vendidos; os demais podem ser desativados."""
    p = _meu_produto()
    vendas = db(db.pedido_item.produto == p.id).count()
    if request.env.request_method == 'POST':
        exigir_post_seguro()
        if request.vars.acao == 'desativar':
            p.update_record(ativo=False)
            db(db.carrinho_item.produto == p.id).delete()
            avisar('ok', 'Produto %s desativado e removido dos carrinhos.' % p.codigo)
        elif vendas:
            avisar('erro', 'Produto com vendas registradas não pode ser excluído.')
        else:
            remover_imagem_produto(p)
            db(db.carrinho_item.produto == p.id).delete()
            db(db.movimento_estoque.produto == p.id).delete()
            del db.produto[p.id]
            avisar('ok', 'Produto %s excluído.' % p.codigo)
        redirect(URL('index'))
    return dict(p=p, vendas=vendas)


@requer_papel('vendedor')
def estoque():
    """Ajustes de estoque — tabela interativa React <Estoque/> (api/estoque)."""
    return dict()


@requer_papel('vendedor')
def movimentos():
    """Histórico de movimentos de um produto."""
    p = _meu_produto()
    linhas = db(db.movimento_estoque.produto == p.id).select(orderby=~db.movimento_estoque.id)
    return dict(p=p, movimentos=linhas)


@requer_papel('vendedor')
def vendas():
    """Itens vendidos dos produtos deste vendedor (pedidos não cancelados)."""
    linhas = db((db.pedido_item.produto == db.produto.id) &
                (db.pedido_item.pedido == db.pedido.id) &
                (db.pedido.status != 'cancelado') &
                _produtos_visiveis()
                ).select(orderby=~db.pedido.id)
    return dict(linhas=linhas)
