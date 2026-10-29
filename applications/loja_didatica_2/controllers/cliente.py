# -*- coding: utf-8 -*-
# =============================================================================
#  CONTROLLER cliente — carrinho, checkout, PIX, pedidos, reclamações, mensagens
# =============================================================================


def _meu_pedido():
    """Pedido informado em request.args(0) que pertença ao cliente logado."""
    pedido = db.pedido(request.args(0, cast=int)) if request.args else None
    if not pedido or pedido.cliente != auth.user_id:
        avisar('erro', 'Pedido não encontrado.')
        redirect(URL('pedidos'))
    return pedido


@requer_papel('cliente')
def carrinho():
    """Página do carrinho — o conteúdo é o componente React <Carrinho/>."""
    return dict(resumo=resumo_carrinho(auth.user_id))


@requer_papel('cliente')
def adicionar():
    """Adiciona ao carrinho a partir da página do produto (formulário clássico)."""
    exigir_post_seguro()
    try:
        p = adicionar_ao_carrinho(auth.user_id, request.args(0, cast=int),
                                  request.vars.quantidade or 1)
        avisar('ok', '"%s" adicionado ao carrinho.' % p.nome)
    except (ErroDeNegocio, ValueError) as e:
        avisar('erro', str(e) or 'Quantidade inválida.')
    redirect(URL('default', 'produto', args=[request.args(0)]))


@requer_papel('cliente')
def avaliar_produto():
    """Cria ou atualiza a avaliação de um produto já entregue ao cliente."""
    exigir_post_seguro()
    produto_id = request.args(0, cast=int) if request.args else None
    p = db.produto[produto_id] if produto_id else None
    try:
        nota = int(request.vars.nota or '')
    except (ValueError, TypeError):
        nota = 0
    if not p or not cliente_pode_avaliar(auth.user_id, produto_id):
        avisar('erro', 'Só é possível avaliar produtos de pedidos já entregues.')
    elif not 1 <= nota <= 5:
        avisar('erro', 'Selecione uma nota entre 1 e 5 estrelas.')
    else:
        existente = db((db.avaliacao_produto.produto == produto_id) &
                       (db.avaliacao_produto.cliente == auth.user_id)).select().first()
        if existente:
            existente.update_record(nota=nota, atualizado_em=request.now)
            avisar('ok', 'Sua avaliação foi atualizada.')
        else:
            db.avaliacao_produto.insert(produto=produto_id, cliente=auth.user_id,
                                        nota=nota,
                                        chave='%s:%s' % (auth.user_id, produto_id))
            avisar('ok', 'Obrigado por avaliar este produto!')
    redirect(URL('default', 'produto', args=[produto_id] if p else []))


@requer_papel('cliente')
def desejo_adicionar():
    """Adiciona o produto da página de detalhes à lista de desejos."""
    exigir_post_seguro()
    produto_id = request.args(0, cast=int) if request.args else None
    try:
        produto, criado = adicionar_lista_desejo(auth.user_id, produto_id)
        avisar('ok' if criado else 'info',
               ('"%s" adicionado à sua lista de desejos.' if criado else
                '"%s" já está na sua lista de desejos.') % produto.nome)
    except (ErroDeNegocio, ValueError, TypeError) as e:
        avisar('erro', str(e) or 'Não foi possível adicionar o produto.')
    redirect(URL('default', 'produto', args=[produto_id]))


@requer_papel('cliente')
def desejo_remover():
    """Remove um produto da lista do cliente autenticado."""
    exigir_post_seguro()
    produto_id = request.args(0, cast=int) if request.args else None
    removidos = remover_lista_desejo(auth.user_id, produto_id)
    avisar('info' if removidos else 'erro',
           'Produto removido da sua lista de desejos.' if removidos else
           'Produto não encontrado na sua lista de desejos.')
    redirect(URL('lista_desejo'))


@requer_papel('cliente')
def lista_desejo():
    """Exibe apenas os produtos salvos pelo cliente autenticado."""
    return dict(itens=itens_lista_desejo(auth.user_id))


@requer_papel('cliente')
def checkout():
    """Fecha o pedido a partir do carrinho (POST clássico; a versão React usa
    api/carrinho_finalizar) e redireciona para a tela do PIX."""
    exigir_post_seguro()
    try:
        pedido_id = criar_pedido_do_carrinho(auth.user_id)
    except ErroDeNegocio as e:
        avisar('erro', str(e))
        redirect(URL('carrinho'))
    redirect(URL('pix', args=[pedido_id]))


