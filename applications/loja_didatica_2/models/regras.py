# -*- coding: utf-8 -*-
# =============================================================================
#  MODEL — regras de negócio da loja
#  (estoque, carrinho, pedidos, PIX fictício e processamento de imagens)
# =============================================================================
#  Executado depois de db.py (ordem alfabética dos arquivos em models/).
#  Os controllers só chamam estas funções; nenhuma regra fica na camada web.
# =============================================================================
import io
import os
import base64
from decimal import Decimal


class ErroDeNegocio(Exception):
    """Erro previsto (estoque insuficiente, imagem inválida...) — vira mensagem
    amigável para o usuário, não um ticket de erro do web2py."""


# =============================================================================
#  ESTOQUE — toda alteração passa por registrar_movimento() e fica auditável
# =============================================================================
def registrar_movimento(produto_id, tipo, quantidade, motivo='', pedido_id=None):
    """Altera produto.estoque e grava a linha em movimento_estoque.

    quantidade > 0 entra no estoque; quantidade < 0 sai.
    A saída usa um UPDATE condicional (estoque >= qtd): se nenhuma linha for
    alterada, não havia estoque suficiente — assim duas compras simultâneas
    do último item nunca deixam o estoque negativo.
    """
    quantidade = int(quantidade)
    if quantidade == 0:
        raise ErroDeNegocio('A quantidade do movimento não pode ser zero.')
    if quantidade < 0:
        alteradas = db((db.produto.id == produto_id) &
                       (db.produto.estoque >= -quantidade)
                       ).update(estoque=db.produto.estoque + quantidade)
        if not alteradas:
            produto = db.produto[produto_id]
            raise ErroDeNegocio('Estoque insuficiente para "%s" (disponível: %d).'
                                % (produto.nome if produto else produto_id,
                                   produto.estoque if produto else 0))
    else:
        db(db.produto.id == produto_id).update(estoque=db.produto.estoque + quantidade)
    produto = db.produto[produto_id]
    db.movimento_estoque.insert(produto=produto_id, tipo=tipo, quantidade=quantidade,
                                saldo_apos=produto.estoque, motivo=motivo,
                                pedido=pedido_id, usuario=auth.user_id)
    return produto.estoque


def conferir_estoque():
    """Compara produto.estoque com a soma dos movimentos de cada produto.
    Retorna lista de dicts com o campo 'divergente' para o painel do admin."""
    soma = db.movimento_estoque.quantidade.sum()
    somas = dict((r.movimento_estoque.produto, int(r[soma] or 0))
                 for r in db().select(db.movimento_estoque.produto, soma,
                                      groupby=db.movimento_estoque.produto))
    resultado = []
    for p in db(db.produto).select(orderby=db.produto.codigo):
        movimentado = somas.get(p.id, 0)
        resultado.append(dict(produto=p, movimentado=movimentado,
                              divergente=(movimentado != p.estoque)))
    return resultado


# =============================================================================
#  CARRINHO — persistente por usuário (tabela carrinho_item)
# =============================================================================
def itens_carrinho(usuario_id):
    """Linhas (carrinho_item + produto) do carrinho de um usuário."""
    return db((db.carrinho_item.usuario == usuario_id) &
              (db.carrinho_item.produto == db.produto.id)
              ).select(orderby=db.carrinho_item.id)


def produto_para_json(p):
    """Dicionário serializável de um produto (usado pela API/React)."""
    return dict(id=p.id, codigo=p.codigo, nome=p.nome, descricao=p.descricao or '',
                preco=float(p.preco), preco_fmt=moeda(p.preco), estoque=p.estoque,
                prazo_dias=p.prazo_dias, ativo=bool(p.ativo),
                categoria_id=p.categoria,
                categoria=(p.categoria.nome if p.categoria else ''),
                imagem=url_imagem(p, mini=True), imagem_grande=url_imagem(p, mini=False),
                url=URL('default', 'produto', args=[p.id]))


