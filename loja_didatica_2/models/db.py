# -*- coding: utf-8 -*-
# =============================================================================
#  MODEL — conexão com o banco (SQLite via DAL), autenticação (Auth) e tabelas
# =============================================================================
#  Este arquivo é executado pelo web2py a cada requisição, antes do controller.
#  Tudo o que for definido aqui (db, auth, funções auxiliares) fica disponível
#  nos controllers e nas views.
# =============================================================================
import os
import re
import json
import uuid
import random
import hashlib
import sqlite3
from decimal import Decimal

from gluon.tools import Auth

# o driver sqlite3 não aceita Decimal como parâmetro; gravamos como número real
sqlite3.register_adapter(Decimal, float)

# -----------------------------------------------------------------------------
# 1. Pastas e conexão
#    RAIZ é a pasta onde está o loja_didatica_2_v2.py: ela contém applications/
#    (esta aplicação), o banco loja.sqlite e a pasta imagens/ dos produtos.
#    request.folder = <RAIZ>/applications/loja_didatica_2/  -> dois níveis acima.
# -----------------------------------------------------------------------------
RAIZ = os.path.abspath(os.path.join(request.folder, os.pardir, os.pardir))
CAMINHO_BANCO = os.path.join(RAIZ, 'loja.sqlite')       # banco ao lado do .py
PASTA_IMAGENS = os.path.join(RAIZ, 'imagens')            # imagens ao lado do .py

# O banco fica em <RAIZ>/loja.sqlite (criado na primeira execução). Com o
# InDBMigrator, os metadados de migração (os arquivos *.table e sql.log que o
# web2py normalmente grava em databases/) ficam dentro do próprio .sqlite, na
# tabela web2py_filesystem: assim a pasta do projeto só tem o arquivo do banco.
# check_reserved=['all'] impede nomes de campo que sejam palavras reservadas
# de SQL (por isso usamos criado_em, data_pedido etc. em vez de "data").
from pydal.migrator import InDBMigrator
db = DAL('sqlite://loja.sqlite', folder=RAIZ,
         adapter_args=dict(migrator=InDBMigrator),
         pool_size=1, check_reserved=['all'], lazy_tables=False)

response.generic_patterns = []          # não expõe views genéricas (.json/.xml)

# -----------------------------------------------------------------------------
# 2. Constantes da loja
# -----------------------------------------------------------------------------
NOME_LOJA = 'Loja Didática 2'

PAPEIS = ['cliente', 'vendedor', 'operador', 'administrador']
PAPEL_DESCRICAO = {
    'cliente':       'Compra produtos, acompanha pedidos, abre reclamações',
    'vendedor':      'Cadastra produtos, envia imagens e controla o estoque',
    'operador':      'Confirma pagamentos PIX, atualiza entregas e atende reclamações',
    'administrador': 'Gerencia usuários, categorias e tem acesso a tudo',
}

STATUS_PEDIDO = ['aguardando_pagamento', 'pago', 'separando', 'enviado',
                 'em_entrega', 'entregue', 'cancelado']
STATUS_PEDIDO_ROTULO = {
    'aguardando_pagamento': 'Aguardando pagamento',
    'pago':                 'Pago',
    'separando':            'Separando o pedido',
    'enviado':              'Entregue à transportadora',
    'em_entrega':           'Em entrega',
    'entregue':             'Entregue',
    'cancelado':            'Cancelado',
}
# depois destes status o cliente não pode mais cancelar
STATUS_SEM_CANCELAMENTO = {'enviado', 'em_entrega', 'entregue', 'cancelado'}
# sequência que o operador percorre na entrega
FLUXO_ENTREGA = ['pago', 'separando', 'enviado', 'em_entrega', 'entregue']

STATUS_PIX = ['gerado', 'informado', 'confirmado', 'recusado']
STATUS_PIX_ROTULO = {
    'gerado':     'QR Code gerado',
    'informado':  'Cliente informou pagamento',
    'confirmado': 'Confirmado pelo operador',
    'recusado':   'Recusado pelo operador',
}