@requer_papel('cliente')
def pix():
    """Tela de pagamento: QR Code, copia-e-cola e botão "Já paguei"."""
    pedido = _meu_pedido()
    pagamento = pix_do_pedido(pedido.id)
    if not pagamento:
        avisar('erro', 'Este pedido não possui pagamento PIX.')
        redirect(URL('pedidos'))
    return dict(pedido=pedido, pix=pagamento, itens=itens_do_pedido(pedido.id),
                qr=qrcode_base64(pagamento.copia_cola))


@requer_papel('cliente')
def informar_pagamento():
    """Cliente avisa que pagou; o PIX passa a aguardar o operador."""
    exigir_post_seguro()
    pedido = _meu_pedido()
    pagamento = pix_do_pedido(pedido.id)
    try:
        cliente_informa_pagamento(pagamento)
        avisar('ok', 'Pagamento informado. Um operador vai confirmar o recebimento.')
    except ErroDeNegocio as e:
        avisar('erro', str(e))
    redirect(URL('pix', args=[pedido.id]))


@requer_papel('cliente')
def pedidos():
    meus = db(db.pedido.cliente == auth.user_id).select(orderby=~db.pedido.id)
    reclamacoes = dict((r.pedido, r) for r in
                       db(db.reclamacao.cliente == auth.user_id).select())
    return dict(pedidos=meus, reclamacoes=reclamacoes)


@requer_papel('cliente')
def pedido():
    p = _meu_pedido()
    return dict(pedido=p, itens=itens_do_pedido(p.id), pix=pix_do_pedido(p.id),
                reclamacao=db(db.reclamacao.pedido == p.id).select().first())


@requer_papel('cliente')
def cancelar():
    """GET mostra a confirmação; POST cancela e devolve o estoque."""
    p = _meu_pedido()
    if request.env.request_method == 'POST':
        exigir_post_seguro()
        try:
            estorno = cancelar_pedido(p, 'Cancelado pelo cliente.')
            if estorno:
                avisar('ok', 'Pedido %s cancelado. O valor de %s será estornado em até '
                             '5 dias úteis.' % (p.codigo, moeda(p.total)))
            else:
                avisar('ok', 'Pedido %s cancelado. Nenhum valor foi cobrado.' % p.codigo)
        except ErroDeNegocio as e:
            avisar('erro', str(e))
        redirect(URL('pedidos'))
    return dict(pedido=p, itens=itens_do_pedido(p.id))


@requer_papel('cliente')
def reclamacao():
    """Uma reclamação por pedido: GET exibe (ou formulário), POST cria."""
    p = _meu_pedido()
    existente = db(db.reclamacao.pedido == p.id).select().first()
    erro = ''
    if request.env.request_method == 'POST' and not existente:
        exigir_post_seguro()
        texto = (request.vars.texto or '').strip()
        if len(texto) < 10:
            erro = 'Descreva o problema com pelo menos 10 caracteres.'
        else:
            db.reclamacao.insert(pedido=p.id, cliente=auth.user_id, texto=texto)
            avisar('ok', 'Reclamação registrada. Um operador vai analisar.')
            redirect(URL('reclamacao', args=[p.id]))
    return dict(pedido=p, reclamacao=existente, erro=erro)


@requer_papel('cliente')
def mensagens():
    """Mensagens do cliente para a loja (lidas pelos operadores)."""
    erro = ''
    if request.env.request_method == 'POST':
        exigir_post_seguro()
        texto = (request.vars.texto or '').strip()
        if not texto:
            erro = 'Escreva a mensagem antes de enviar.'
        else:
            db.mensagem.insert(usuario=auth.user_id, texto=texto)
            avisar('ok', 'Mensagem enviada.')
            redirect(URL('mensagens'))
    minhas = db(db.mensagem.usuario == auth.user_id).select(orderby=~db.mensagem.id)
    return dict(mensagens=minhas, erro=erro)


@requer_papel('cliente')
def cancelar_mensagem():
    exigir_post_seguro()
    m = db.mensagem(request.args(0, cast=int)) if request.args else None
    if m and m.usuario == auth.user_id and not m.cancelada:
        m.update_record(cancelada=True)
        avisar('info', 'Mensagem cancelada.')
    redirect(URL('mensagens'))
