# -*- coding: utf-8 -*-
# =============================================================================
#  CONTROLLER operador — aprovação manual do PIX, entregas, reclamações, mensagens
# =============================================================================


def _pedido_arg():
    p = db.pedido(request.args(0, cast=int)) if request.args else None
    if not p:
        avisar('erro', 'Pedido não encontrado.')
        redirect(URL('pedidos'))
    return p


@requer_papel('operador')
def index():
    """Painel do operador com contadores."""
    n = dict(
        pix_pendentes=db(db.pagamento_pix.status.belongs(['gerado', 'informado'])).count(),
        pix_informados=db(db.pagamento_pix.status == 'informado').count(),
        em_separacao=db(db.pedido.status.belongs(['pago', 'separando'])).count(),
        em_transporte=db(db.pedido.status.belongs(['enviado', 'em_entrega'])).count(),
        reclamacoes_abertas=db(db.reclamacao.status == 'aberta').count(),
        mensagens_nao_lidas=db((db.mensagem.lida == False) &
                               (db.mensagem.cancelada == False)).count(),
    )
    return dict(n=n)


@requer_papel('operador')
def pix():
    """Fila de pagamentos PIX — componente React <PainelPix/> (api/pix_pendentes)."""
    return dict()


@requer_papel('operador')
def decidir_pix():
    """Versão sem JavaScript da decisão (POST clássico)."""
    exigir_post_seguro()
    pagamento = db.pagamento_pix(request.vars.pix_id)
    if not pagamento:
        avisar('erro', 'Pagamento não encontrado.')
        redirect(URL('pix'))
    try:
        pedido = operador_decide_pix(pagamento, request.vars.decisao,
                                     request.vars.observacao or '')
        avisar('ok', 'PIX do pedido %s: %s.' % (pedido.codigo, rotulo_pix(pagamento.status)))
    except ErroDeNegocio as e:
        avisar('erro', str(e))
    redirect(URL('pix'))


@requer_papel('operador')
def pedidos():
    """Lista de todos os pedidos com filtro por status."""
    filtro = request.vars.status or ''
    query = db.pedido.id > 0
    if filtro in STATUS_PEDIDO:
        query &= db.pedido.status == filtro
    linhas = db(query).select(db.pedido.ALL, db.auth_user.first_name, db.auth_user.last_name,
                              db.auth_user.email,
                              left=db.auth_user.on(db.pedido.cliente == db.auth_user.id),
                              orderby=~db.pedido.id)
    return dict(linhas=linhas, filtro=filtro)


@requer_papel('operador')
def pedido():
    """Detalhe do pedido + formulário de status da entrega."""
    p = _pedido_arg()
    if request.env.request_method == 'POST':
        exigir_post_seguro()
        try:
            if request.vars.acao == 'cancelar':
                cancelar_pedido(p, 'Cancelado pelo operador: %s'
                                % (request.vars.motivo or 'sem motivo informado'),
                                por_operador=True)
                avisar('ok', 'Pedido %s cancelado e estoque devolvido.' % p.codigo)
            else:
                definir_status_entrega(p, request.vars.status)
                avisar('ok', 'Pedido %s agora está em "%s".'
                             % (p.codigo, rotulo_pedido(request.vars.status)))
        except ErroDeNegocio as e:
            avisar('erro', str(e))
        redirect(URL('pedido', args=[p.id]))
    cliente = db.auth_user[p.cliente] if p.cliente else None
    return dict(pedido=p, cliente=cliente, itens=itens_do_pedido(p.id), pix=pix_do_pedido(p.id),
                reclamacao=db(db.reclamacao.pedido == p.id).select().first(),
                movimentos=db(db.movimento_estoque.pedido == p.id).select())


@requer_papel('operador')
def reclamacoes():
    linhas = db((db.reclamacao.pedido == db.pedido.id)).select(
        db.reclamacao.ALL, db.pedido.codigo, db.auth_user.first_name, db.auth_user.email,
        left=db.auth_user.on(db.reclamacao.cliente == db.auth_user.id),
        orderby=db.reclamacao.status | ~db.reclamacao.id)
    return dict(linhas=linhas)


@requer_papel('operador')
def responder():
    r = db.reclamacao(request.args(0, cast=int)) if request.args else None
    if not r:
        avisar('erro', 'Reclamação não encontrada.')
        redirect(URL('reclamacoes'))
    if request.env.request_method == 'POST':
        exigir_post_seguro()
        status = request.vars.status
        if status not in STATUS_RECLAMACAO:
            avisar('erro', 'Status inválido.')
        else:
            r.update_record(status=status, resposta=(request.vars.resposta or '').strip(),
                            respondida_por=auth.user_id, respondida_em=request.now)
            avisar('ok', 'Reclamação atualizada.')
            redirect(URL('reclamacoes'))
    pedido = db.pedido[r.pedido]
    cliente = db.auth_user[r.cliente] if r.cliente else None
    return dict(r=r, pedido=pedido, cliente=cliente)


@requer_papel('operador')
def mensagens():
    """Lista mensagens ativas e marca as não lidas como lidas."""
    db((db.mensagem.lida == False) & (db.mensagem.cancelada == False)).update(lida=True)
    linhas = db((db.mensagem.cancelada == False) &
                (db.mensagem.usuario == db.auth_user.id)).select(orderby=~db.mensagem.id)
    return dict(linhas=linhas)