STATUS_RECLAMACAO = ['aberta', 'concluida', 'recusada']
STATUS_RECLAMACAO_ROTULO = {'aberta': 'Aberta', 'concluida': 'Concluída',
                            'recusada': 'Recusada'}

TIPOS_MOVIMENTO = ['entrada', 'saida', 'devolucao', 'ajuste']
TIPO_MOVIMENTO_ROTULO = {'entrada': 'Entrada', 'saida': 'Saída (venda)',
                         'devolucao': 'Devolução (cancelamento)', 'ajuste': 'Ajuste'}

# imagens dos produtos (processadas pelo Pillow no upload, gravadas em PASTA_IMAGENS)
IMAGEM_W, IMAGEM_H = 800, 600            # imagem principal
MINI_W, MINI_H = 400, 300                # miniatura usada em cards e listas
IMAGEM_MAX_BYTES = 5 * 1024 * 1024       # 5 MB
RE_NOME_IMAGEM = re.compile(r'^[A-Za-z0-9_-]{1,40}\.jpg$')   # PRD-10001.jpg / PRD-10001_min.jpg

# -----------------------------------------------------------------------------
# 3. Autenticação — Auth do web2py com grupos usados como papéis
# -----------------------------------------------------------------------------
auth = Auth(db)
auth.settings.extra_fields['auth_user'] = [
    Field('telefone', 'string', length=20, label='Telefone'),
]
auth.settings.password_min_length = 6
auth.define_tables(username=False, signature=False)

auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.expiration = 8 * 3600                      # sessão de 8 horas
auth.settings.login_url = URL('default', 'login')
auth.settings.logout_next = URL('default', 'index')
auth.settings.on_failed_authorization = URL('default', 'sem_permissao')
auth.settings.actions_disabled = ['register', 'retrieve_username',
                                  'request_reset_password', 'reset_password',
                                  'verify_email', 'impersonate', 'groups']

db.auth_user.first_name.label = 'Nome'
db.auth_user.last_name.label = 'Sobrenome'
db.auth_user.email.label = 'E-mail'
db.auth_user.password.label = 'Senha'
db.auth_user.last_name.requires = None            # sobrenome opcional

# -----------------------------------------------------------------------------
# 4. Tabelas da loja
# -----------------------------------------------------------------------------
db.define_table('categoria',
    Field('nome', 'string', length=60, notnull=True, unique=True,
          requires=IS_NOT_EMPTY(), label='Nome'),
    Field('descricao', 'string', length=200, default='', label='Descrição'),
    format='%(nome)s')

db.define_table('produto',
    Field('codigo', 'string', length=12, notnull=True, unique=True, label='Código'),
    Field('nome', 'string', length=120, notnull=True, requires=IS_NOT_EMPTY(), label='Nome'),
    Field('descricao', 'text', default='', label='Descrição'),
    Field('categoria', 'reference categoria', ondelete='SET NULL', label='Categoria'),
    Field('preco', 'decimal(10,2)', notnull=True, default=0,
          requires=IS_DECIMAL_IN_RANGE(0, 999999), label='Preço (R$)'),
    Field('estoque', 'integer', notnull=True, default=0,
          requires=IS_INT_IN_RANGE(0, 1000000), label='Estoque'),
    Field('prazo_dias', 'integer', notnull=True, default=5,
          requires=IS_INT_IN_RANGE(1, 365), label='Prazo de entrega (dias úteis)'),
    Field('imagem', 'string', length=64, default='', label='Imagem'),
    Field('ativo', 'boolean', default=True, label='Ativo no catálogo'),
    Field('vendedor', 'reference auth_user', ondelete='SET NULL', label='Vendedor'),
    Field('criado_em', 'datetime', default=request.now, writable=False),
    Field('atualizado_em', 'datetime', default=request.now, update=request.now,
          writable=False),
    format='%(codigo)s - %(nome)s')