def resumo_carrinho(usuario_id):
    """Dicionário com itens, total e prazo — é o que o React exibe."""
    itens, total, prazo = [], Decimal('0.00'), 0
    for linha in itens_carrinho(usuario_id):
        item, p = linha.carrinho_item, linha.produto
        subtotal = Decimal(p.preco) * item.quantidade
        total += subtotal
        prazo = max(prazo, p.prazo_dias or 0)
        itens.append(dict(item_id=item.id, produto_id=p.id, codigo=p.codigo, nome=p.nome,
                          preco=float(p.preco), preco_fmt=moeda(p.preco),
                          quantidade=item.quantidade, estoque=p.estoque,
                          subtotal=float(subtotal), subtotal_fmt=moeda(subtotal),
                          imagem=url_imagem(p, mini=True), ativo=bool(p.ativo),
                          url=URL('default', 'produto', args=[p.id])))
    return dict(itens=itens, total=float(total), total_fmt=moeda(total),
                quantidade_total=sum(i['quantidade'] for i in itens),
                prazo_dias=prazo)


def adicionar_ao_carrinho(usuario_id, produto_id, quantidade=1):
    """Adiciona (ou soma) um produto ao carrinho respeitando o estoque."""
    quantidade = int(quantidade)
    produto = db.produto[produto_id]
    if not produto or not produto.ativo:
        raise ErroDeNegocio('Produto indisponível.')
    if quantidade < 1:
        raise ErroDeNegocio('Quantidade inválida.')
    item = db((db.carrinho_item.usuario == usuario_id) &
              (db.carrinho_item.produto == produto_id)).select().first()
    nova = (item.quantidade if item else 0) + quantidade
    if nova > produto.estoque:
        raise ErroDeNegocio('Só há %d unidade(s) de "%s" em estoque.'
                            % (produto.estoque, produto.nome))
    if item:
        item.update_record(quantidade=nova)
    else:
        db.carrinho_item.insert(usuario=usuario_id, produto=produto_id, quantidade=nova)
    return produto


def atualizar_item_carrinho(usuario_id, item_id, quantidade):
    """Define a quantidade de um item (0 remove)."""
    item = db((db.carrinho_item.id == item_id) &
              (db.carrinho_item.usuario == usuario_id)).select().first()
    if not item:
        raise ErroDeNegocio('Item não encontrado no carrinho.')
    quantidade = int(quantidade)
    if quantidade <= 0:
        del db.carrinho_item[item.id]
        return
    produto = db.produto[item.produto]
    if quantidade > produto.estoque:
        raise ErroDeNegocio('Só há %d unidade(s) de "%s" em estoque.'
                            % (produto.estoque, produto.nome))
    item.update_record(quantidade=quantidade)


def remover_item_carrinho(usuario_id, item_id):
    db((db.carrinho_item.id == item_id) & (db.carrinho_item.usuario == usuario_id)).delete()


def limpar_carrinho(usuario_id):
    db(db.carrinho_item.usuario == usuario_id).delete()


def quantidade_carrinho(usuario_id):
    """Total de unidades no carrinho (badge da barra de navegação)."""
    if not usuario_id:
        return 0
    soma = db.carrinho_item.quantidade.sum()
    return int(db(db.carrinho_item.usuario == usuario_id).select(soma).first()[soma] or 0)


