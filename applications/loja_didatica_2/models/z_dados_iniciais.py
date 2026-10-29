# -*- coding: utf-8 -*-
# =============================================================================
#  MODEL — carga inicial (executa uma única vez, quando não há grupos no banco)
#  O prefixo "z_" garante que este arquivo rode depois de db.py e regras.py.
# =============================================================================
import re


USUARIOS_DEMO = [
    # (papel,          nome,           e-mail,                senha)
    ('administrador', 'Administrador', 'admin@loja.com',     'admin123'),
    ('operador',      'Olívia',        'operador@loja.com',  'operador123'),
    ('vendedor',      'Vicente',       'vendedor@loja.com',  'vendedor123'),
    ('cliente',       'Clara',         'cliente@loja.com',   'cliente123'),
]

# (código, nome, categoria, preço, estoque inicial, prazo em dias úteis, descrição)
PRODUTOS_DEMO = [
    ('PRD-10001', 'Resident Evil', 'Jogos', 3000.0, 40, 12,
     'Jogo para PlayStation 1, Mídia Física, Original\n'
     'Acompanha o manual\n'
     'Estado: muito bom\n'),
    ('PRD-10002', 'Crash Bandicoot', 'Jogos', 720.0, 0, 6,
     'Jogo para PlayStation 1, Mídia Física, Original\n'
     'Estado: bom\n'),
    ('PRD-10003', 'GTA San Andreas', 'Jogos', 210.0, 2, 5,
     'Jogo para PlayStation 2, Mídia Física, Original\n'
     'Estado: usado\n'),
    ('PRD-10004', 'Resident Evil 4', 'Jogos', 680.0, 1, 5,
     'Jogo para PlayStation 2, Mídia Física, Original\n'
     'Estado: muito bom\n'),
    ('PRD-10005', 'Spider-Man: Shattered Dimensions', 'Jogos', 1200.0, 1, 7,
     'Jogo para PlayStation 3, Mídia Física, Original\n'
     'Estado: quase novo\n'),
    ('PRD-10006', 'Grand Theft Auto V', 'Jogos', 80, 4, 2,
     'Jogo para PlayStation 3, Mídia Física, Original\n'
     'Acompanha mapa e guia do jogo\n'
     'Estado: aceitável\n'),
    ('PRD-10007', 'Ben 10: Protector of Earth', 'Jogos', 1010.1, 10, 10,
     'Jogo para PSP, Mídia Física, Original\n'
     'Estado: muito bom\n'),
    ('PRD-10008', 'God of War: Chains of Olympus', 'Jogos', 440.0, 2, 13,
     'Jogo para PSP, Mídia Física, Original\n'
     'Acompanha manual\n'
     'Estado: bom\n'),
    ('PRD-10009', 'Persona 4 Golden', 'Jogos', 270.0, 1, 9,
     'Jogo para PS Vita, Mídia Física, Original\n'
     'Estado: muito bom\n'),
    ('PRD-10010', 'Rayman Origins', 'Jogos', 90.0, 3, 9,
     'Jogo para PS Vita, Mídia Física, Original\n'
     'Estado: aceitável\n'),
    ('PRD-10011', 'Super Mario Bros.', 'Jogos', 40000.0, 1, 20,
     'Jogo para NES, Mídia Física, Original\n'
     'Estado: novo\n'),
    ('PRD-10012', 'Castlevania', 'Jogos', 520.0, 1, 17,
     'Jogo para NES, Mídia Física, Original\n'
     'Acompanha caixa original e manual\n'
     'Estado: bom\n'),
    ('PRD-10013', 'Super Mario World', 'Jogos', 150.0, 4, 11,
     'Jogo para Super Nintendo, Mídia Física, Original\n'
     'Apenas cartucho, não acompanha caixa\n'
     'Acompanha manual\n'
     'Estado: razoável\n'),
    ('PRD-10014', 'Donkey Kong Country', 'Jogos', 16200.0, 1, 25,
     'Jogo para Super Nintendo, Mídia Física, Original\n'
     'Acompanha cartucho e caixa originais\n'
     'Estado: novo\n'),
    ('PRD-10015', 'Tetris', 'Jogos', 200.0, 7, 6,
     'Jogo para Game Boy, Mídia Física, Original\n'
     'Não acompanha caixa, apenas o cartucho\n'
     'Estado: muito bom\n'),
    ('PRD-10016', 'Pokémon Red', 'Jogos', 2500.0, 1, 18,
     'Jogo para Game Boy, Mídia Física, Original\n'
     'Acompanha caixa, cartucho, berço, encartes e manual originais\n'
     'Estado: bom\n'),
    ('PRD-10017', 'Pokémon Gold', 'Jogos', 1700, 1, 11,
     'Jogo para Game Boy Color, Mídia Física, Original\n'
     'Acompanha caixa e cartucho originais\n'
     'Estado: muito bom\n'),
    ('PRD-10018', 'Legend Of Zelda - Link’s Awakening DX', 'Jogos', 1000, 0, 22,
     'Acompanha caixa, cartucho e manuais originais\n'
     'Estado: bom\n'),
    ('PRD-10019', 'Metroid: Zero Mission', 'Jogos', 800.0, 1, 27,
     'Jogo para Game Boy Advance, Mídia Física, Original, Versão japonesa\n'
     'Acompanha caixa, manual, livretos, DVD/VHS e cartucho originais\n'
     'Estado: muito bom\n'),
    ('PRD-10020', 'Mother 1+2', 'Jogos', 610.0, 2, 12,
     'Jogo para Game Boy Advance, Mídia Física, Original\n'
     'Acompanha caixa, manual e cartucho originais\n'
     'Estado: muito bom\n'),
    ('PRD-10021', 'Lego Batman The Videogame', 'Jogos', 505.0, 1, 2,
     'Jogo para Nintendo DS, Mídia Física, Original\n'
     'Acompanha manual\n'
     'Estado: como novo\n'),
    ('PRD-10022', 'Rhythm Heaven', 'Jogos', 270.0, 1, 8,
     'Jogo para Nintendo DS, Mídia Física, Original\n'
     'Não acompanha manual\n'
     'Estado: aceitável\n'),
    ('PRD-10023', 'Animal Crossing: New Leaf', 'Jogos', 279.99, 9, 21,
     'Jogo para Nintendo 3DS, Mídia Física, Original\n'
     'Estado: Muito Bom\n'),
    ('PRD-10024', 'Super Mario 3D Land', 'Jogos', 219.99, 10, 7,
     'Jogo para Nintendo 3DS, Mídia Física, Original\n'
     'Estado: Aceitável\n'),
    ('PRD-10025', 'Super Mario 64', 'Jogos', 1100.99, 1, 30,
     'Jogo para Nintendo 64, Mídia Física, Original\n'
     'Estado: Semi Novo\n'),
    ('PRD-10026', 'The Legend of Zelda: Ocarina of Time - Edição Colecionador', 'Jogos', 3049.99, 1, 30,
     'Jogo para Nintendo 64, Mídia Física, Original\n'
     'Estado: Semi Novo\n'),
    ('PRD-10027', 'Metroid Prime', 'Jogos', 279.99, 2, 10,
     'Jogo para Gamecube, Mídia Física, Original\n'
     'Estado: Muito Bom\n'),
    ('PRD-10028', 'Super Mario Sunshine', 'Jogos', 259.31, 4, 13,
     'Jogo para Gamecube, Mídia Física, Original\n'
     ' Estado: Aceitável\n'),
    ('PRD-10029', 'Punch Out', 'Jogos', 270.95, 3, 29,
     'Jogo para Wii, Mídia Física, Original\n'
     'Estado: Novo\n'),
    ('PRD-10030', 'Scooby Doo And The Spooky Swamp', 'Jogos', 1000.99, 1, 9,
     'Jogo para Wii, Mídia Física, Original\n'
     'Estado: Aceitável\n'),
    ('PRD-10031', 'Mario Kart 8', 'Jogos', 179.45, 4, 20,
     'Jogo para Wii U, Mídia Física, Original\n'
     'Estado: Novo\n'),
    ('PRD-10032', 'Splatoon', 'Jogos', 150.77, 1, 13,
     'Jogo para Wii U, Mídia Física, Original\n'
     'Estado: Aceitável\n'),
    ('PRD-10033', 'Alex Kidd in Miracle World', 'Jogos', 240.8, 3, 5,
     'Jogo para Master System, Mídia Física, Original\n'
     'Estado: Muito Bom\n'),
    ('PRD-10034', 'Castle of Illusion Starring Mickey Mouse', 'Jogos', 199.99, 1, 18,
     'Jogo para Master System, Mídia Física, Original\n'
     'Estado: Bom\n'),
    ('PRD-10035', 'Sonic the Hedgehog.', 'Jogos', 780.0, 1, 30,
     'Jogo para Sega Genesis, Mídia Física, Original\n'
     'Estado: Aceitável\n'),
    ('PRD-10036', 'Streets of Rage 2', 'Jogos', 695.0, 2, 11,
     'Jogo para Sega Genesis, Mídia Física, Original\n'
     'Estado: Muito Bom\n'),
    ('PRD-10037', 'Crazy Taxi', 'Jogos', 595.0, 1, 29,
     'Jogo para Dreamcast, Mídia Física, Original\n'
     'Estado: Aceitável\n'),
    ('PRD-10038', 'Shenmue', 'Jogos', 490.99, 2, 20,
     'Jogo para Dreamcast, Mídia Física, Original\n'
     'Estado: Aceitável\n'),
    ('PRD-10039', 'Fable', 'Jogos', 200.0, 2, 20,
     'Jogo para XBOX, Mídia Física, Original\n'
     'Estado: Aceitável\n'),
    ('PRD-10040', 'Legacy of Kain: Defiance', 'Jogos', 230.0, 1, 20,
     'Jogo para XBOX, Mídia Física, Original\n'
     'Estado: Muito Bom\n'),
    ('PRD-10041', 'Gears of War', 'Jogos', 200, 5, 11,
     'Jogo para XBOX, Mídia Física, Original\n'
     'Estado: Muito bom\n'),
    ('PRD-10042', 'Halo 3', 'Jogos', 185.0, 4, 3,
     'Jogo para XBOX, Mídia Física, Original\n'
     'Estado: Bom\n'),
    ('PRD-10043', 'Grand Theft Auto IV', 'Jogos', 280.0, 1, 14,
     'Jogo para XBOX 360, Mídia Física, Original\n'
     'Estado: Novo\n'),
    ('PRD-10044', 'Grand Theft Auto V', 'Jogos', 280.0, 15, 15,
     'Jogo para XBOX 360, Mídia Física, Original\n'
     'Estado: Semi Novo\n'),
    ('PRD-10045', 'E.T. the Extra-Terrestrial', 'Jogos', 1500.0, 2, 12,
     'Jogo para Atari 2600, Mídia Física, Original, Lacrado\n'
     'Acompanha caixa e cartucho originais\n'
     'Estado: muito bom\n'),
    ('PRD-10046', 'Pac-Man', 'Jogos', 450.0, 1, 24,
     'Jogo para Atari 2600, Mídia Física, Original\n'
     'Acompanha caixa, cartucho e manual originais\n'
     'Estado: razoável\n'),
]