db.define_table('pedido',
    Field('codigo', 'string', length=16, notnull=True, unique=True),      # PED-XXXXXXXX
    Field('codigo_rastreio', 'string', length=20, notnull=True),         # BR..........BR
    Field('cliente', 'reference auth_user', ondelete='SET NULL'),
    Field('total', 'decimal(10,2)', notnull=True, default=0),
    Field('status', 'string', length=24, notnull=True, default='aguardando_pagamento',
          requires=IS_IN_SET(STATUS_PEDIDO)),
    Field('prazo_dias', 'integer', default=5),                           # maior prazo dos itens
    Field('data_pedido', 'datetime', default=request.now),
    Field('data_pagamento', 'datetime'),
    Field('data_cancelamento', 'datetime'),
    Field('observacao', 'text', default=''),
    format='%(codigo)s')

# Itens do pedido guardam nome e preço da época da compra (snapshot)
db.define_table('pedido_item',
    Field('pedido', 'reference pedido', ondelete='CASCADE', notnull=True),
    Field('produto', 'reference produto', ondelete='SET NULL'),
    Field('codigo_produto', 'string', length=12),
    Field('nome_produto', 'string', length=120),
    Field('preco_unitario', 'decimal(10,2)', notnull=True),
    Field('quantidade', 'integer', notnull=True),
    Field('subtotal', 'decimal(10,2)', notnull=True))

# Cada alteração de estoque gera um registro aqui.  A soma das quantidades
# de um produto deve ser sempre igual a produto.estoque (conferência do admin).
db.define_table('movimento_estoque',
    Field('produto', 'reference produto', ondelete='CASCADE', notnull=True),
    Field('tipo', 'string', length=12, notnull=True, requires=IS_IN_SET(TIPOS_MOVIMENTO)),
    Field('quantidade', 'integer', notnull=True),          # positivo entra, negativo sai
    Field('saldo_apos', 'integer', notnull=True),          # estoque após o movimento
    Field('motivo', 'string', length=200, default=''),
    Field('pedido', 'reference pedido', ondelete='SET NULL'),
    Field('usuario', 'reference auth_user', ondelete='SET NULL'),
    Field('criado_em', 'datetime', default=request.now))

# Carrinho persistente: uma linha por (usuário, produto)
db.define_table('carrinho_item',
    Field('usuario', 'reference auth_user', ondelete='CASCADE', notnull=True),
    Field('produto', 'reference produto', ondelete='CASCADE', notnull=True),
    Field('quantidade', 'integer', notnull=True, default=1),
    Field('criado_em', 'datetime', default=request.now))

# Pagamento PIX fictício — um por pedido; aprovado manualmente por um operador
db.define_table('pagamento_pix',
    Field('pedido', 'reference pedido', ondelete='CASCADE', notnull=True, unique=True),
    Field('txid', 'string', length=35, notnull=True, unique=True),
    Field('copia_cola', 'text', notnull=True),                            # payload BR Code
    Field('valor', 'decimal(10,2)', notnull=True),
    Field('status', 'string', length=12, notnull=True, default='gerado',
          requires=IS_IN_SET(STATUS_PIX)),
    Field('criado_em', 'datetime', default=request.now),
    Field('informado_em', 'datetime'),
    Field('decidido_em', 'datetime'),
    Field('operador', 'reference auth_user', ondelete='SET NULL'),
    Field('observacao', 'string', length=200, default=''))

db.define_table('reclamacao',
    Field('pedido', 'reference pedido', ondelete='CASCADE', notnull=True, unique=True),
    Field('cliente', 'reference auth_user', ondelete='SET NULL'),
    Field('texto', 'text', notnull=True),
    Field('status', 'string', length=12, notnull=True, default='aberta',
          requires=IS_IN_SET(STATUS_RECLAMACAO)),
    Field('resposta', 'text', default=''),
    Field('respondida_por', 'reference auth_user', ondelete='SET NULL'),
    Field('criado_em', 'datetime', default=request.now),
    Field('respondida_em', 'datetime'))

