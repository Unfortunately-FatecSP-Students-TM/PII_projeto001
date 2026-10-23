# -*- coding: utf-8 -*-
# =============================================================================
#  MODEL — carga inicial (executa uma única vez, quando não há grupos no banco)
#  O prefixo "z_" garante que este arquivo rode depois de db.py e regras.py.
# =============================================================================

USUARIOS_DEMO = [
    # (papel,          nome,           e-mail,                senha)
    ('administrador', 'Administrador', 'admin@loja.com',     'admin123'),
    ('operador',      'Olívia',        'operador@loja.com',  'operador123'),
    ('vendedor',      'Vicente',       'vendedor@loja.com',  'vendedor123'),
    ('cliente',       'Clara',         'cliente@loja.com',   'cliente123'),
]

# (código, nome, categoria, preço, estoque inicial, prazo em dias úteis, descrição)
PRODUTOS_DEMO = [
    ('PRD-10001', 'Camiseta Básica', 'Vestuário', 49.90, 40, 5,
     'Camiseta 100% algodão, malha penteada, disponível em várias cores.'),
    ('PRD-10002', 'Moletom com Capuz', 'Vestuário', 159.90, 15, 7,
     'Moletom flanelado com capuz e bolso canguru. Tamanhos P ao GG.'),
    ('PRD-10003', 'Boné Bordado', 'Vestuário', 59.90, 25, 5,
     'Boné aba curva com ajuste traseiro e bordado frontal.'),
    ('PRD-10004', 'Caneca Térmica 500 ml', 'Acessórios', 89.90, 30, 7,
     'Caneca de aço inox com tampa hermética; mantém a temperatura por 12 horas.'),
    ('PRD-10005', 'Garrafa Squeeze 750 ml', 'Acessórios', 39.90, 50, 5,
     'Garrafa livre de BPA com bico retrátil, ideal para academia.'),
    ('PRD-10006', 'Mochila para Notebook', 'Acessórios', 199.90, 12, 10,
     'Mochila impermeável com compartimento acolchoado para notebook de até 15,6".'),
    ('PRD-10007', 'Mouse Sem Fio', 'Informática', 79.90, 35, 5,
     'Mouse óptico 2.4 GHz com 6 botões e receptor USB nano.'),
    ('PRD-10008', 'Teclado Mecânico Compacto', 'Informática', 349.90, 8, 10,
     'Teclado 65% com switches vermelhos, keycaps PBT e iluminação branca.'),
    ('PRD-10009', 'Headset com Microfone', 'Informática', 229.90, 10, 7,
     'Headset over-ear com microfone removível e cabo de 2 m.'),
    ('PRD-10010', 'Hub USB-C 7 em 1', 'Informática', 189.90, 20, 7,
     'Hub com HDMI 4K, 3 portas USB 3.0, leitor SD/microSD e USB-C PD 100 W.'),
    ('PRD-10011', 'Caderno Pautado 200 folhas', 'Papelaria', 34.90, 60, 5,
     'Caderno universitário capa dura, 10 matérias, papel 70 g/m².'),
    ('PRD-10012', 'Kit de Canetas Coloridas', 'Papelaria', 24.90, 0, 5,
     'Estojo com 12 canetas ponta fina 0,4 mm em cores sortidas.'),
]


def carga_inicial():
    grupos = {}
    for papel in PAPEIS:
        grupos[papel] = auth.add_group(papel, PAPEL_DESCRICAO[papel])

    usuarios = {}
    for papel, nome, email, senha in USUARIOS_DEMO:
        uid = db.auth_user.insert(first_name=nome, last_name='Demo', email=email,
                                  password=db.auth_user.password.validate(senha)[0],
                                  telefone='(11) 99999-0000')
        auth.add_membership(grupos[papel], uid)
        usuarios[papel] = uid
    # o administrador também pode operar e vender
    auth.add_membership(grupos['operador'], usuarios['administrador'])
    auth.add_membership(grupos['vendedor'], usuarios['administrador'])

    categorias = {}
    for nome, desc in [('Vestuário', 'Camisetas, moletons e bonés'),
                       ('Acessórios', 'Canecas, garrafas e mochilas'),
                       ('Informática', 'Periféricos e acessórios para computador'),
                       ('Papelaria', 'Cadernos e materiais de escrita')]:
        categorias[nome] = db.categoria.insert(nome=nome, descricao=desc)

    for codigo, nome, cat, preco, estoque, prazo, desc in PRODUTOS_DEMO:
        imagem = codigo + '.jpg'
        if not os.path.exists(caminho_imagem(imagem)):
            imagem = ''
        pid = db.produto.insert(codigo=codigo, nome=nome, descricao=desc,
                                categoria=categorias[cat], preco=preco, estoque=0,
                                prazo_dias=prazo, imagem=imagem, ativo=True,
                                vendedor=usuarios['vendedor'])
        if estoque:
            registrar_movimento(pid, 'entrada', estoque, motivo='Estoque inicial')
    db.commit()


if db(db.auth_group).isempty():
    carga_inicial()