# =============================================================================
#  PEDIDO — criação a partir do carrinho, cancelamento e entrega
# =============================================================================
def criar_pedido_do_carrinho(usuario_id):
    """Transforma o carrinho em pedido + itens + PIX, baixando o estoque.

    Tudo acontece em uma única transação: se um produto não tiver estoque,
    db.rollback() desfaz o pedido inteiro e a mensagem volta para o cliente.
    """
    linhas = itens_carrinho(usuario_id)
    if not linhas:
        raise ErroDeNegocio('Seu carrinho está vazio.')
    pedido_id = db.pedido.insert(codigo=gerar_codigo_pedido(),
                                 codigo_rastreio=gerar_codigo_rastreio(),
                                 cliente=usuario_id, total=0,
                                 status='aguardando_pagamento')
    total, prazo = Decimal('0.00'), 0
    try:
        for linha in linhas:
            item, p = linha.carrinho_item, linha.produto
            if not p.ativo:
                raise ErroDeNegocio('"%s" saiu do catálogo. Remova-o do carrinho.' % p.nome)
            registrar_movimento(p.id, 'saida', -item.quantidade,
                                motivo='Venda', pedido_id=pedido_id)
            subtotal = Decimal(p.preco) * item.quantidade
            total += subtotal
            prazo = max(prazo, p.prazo_dias or 0)
            db.pedido_item.insert(pedido=pedido_id, produto=p.id, codigo_produto=p.codigo,
                                  nome_produto=p.nome, preco_unitario=float(p.preco),
                                  quantidade=item.quantidade, subtotal=float(subtotal))
    except ErroDeNegocio:
        db.rollback()            # desfaz pedido, itens e baixas de estoque
        raise
    db(db.pedido.id == pedido_id).update(total=float(total), prazo_dias=prazo)
    criar_pix(db.pedido[pedido_id])
    limpar_carrinho(usuario_id)
    db.commit()
    return pedido_id


def itens_do_pedido(pedido_id):
    return db(db.pedido_item.pedido == pedido_id).select(orderby=db.pedido_item.id)


def pode_cancelar(pedido):
    return pedido.status not in STATUS_SEM_CANCELAMENTO


def cancelar_pedido(pedido, motivo, por_operador=False):
    """Cancela o pedido devolvendo cada item ao estoque (movimento 'devolucao')."""
    if not pode_cancelar(pedido):
        raise ErroDeNegocio('O pedido %s já foi enviado e não pode mais ser cancelado.'
                            % pedido.codigo)
    for item in itens_do_pedido(pedido.id):
        if item.produto and db.produto[item.produto]:
            registrar_movimento(item.produto, 'devolucao', item.quantidade,
                                motivo='Cancelamento do pedido %s' % pedido.codigo,
                                pedido_id=pedido.id)
    pix = db(db.pagamento_pix.pedido == pedido.id).select().first()
    if pix and pix.status in ('gerado', 'informado'):
        pix.update_record(status='recusado', decidido_em=request.now,
                          operador=auth.user_id if por_operador else None,
                          observacao=motivo[:200])
    estorno = pedido.status != 'aguardando_pagamento'
    pedido.update_record(status='cancelado', data_cancelamento=request.now,
                         observacao=motivo)
    db.commit()
    return estorno   # True se já estava pago (aviso de estorno)


def definir_status_entrega(pedido, novo_status):
    """Operador altera a etapa de entrega (só de pedidos pagos)."""
    if novo_status not in FLUXO_ENTREGA:
        raise ErroDeNegocio('Status de entrega inválido.')
    if pedido.status not in FLUXO_ENTREGA:
        raise ErroDeNegocio('Só pedidos pagos podem ter a entrega atualizada.')
    pedido.update_record(status=novo_status)


# =============================================================================
#  PIX FICTÍCIO — payload no padrão BR Code (EMV) com CRC16 real, mas com chave
#  inexistente: nada é cobrado. A aprovação é manual, feita por um operador.
# =============================================================================
CHAVE_PIX_FAKE = 'pagamentos@lojadidatica.fake'


def _campo_emv(identificador, valor):
    """Monta um campo TLV: ID (2) + tamanho (2) + valor."""
    return '%s%02d%s' % (identificador, len(valor), valor)


def crc16_ccitt(texto):
    """CRC-16/CCITT-FALSE (polinômio 0x1021, valor inicial 0xFFFF) em hexa."""
    crc = 0xFFFF
    for byte in texto.encode('utf-8'):
        crc ^= byte << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) if crc & 0x8000 else (crc << 1)
            crc &= 0xFFFF
    return '%04X' % crc