db.define_table('mensagem',
    Field('usuario', 'reference auth_user', ondelete='CASCADE', notnull=True),
    Field('texto', 'text', notnull=True),
    Field('lida', 'boolean', default=False),
    Field('cancelada', 'boolean', default=False),
    Field('criado_em', 'datetime', default=request.now))

# -----------------------------------------------------------------------------
# 5. Papéis do usuário logado (consultados no banco a cada requisição, para que
#    mudanças feitas pelo administrador valham sem novo login)
# -----------------------------------------------------------------------------
def papeis_de(usuario_id):
    """Conjunto de papéis (roles dos grupos Auth) de um usuário."""
    if not usuario_id:
        return set()
    linhas = db((db.auth_membership.user_id == usuario_id) &
                (db.auth_membership.group_id == db.auth_group.id)).select(db.auth_group.role)
    return set(l.role for l in linhas)

MEUS_PAPEIS = papeis_de(auth.user_id)

def tem_papel(*papeis):
    """True se o usuário logado tem algum dos papéis informados."""
    return bool(MEUS_PAPEIS.intersection(papeis))

def eh_admin():
    return 'administrador' in MEUS_PAPEIS

def requer_papel(*papeis):
    """Decorator para actions: exige login e um dos papéis (admin passa sempre)."""
    def decorador(acao):
        def protegida(*a, **kw):
            if not auth.user:
                session.proximo = request.url
                avisar('info', 'Entre na sua conta para continuar.')
                redirect(URL('default', 'login'))
            if not (eh_admin() or tem_papel(*papeis)):
                redirect(URL('default', 'sem_permissao'))
            return acao(*a, **kw)
        protegida.__name__ = acao.__name__
        return protegida
    return decorador

def pagina_inicial_do_papel():
    """Para onde mandar o usuário após o login."""
    if eh_admin():                 return URL('admin', 'index')
    if tem_papel('operador'):      return URL('operador', 'index')
    if tem_papel('vendedor'):      return URL('vendedor', 'index')
    return URL('default', 'index')

# -----------------------------------------------------------------------------
# 6. Proteção CSRF simples — o mesmo token vale para formulários HTML
#    (campo oculto _csrf) e para a API JSON usada pelo React (cabeçalho X-CSRF-Token)
# -----------------------------------------------------------------------------
if not session.csrf_token:
    session.csrf_token = uuid.uuid4().hex

def csrf_token():
    return session.csrf_token

def csrf_ok():
    enviado = request.vars._csrf or request.env.http_x_csrf_token
    return bool(enviado) and enviado == session.csrf_token

def exigir_post_seguro():
    """Aborta se a requisição não for POST com token CSRF válido."""
    if request.env.request_method != 'POST':
        raise HTTP(405, 'Método não permitido')
    if not csrf_ok():
        raise HTTP(403, 'Token CSRF inválido — recarregue a página e tente novamente.')

# -----------------------------------------------------------------------------
# 7. Avisos (flash) com tipo: ok / erro / info / alerta
# -----------------------------------------------------------------------------
def avisar(tipo, texto):
    session.aviso = dict(tipo=tipo, texto=texto)

response.aviso = session.aviso
session.aviso = None

# -----------------------------------------------------------------------------
# 8. Utilidades de formatação e geração de códigos
# -----------------------------------------------------------------------------
def moeda(valor):
    """1234.5 -> 'R$ 1.234,50'"""
    valor = float(valor or 0)
    inteiro, centavos = '{:,.2f}'.format(valor).split('.')
    return 'R$ ' + inteiro.replace(',', '.') + ',' + centavos

def data_br(dt, com_hora=True):
    if not dt:
        return '—'
    return dt.strftime('%d/%m/%Y %H:%M' if com_hora else '%d/%m/%Y')