def plataforma_jogo(codigo, descricao):
    match = re.search(r'Jogo para ([^,\n]+)', descricao, re.IGNORECASE)
    plataforma = match.group(1).strip() if match else (
        'Game Boy Color' if codigo == 'PRD-10018' else '')
    return {'Gamecube': 'GameCube', 'XBOX': 'Xbox', 'XBOX 360': 'Xbox 360'}.get(
        plataforma, plataforma)


def estado_jogo(descricao):
    match = re.search(r'Estado:\s*([^\n]+)', descricao, re.IGNORECASE)
    estado = match.group(1).strip().lower() if match else 'bom'
    if estado in ('novo', 'lacrado'):
        return 'Novo'
    if estado in ('como novo', 'quase novo', 'semi novo'):
        return 'Como novo'
    if estado == 'muito bom':
        return 'Muito bom'
    if estado in ('aceit?vel', 'razo?vel'):
        return 'Aceit?vel'
    return 'Bom'


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
    nome, desc = ('Jogos', 'Jogos clássicos e colecionáveis para consoles de várias gerações.')
    categorias[nome] = db.categoria.insert(nome=nome, descricao=desc)

    for codigo, nome, cat, preco, estoque, prazo, desc in PRODUTOS_DEMO:
        imagem = codigo + '.jpg'
        if not os.path.exists(caminho_imagem(imagem)):
            imagem = ''
        pid = db.produto.insert(codigo=codigo, nome=nome, descricao=desc,
                                categoria=categorias[cat], console=plataforma_jogo(codigo, desc),
                                estado=estado_jogo(desc), preco=preco, estoque=0,
                                prazo_dias=prazo, imagem=imagem, ativo=True,
                                vendedor=usuarios['vendedor'])
        if estoque:
            registrar_movimento(pid, 'entrada', estoque, motivo='Estoque inicial')
    db.commit()


if db(db.auth_group).isempty():
    carga_inicial()