def gerar_copia_cola(txid, valor):
    """Gera o texto "PIX copia e cola" (BR Code) para um valor e um txid."""
    conta = _campo_emv('00', 'br.gov.bcb.pix') + _campo_emv('01', CHAVE_PIX_FAKE)
    adicional = _campo_emv('05', txid)
    payload = (_campo_emv('00', '01') +                     # formato do payload
               _campo_emv('01', '12') +                     # QR dinâmico
               _campo_emv('26', conta) +                    # conta do recebedor
               _campo_emv('52', '0000') +                   # categoria do comerciante
               _campo_emv('53', '986') +                    # moeda: BRL
               _campo_emv('54', '%.2f' % float(valor)) +    # valor
               _campo_emv('58', 'BR') +
               _campo_emv('59', 'LOJA DIDATICA 2') +
               _campo_emv('60', 'SAO PAULO') +
               _campo_emv('62', adicional) +                # txid
               '6304')                                      # CRC (calculado a seguir)
    return payload + crc16_ccitt(payload)


def criar_pix(pedido):
    txid = ('LD2' + pedido.codigo.replace('-', ''))[:25]
    return db.pagamento_pix.insert(pedido=pedido.id, txid=txid, valor=float(pedido.total),
                                   copia_cola=gerar_copia_cola(txid, pedido.total),
                                   status='gerado')


def pix_do_pedido(pedido_id):
    return db(db.pagamento_pix.pedido == pedido_id).select().first()


def qrcode_base64(texto):
    """PNG do QR Code em base64 (data URI). Retorna None se a lib qrcode faltar."""
    try:
        import qrcode
    except ImportError:
        return None
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M,
                       box_size=8, border=2)
    qr.add_data(texto)
    qr.make(fit=True)
    img = qr.make_image(fill_color='#0b2a5b', back_color='white')
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return 'data:image/png;base64,' + base64.b64encode(buffer.getvalue()).decode()


def cliente_informa_pagamento(pix):
    """Cliente clica em "Já paguei": o PIX passa a aguardar o operador."""
    if pix.status != 'gerado':
        raise ErroDeNegocio('Este pagamento já foi informado ou decidido.')
    pix.update_record(status='informado', informado_em=request.now)


def operador_decide_pix(pix, decisao, observacao=''):
    """Aprovação manual: 'confirmar' marca o pedido como pago; 'recusar' cancela
    o pedido e devolve os itens ao estoque."""
    if pix.status not in ('gerado', 'informado'):
        raise ErroDeNegocio('Este PIX já foi decidido (%s).' % rotulo_pix(pix.status))
    pedido = db.pedido[pix.pedido]
    if decisao == 'confirmar':
        pix.update_record(status='confirmado', decidido_em=request.now,
                          operador=auth.user_id, observacao=observacao[:200])
        pedido.update_record(status='pago', data_pagamento=request.now)
    elif decisao == 'recusar':
        cancelar_pedido(pedido, 'PIX recusado pelo operador. ' + observacao, por_operador=True)
        pix.update_record(status='recusado', decidido_em=request.now,
                          operador=auth.user_id, observacao=observacao[:200])
    else:
        raise ErroDeNegocio('Decisão inválida.')
    db.commit()
    return pedido


def listar_pix_pendentes():
    """PIX aguardando decisão, com pedido e cliente (painel do operador)."""
    linhas = db((db.pagamento_pix.status.belongs(['gerado', 'informado'])) &
                (db.pagamento_pix.pedido == db.pedido.id)
                ).select(orderby=~db.pagamento_pix.status | db.pagamento_pix.criado_em)
    saida = []
    for l in linhas:
        pix, pedido = l.pagamento_pix, l.pedido
        cliente = db.auth_user[pedido.cliente] if pedido.cliente else None
        itens = [dict(nome=i.nome_produto, quantidade=i.quantidade,
                      subtotal_fmt=moeda(i.subtotal)) for i in itens_do_pedido(pedido.id)]
        saida.append(dict(pix_id=pix.id, txid=pix.txid, status=pix.status,
                          status_rotulo=rotulo_pix(pix.status),
                          valor=float(pix.valor), valor_fmt=moeda(pix.valor),
                          criado_em=data_br(pix.criado_em),
                          informado_em=data_br(pix.informado_em) if pix.informado_em else None,
                          pedido_id=pedido.id, pedido_codigo=pedido.codigo,
                          cliente=nome_usuario(cliente),
                          cliente_email=cliente.email if cliente else '',
                          itens=itens, url_pedido=URL('operador', 'pedido', args=[pedido.id])))
    return saida