def rotulo_pedido(status):      return STATUS_PEDIDO_ROTULO.get(status, status)
def rotulo_pix(status):         return STATUS_PIX_ROTULO.get(status, status)
def rotulo_reclamacao(status):  return STATUS_RECLAMACAO_ROTULO.get(status, status)

def nome_usuario(u):
    if not u:
        return '—'
    return ('%s %s' % (u.first_name or '', u.last_name or '')).strip() or u.email

RE_TELEFONE = re.compile(r'^[\d\s()\-\+]{8,20}$')

def telefone_ok(t):
    return bool(RE_TELEFONE.match((t or '').strip()))

def gerar_codigo_produto():
    while True:
        cod = 'PRD-%05d' % random.randint(10000, 99999)
        if not db(db.produto.codigo == cod).count():
            return cod

def gerar_codigo_pedido():
    while True:
        cod = 'PED-' + uuid.uuid4().hex[:8].upper()
        if not db(db.pedido.codigo == cod).count():
            return cod

def gerar_codigo_rastreio():
    return 'BR' + uuid.uuid4().hex[:10].upper() + 'BR'

# -----------------------------------------------------------------------------
# 9. Imagens dos produtos — ficam em <RAIZ>/imagens/ (fora de static/), por isso
#    são servidas pela action default/imagem. A URL leva "v=mtime" para furar o
#    cache do navegador quando o vendedor troca a imagem.
# -----------------------------------------------------------------------------
def caminho_imagem(nome_arquivo):
    return os.path.join(PASTA_IMAGENS, nome_arquivo)

def url_imagem(produto, mini=True):
    """URL da imagem (ou da miniatura) de um produto; placeholder se não houver."""
    nome = (produto.imagem or (produto.codigo + '.jpg')) if produto else ''
    if nome:
        if mini:
            nome = nome.replace('.jpg', '_min.jpg')
        caminho = caminho_imagem(nome)
        if os.path.exists(caminho):
            return URL('default', 'imagem', args=[nome],
                       vars=dict(v=int(os.path.getmtime(caminho))))
    return URL('static', 'images/sem-imagem.svg')

# Babel (compila JSX no navegador) só é necessário se algum .jsx for editado;
# os componentes React já vão pré-compilados em static/js/componentes/compilado/.
BABEL_LOCAL = os.path.exists(os.path.join(request.folder, 'static', 'js', 'vendor', 'babel.min.js'))


# -----------------------------------------------------------------------------
# 10. Dados para o JavaScript (window.LOJA) e contadores da barra de navegação
# -----------------------------------------------------------------------------
def contexto_js():
    """JSON injetado pelo layout em window.LOJA — usado por loja.js e pelo React."""
    dados = dict(
        app=request.application,
        base=URL('default', 'index').rsplit('/', 2)[0],
        usuario=dict(logado=bool(auth.user),
                     nome=(auth.user.first_name if auth.user else ''),
                     papeis=sorted(MEUS_PAPEIS)),
        urls=dict(login=URL('default', 'login'), catalogo=URL('default', 'index'),
                  carrinho=URL('cliente', 'carrinho'), pedidos=URL('cliente', 'pedidos')),
    )
    texto = json.dumps(dados, ensure_ascii=False)
    return XML(texto.replace('<', '\\u003c').replace('>', '\\u003e'))


def contadores_nav():
    """Números exibidos nos badges do menu, conforme o papel do usuário."""
    n = dict(carrinho=0, pix=0, reclamacoes=0, mensagens=0)
    if tem_papel('cliente'):
        n['carrinho'] = quantidade_carrinho(auth.user_id)
    if tem_papel('operador', 'administrador'):
        n['pix'] = db(db.pagamento_pix.status.belongs(['gerado', 'informado'])).count()
        n['reclamacoes'] = db(db.reclamacao.status == 'aberta').count()
        n['mensagens'] = db((db.mensagem.lida == False) & (db.mensagem.cancelada == False)).count()
    return n
