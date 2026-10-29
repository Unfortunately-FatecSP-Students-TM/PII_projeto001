# -*- coding: utf-8 -*-
# =============================================================================
#  CONTROLLER admin — painel, usuários e papéis, categorias, conferência de estoque
# =============================================================================


@requer_papel('administrador')
def index():
    n = dict(
        produtos=db(db.produto).count(),
        produtos_sem_estoque=db(db.produto.estoque == 0).count(),
        usuarios=db(db.auth_user).count(),
        pedidos=db(db.pedido).count(),
        aguardando=db(db.pedido.status == 'aguardando_pagamento').count(),
        pagos=db(db.pedido.status.belongs(FLUXO_ENTREGA)).count(),
        cancelados=db(db.pedido.status == 'cancelado').count(),
        pix_pendentes=db(db.pagamento_pix.status.belongs(['gerado', 'informado'])).count(),
        reclamacoes_abertas=db(db.reclamacao.status == 'aberta').count(),
        mensagens_nao_lidas=db((db.mensagem.lida == False) &
                               (db.mensagem.cancelada == False)).count(),
    )
    soma = db.pedido.total.sum()
    n['faturado'] = db(db.pedido.status.belongs(FLUXO_ENTREGA)).select(soma).first()[soma] or 0
    por_papel = dict((papel, 0) for papel in PAPEIS)
    cont = db.auth_membership.id.count()
    for r in db((db.auth_membership.group_id == db.auth_group.id)).select(
            db.auth_group.role, cont, groupby=db.auth_group.role):
        por_papel[r.auth_group.role] = r[cont]
    divergencias = [d for d in conferir_estoque() if d['divergente']]
    return dict(n=n, por_papel=por_papel, divergencias=divergencias)


@requer_papel('administrador')
def usuarios():
    lista = db(db.auth_user).select(orderby=db.auth_user.first_name)
    papeis = {}
    for m in db((db.auth_membership.group_id == db.auth_group.id)).select(
            db.auth_membership.user_id, db.auth_group.role):
        papeis.setdefault(m.auth_membership.user_id, []).append(m.auth_group.role)
    return dict(lista=lista, papeis=papeis)


def _ler_papeis():
    marcados = request.vars.papeis or []
    if not isinstance(marcados, list):
        marcados = [marcados]
    return [p for p in PAPEIS if p in marcados]


@requer_papel('administrador')
def usuario():
    """Cria (sem args) ou edita (args[0]=id) um usuário e seus papéis."""
    u = db.auth_user(request.args(0, cast=int)) if request.args else None
    if request.args and not u:
        avisar('erro', 'Usuário não encontrado.')
        redirect(URL('usuarios'))
    papeis_atuais = sorted(papeis_de(u.id)) if u else ['cliente']
    dados = dict(nome=u.first_name if u else '', sobrenome=u.last_name if u else '',
                 email=u.email if u else '', telefone=u.telefone if u else '',
                 bloqueado=bool(u and u.registration_key))
    erros = {}
    if request.env.request_method == 'POST':
        exigir_post_seguro()
        dados = dict(nome=(request.vars.nome or '').strip(),
                     sobrenome=(request.vars.sobrenome or '').strip(),
                     email=(request.vars.email or '').strip().lower(),
                     telefone=(request.vars.telefone or '').strip(),
                     bloqueado=bool(request.vars.bloqueado))
        papeis_novos = _ler_papeis()
        senha = request.vars.senha or ''
        if not dados['nome']:
            erros['nome'] = 'Informe o nome.'
        if IS_EMAIL()(dados['email'])[1] is not None:
            erros['email'] = 'E-mail inválido.'
        else:
            q = db.auth_user.email == dados['email']
            if u:
                q &= db.auth_user.id != u.id
            if db(q).count():
                erros['email'] = 'E-mail já cadastrado.'
        if dados['telefone'] and not telefone_ok(dados['telefone']):
            erros['telefone'] = 'Telefone inválido.'
        if not papeis_novos:
            erros['papeis'] = 'Marque pelo menos um papel.'
        if (not u or senha) and len(senha) < 6:
            erros['senha'] = 'Senha com pelo menos 6 caracteres.'
        if u and u.id == auth.user_id and 'administrador' not in papeis_novos:
            erros['papeis'] = 'Você não pode remover seu próprio papel de administrador.'
        if u and u.id == auth.user_id and dados['bloqueado']:
            erros['bloqueado'] = 'Você não pode bloquear a própria conta.'
        if not erros:
            campos = dict(first_name=dados['nome'], last_name=dados['sobrenome'],
                          email=dados['email'], telefone=dados['telefone'],
                          registration_key='blocked' if dados['bloqueado'] else '')
            if senha:
                campos['password'] = db.auth_user.password.validate(senha)[0]
            if u:
                u.update_record(**campos)
            else:
                u = db.auth_user[db.auth_user.insert(**campos)]
            # sincroniza os grupos (papéis) com as caixas marcadas
            for papel in PAPEIS:
                gid = auth.id_group(papel)
                if papel in papeis_novos:
                    auth.add_membership(gid, u.id)
                else:
                    auth.del_membership(gid, u.id)
            avisar('ok', 'Usuário %s salvo.' % dados['email'])
            redirect(URL('usuarios'))
        papeis_atuais = papeis_novos
    return dict(u=u, dados=dados, erros=erros, papeis_atuais=papeis_atuais)


@requer_papel('administrador')
def categorias():
    erro = ''
    if request.env.request_method == 'POST':
        exigir_post_seguro()
        acao = request.vars.acao
        if acao == 'nova':
            nome = (request.vars.nome or '').strip()
            if not nome:
                erro = 'Informe o nome da categoria.'
            elif db(db.categoria.nome == nome).count():
                erro = 'Categoria já existe.'
            else:
                db.categoria.insert(nome=nome, descricao=(request.vars.descricao or '').strip())
                avisar('ok', 'Categoria "%s" criada.' % nome)
                redirect(URL('categorias'))
        elif acao == 'excluir':
            c = db.categoria(request.vars.id)
            if c:
                db(db.produto.categoria == c.id).update(categoria=None)
                del db.categoria[c.id]
                avisar('ok', 'Categoria "%s" excluída; produtos ficaram sem categoria.' % c.nome)
            redirect(URL('categorias'))
    cont = db.produto.id.count()
    totais = dict((r.produto.categoria, r[cont]) for r in
                  db(db.produto).select(db.produto.categoria, cont, groupby=db.produto.categoria))
    return dict(categorias=db(db.categoria).select(orderby=db.categoria.nome),
                totais=totais, erro=erro)


@requer_papel('administrador')
def estoque():
    """Conferência: produto.estoque × soma dos movimentos."""
    return dict(conferencia=conferir_estoque())