# =============================================================================
#  IMAGENS — upload processado pelo Pillow: valida, corrige orientação EXIF,
#  converte para RGB, recorta/redimensiona para 800×600 e gera miniatura 400×300
# =============================================================================
FORMATOS_ACEITOS = ('JPEG', 'PNG', 'GIF', 'WEBP', 'BMP', 'TIFF')


def processar_imagem(dados):
    """bytes enviados -> (jpeg_principal, jpeg_miniatura, info)."""
    try:
        from PIL import Image, ImageOps
    except ImportError:
        raise ErroDeNegocio('A biblioteca Pillow não está instalada no servidor '
                            '(pip install pillow).')
    if not dados:
        raise ErroDeNegocio('Nenhum arquivo de imagem foi enviado.')
    if len(dados) > IMAGEM_MAX_BYTES:
        raise ErroDeNegocio('A imagem tem mais de 5 MB.')
    try:
        img = Image.open(io.BytesIO(dados))
        formato = img.format
        img.load()
    except Exception:
        raise ErroDeNegocio('O arquivo enviado não é uma imagem válida.')
    if formato not in FORMATOS_ACEITOS:
        raise ErroDeNegocio('Formato %s não aceito. Use: %s.'
                            % (formato, ', '.join(FORMATOS_ACEITOS)))
    info = dict(formato=formato, largura=img.width, altura=img.height)
    img = ImageOps.exif_transpose(img)                   # fotos de celular giradas
    if img.mode in ('RGBA', 'LA', 'P'):                  # transparência -> fundo branco
        img = img.convert('RGBA')
        fundo = Image.new('RGB', img.size, (255, 255, 255))
        fundo.paste(img, mask=img.split()[-1])
        img = fundo
    else:
        img = img.convert('RGB')
    principal = ImageOps.fit(img, (IMAGEM_W, IMAGEM_H), Image.LANCZOS)   # recorte central 4:3
    mini = ImageOps.fit(img, (MINI_W, MINI_H), Image.LANCZOS)

    def jpeg(im):
        buffer = io.BytesIO()
        im.save(buffer, format='JPEG', quality=85, optimize=True, progressive=True)
        return buffer.getvalue()
    return jpeg(principal), jpeg(mini), info


def salvar_imagem_produto(produto, dados):
    """Processa e grava <RAIZ>/imagens/<codigo>.jpg e <codigo>_min.jpg."""
    principal, mini, info = processar_imagem(dados)
    os.makedirs(PASTA_IMAGENS, exist_ok=True)
    nome = produto.codigo + '.jpg'
    with open(caminho_imagem(nome), 'wb') as f:
        f.write(principal)
    with open(caminho_imagem(produto.codigo + '_min.jpg'), 'wb') as f:
        f.write(mini)
    produto.update_record(imagem=nome)
    return info


def remover_imagem_produto(produto):
    for nome in (produto.codigo + '.jpg', produto.codigo + '_min.jpg'):
        caminho = caminho_imagem(nome)
        if os.path.exists(caminho):
            os.remove(caminho)
    produto.update_record(imagem='')


def arquivo_enviado(campo):
    """Retorna (nome, bytes) do upload de um campo do formulário ou None se vazio."""
    arquivo = request.vars.get(campo)
    if isinstance(arquivo, list):
        arquivo = arquivo[0]
    if arquivo is None or not hasattr(arquivo, 'file'):
        return None
    dados = arquivo.file.read()
    return (arquivo.filename, dados) if dados else None
