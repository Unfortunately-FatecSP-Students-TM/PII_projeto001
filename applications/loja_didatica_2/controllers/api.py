# -*- coding: utf-8 -*-
# =============================================================================
#  CONTROLLER api — endpoints JSON usados pelos componentes React
#  Leitura: GET.  Escrita: POST com corpo JSON e cabeçalho X-CSRF-Token
#  (o token é o mesmo dos formulários; ver static/js/loja.js -> LojaAPI).
# =============================================================================
import json


def _json(dados, status=200):
    response.status = status
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return json.dumps(dados, ensure_ascii=False)


def _corpo():
    """Corpo JSON da requisição como dict (ou {} se vazio/inválido)."""
    try:
        return json.loads(request.body.read().decode('utf-8') or '{}')
    except ValueError:
        return {}


def _erro(mensagem, status=400):
    return _json(dict(ok=False, erro=mensagem), status)


def _exigir(*papeis):
    """Login + papel + POST seguro (para chamadas que alteram dados)."""
    if not auth.user:
        raise HTTP(401, _json(dict(ok=False, erro='Faça login para continuar.',
                                   login=URL('default', 'login')), 401))
    if papeis and not (eh_admin() or tem_papel(*papeis)):
        raise HTTP(403, _json(dict(ok=False, erro='Sem permissão.'), 403))
    if request.env.request_method == 'POST' and not csrf_ok():
        raise HTTP(403, _json(dict(ok=False, erro='Token CSRF inválido.'), 403))


# -----------------------------------------------------------------------------
#  Catálogo (público)
# -----------------------------------------------------------------------------
def produtos():
    """GET api/produtos?q=texto&categoria=id  -> lista para o <Catalogo/>."""
    query = db.produto.ativo == True
    q = (request.vars.q or '').strip()
    if q:
        padrao = '%' + q + '%'
        query &= (db.produto.nome.ilike(padrao) | db.produto.descricao.ilike(padrao) |
                  db.produto.codigo.ilike(padrao))
    if request.vars.categoria:
        query &= db.produto.categoria == request.vars.categoria
    lista = [produto_para_json(p) for p in db(query).select(orderby=db.produto.nome)]
    categorias = [dict(id=c.id, nome=c.nome) for c in db(db.categoria).select(orderby=db.categoria.nome)]
    return _json(dict(ok=True, produtos=lista, categorias=categorias,
                      logado=bool(auth.user), pode_comprar=tem_papel('cliente'),
                      no_carrinho=quantidade_carrinho(auth.user_id)))


# -----------------------------------------------------------------------------
#  Carrinho (cliente)
# -----------------------------------------------------------------------------
def carrinho():
    _exigir('cliente')
    return _json(dict(ok=True, carrinho=resumo_carrinho(auth.user_id)))


def carrinho_adicionar():
    _exigir('cliente')
    dados = _corpo()
    try:
        p = adicionar_ao_carrinho(auth.user_id, dados.get('produto_id'), dados.get('quantidade', 1))
    except (ErroDeNegocio, ValueError, TypeError) as e:
        return _erro(str(e) or 'Dados inválidos.')
    return _json(dict(ok=True, mensagem='"%s" adicionado ao carrinho.' % p.nome,
                      carrinho=resumo_carrinho(auth.user_id)))


def carrinho_atualizar():
    _exigir('cliente')
    dados = _corpo()
    try:
        atualizar_item_carrinho(auth.user_id, dados.get('item_id'), dados.get('quantidade'))
    except (ErroDeNegocio, ValueError, TypeError) as e:
        return _erro(str(e) or 'Dados inválidos.')
    return _json(dict(ok=True, carrinho=resumo_carrinho(auth.user_id)))


def carrinho_remover():
    _exigir('cliente')
    remover_item_carrinho(auth.user_id, _corpo().get('item_id'))
    return _json(dict(ok=True, carrinho=resumo_carrinho(auth.user_id)))


def carrinho_finalizar():
    """Fecha o pedido; o React redireciona para url_pix."""
    _exigir('cliente')
    try:
        pedido_id = criar_pedido_do_carrinho(auth.user_id)
    except ErroDeNegocio as e:
        return _erro(str(e), 409)
    return _json(dict(ok=True, pedido_id=pedido_id,
                      url_pix=URL('cliente', 'pix', args=[pedido_id])))


def pix_status():
    """GET api/pix_status/<pedido_id> — a tela do PIX consulta a cada 5 s."""
    _exigir('cliente')
    pedido = db.pedido(request.args(0, cast=int)) if request.args else None
    if not pedido or pedido.cliente != auth.user_id:
        return _erro('Pedido não encontrado.', 404)
    pagamento = pix_do_pedido(pedido.id)
    return _json(dict(ok=True, status_pix=pagamento.status if pagamento else None,
                      status_pix_rotulo=rotulo_pix(pagamento.status) if pagamento else '',
                      status_pedido=pedido.status, status_pedido_rotulo=rotulo_pedido(pedido.status),
                      url_pedido=URL('cliente', 'pedido', args=[pedido.id])))


# -----------------------------------------------------------------------------
#  Operador — fila de PIX
# -----------------------------------------------------------------------------
def pix_pendentes():
    _exigir('operador')
    return _json(dict(ok=True, pendentes=listar_pix_pendentes()))


def pix_decidir():
    _exigir('operador')
    dados = _corpo()
    pagamento = db.pagamento_pix(dados.get('pix_id'))
    if not pagamento:
        return _erro('Pagamento não encontrado.', 404)
    try:
        pedido = operador_decide_pix(pagamento, dados.get('decisao'), dados.get('observacao') or '')
    except ErroDeNegocio as e:
        return _erro(str(e), 409)
    return _json(dict(ok=True, mensagem='Pedido %s: %s.' % (pedido.codigo, rotulo_pix(pagamento.status)),
                      pendentes=listar_pix_pendentes()))


# -----------------------------------------------------------------------------
#  Vendedor — estoque
# -----------------------------------------------------------------------------
def _query_estoque():
    return (db.produto.id > 0) if eh_admin() else (db.produto.vendedor == auth.user_id)


def _lista_estoque():
    lista = []
    for p in db(_query_estoque()).select(orderby=db.produto.codigo):
        ultimo = db(db.movimento_estoque.produto == p.id).select(
            orderby=~db.movimento_estoque.id, limitby=(0, 1)).first()
        d = produto_para_json(p)
        d['ultimo_movimento'] = (dict(tipo=TIPO_MOVIMENTO_ROTULO.get(ultimo.tipo, ultimo.tipo),
                                      quantidade=ultimo.quantidade, motivo=ultimo.motivo,
                                      quando=data_br(ultimo.criado_em)) if ultimo else None)
        d['url_movimentos'] = URL('vendedor', 'movimentos', args=[p.id])
        lista.append(d)
    return lista


def estoque():
    _exigir('vendedor')
    return _json(dict(ok=True, produtos=_lista_estoque()))


def estoque_ajustar():
    """POST {produto_id, quantidade (+/-), motivo} — registra entrada/ajuste."""
    _exigir('vendedor')
    dados = _corpo()
    p = db.produto(dados.get('produto_id'))
    if not p or not db(_query_estoque() & (db.produto.id == p.id)).count():
        return _erro('Produto não encontrado.', 404)
    try:
        quantidade = int(dados.get('quantidade'))
        motivo = (dados.get('motivo') or '').strip() or 'Ajuste manual'
        tipo = 'entrada' if quantidade > 0 else 'ajuste'
        saldo = registrar_movimento(p.id, tipo, quantidade, motivo=motivo)
        db.commit()
    except (ErroDeNegocio, ValueError, TypeError) as e:
        return _erro(str(e) or 'Quantidade inválida.', 409)
    return _json(dict(ok=True, mensagem='%s: estoque agora é %d.' % (p.nome, saldo),
                      produtos=_lista_estoque()))
