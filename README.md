# Loja Didática 2 (v2) — MVC com web2py, SQLite, JavaScript e React

Evolução da *Loja Didática* (`loja_web.py`, `http.server` + CSV) para uma aplicação
**web2py** completa, no padrão **MVC**, com **SQLite**, **papéis de usuário**
(cliente, vendedor, operador, administrador), **fake PIX com aprovação manual pelo
operador**, **carrinho e lista de desejos por usuário**, **recuperação de senha por e-mail**,
**upload de imagem processado**, **React** no
front-end e **CSS azul responsivo**. O arquivo `loja_didatica_2_v2.py` extrai a aplicação
web na primeira execução; a pasta `imagens/` acompanha o projeto com as capas dos jogos.

Material didático da disciplina Projeto Integrador em ADS (Fatec São Paulo).
Uso exclusivamente educacional: o PIX é fictício e nada é cobrado.

No cadastro de produtos, vendedores informam o estado (Novo, Como novo, Muito
bom, Bom ou Aceitável) e, quando aplicável, o console. Clientes podem avaliar
produtos de pedidos entregues com notas de 1 a 5 estrelas. O catálogo exibe as
médias e permite filtrar por console, faixa de preço, categoria, avaliação
mínima e estado.

## O que a v2 muda em relação à versão anterior

| | versão anterior | **v2** |
|---|---|---|
| onde a aplicação é gravada | `<web2py>/applications/loja_didatica_2/` | `applications/loja_didatica_2/` **ao lado do .py** |
| banco de dados | `<app>/databases/loja.sqlite` (+ arquivos `*.table`) | **`loja.sqlite` ao lado do .py**, sem arquivos auxiliares (migrações guardadas dentro do banco) |
| imagens dos produtos | pictogramas gerados pelo Pillow em `static/images/produtos/` | **capas de 46 jogos clássicos** em `imagens/` ao lado do `.py`, com miniaturas e imagens adicionais; servidas pela action `default/imagem` |
| React / Babel | React local ou CDN + Babel compilando JSX no navegador | React embutido no .py e **componentes pré-compilados** (`compilado/*.js`): funciona sem internet; Babel só entra se um `.jsx` for editado |
| URL | `http://localhost:8000/loja_didatica_2` | **`http://localhost:8000/`** (routes.py gravado na pasta) |
| web2py e bibliotecas | tinham de ser instalados antes | a **primeira execução verifica e ajusta o ambiente**: cria `venv/` com Pillow e qrcode, baixa o web2py em `./web2py` se não houver e usa a própria pasta como *applications parent* |
| tema | azul-marinho com gradiente escuro nas imagens | cabeçalho com gradiente azul, contrastes revisados (≥ 4,4:1) e catálogo de jogos em imagens com fundo claro |
| plataformas | testado só no Linux | Windows, Linux e macOS: atalhos `iniciar.bat`/`iniciar.sh`, instalação no venv já ativo, console sem UTF-8 tolerado, download sem certificado de CA tolerado, `--diagnostico` |

## Primeira execução: o programa prepara o ambiente sozinho

Basta ter **Python 3.9+** e rodar, na pasta em que colocou o arquivo:

| Sistema | Comando |
|---|---|
| Linux / macOS | `python3 loja_didatica_2_v2.py` — ou `./iniciar.sh` |
| Windows | `py loja_didatica_2_v2.py` — ou clique duplo em `iniciar.bat` |

Os atalhos `iniciar.sh` e `iniciar.bat` (incluídos no pacote e recriados na primeira execução)
procuram um Python 3.9+ que funcione e rodam o programa a partir da pasta do arquivo. Eles
resolvem o caso em que `python` aponta para um ambiente virtual que não existe mais
(`bash: .../bin/python: Arquivo ou diretório inexistente`): nessa situação, digite `deactivate`
e use `python3` (ou `./iniciar.sh`). Se você já estiver em um ambiente virtual seu — por exemplo
`python -m venv .` + `source bin/activate` — as bibliotecas são instaladas **nele**, sem criar
`venv/`. `python3 loja_didatica_2_v2.py --diagnostico` mostra o que o programa vê do ambiente
(Python, venv, git, web2py, internet, porta).

Na primeira vez ele verifica e ajusta tudo **na própria pasta**, nesta ordem:

1. **Python** — exige 3.9 ou superior.
2. **Bibliotecas** — se faltarem Pillow (upload de imagens) ou qrcode (QR Code do PIX), cria o
   ambiente virtual `venv/`, instala as duas com pip e se reexecuta nele. *(No Debian/Ubuntu é
   preciso o pacote `python3-venv`: `sudo apt install python3-venv`.)*
3. **Aplicação e rotas** — extrai `applications/loja_didatica_2/` (MVC) e o `routes.py`
   (a loja responde na raiz do site). As capas, miniaturas e imagens adicionais dos 46 jogos
   ficam na pasta `imagens/` e acompanham o projeto.
4. **web2py** — usa o que encontrar em `./web2py`, `../web2py`, `~/web2py` ou `--web2py DIR`;
   se não houver, baixa em `./web2py` (`git clone --recursive`; sem git, os zips do GitHub de
   web2py, pydal, yatl e rocket3).
5. **Servidor e banco** — inicia o web2py com esta pasta como *applications parent* e faz a
   primeira requisição, que cria e povoa `loja.sqlite` (usuários, categorias, 46 jogos com
   estoque). Ao final mostra `banco de dados OK ... pronto! loja em http://127.0.0.1:8000/`
   e abre o navegador.

Internet é necessária apenas nessa primeira vez (web2py, Pillow, qrcode). Depois disso tudo
roda localmente — React e os componentes já compilados estão embutidos no `.py`.
Sem internet, `--offline` pula os downloads (a loja roda sem upload de imagem/QR Code se as
bibliotecas faltarem, desde que o web2py já esteja ao lado).

### Pasta após a primeira execução

```
<pasta do loja_didatica_2_v2.py>/
├── loja_didatica_2_v2.py          o arquivo único (fonte da verdade)
├── iniciar.sh / iniciar.bat       atalhos (Linux/macOS e Windows)
├── venv/                          ambiente virtual com Pillow e qrcode (criado só se faltarem)
├── web2py/                        o framework (baixado só se não for encontrado)
├── loja.sqlite                    banco de dados, criado e povoado na 1ª execução
├── imagens/                       capas, miniaturas e imagens adicionais dos jogos + uploads
├── routes.py                      faz a loja responder na raiz do site
├── parameters_8000.py             senha do admin do web2py (gerado pelo web2py)
├── httpserver.log / .pid          registros do servidor
└── applications/
    ├── __init__.py
    └── loja_didatica_2/           a aplicação no padrão MVC do web2py
        ├── models/                db.py  regras.py  z_dados_iniciais.py
        ├── controllers/           default.py cliente.py vendedor.py operador.py admin.py api.py
        ├── views/                 layout.html react.html + uma pasta por controller (yatl)
        ├── static/                css/loja.css  js/loja.js  js/componentes/*.jsx (+compilado/*.js)  js/vendor/ (React)  images/
        ├── sessions/ errors/ cache/ uploads/ private/ languages/ modules/ databases/
        └── .extraido.json         manifesto (hash de cada arquivo extraído)
```

### Opções

```bash
python loja_didatica_2_v2.py --web2py C:\web2py   # usa um web2py já existente
python loja_didatica_2_v2.py --rede               # aceita acesso da rede do laboratório (-i 0.0.0.0)
python loja_didatica_2_v2.py --porta 8080 --senha minhasenha
python loja_didatica_2_v2.py --extrair-apenas     # só prepara os arquivos, não inicia o servidor
python loja_didatica_2_v2.py --atualizar          # sobrescreve também os arquivos que você editou
python loja_didatica_2_v2.py --limpar-banco       # apaga loja.sqlite e recria os dados de exemplo
python loja_didatica_2_v2.py --regravar-imagens   # regrava apenas imagens de exemplo inalteradas
python loja_didatica_2_v2.py --offline            # não baixa nada nem cria o venv
python loja_didatica_2_v2.py --sem-venv           # usa o Python atual mesmo sem Pillow/qrcode
python loja_didatica_2_v2.py --babel              # baixa o Babel para editar os .jsx sem internet
python loja_didatica_2_v2.py --sem-navegador      # não abre o navegador
python loja_didatica_2_v2.py --diagnostico        # mostra Python, venv, git, web2py, internet e sai
```

**Editando a aplicação.** Depois da primeira execução, edite os arquivos em
`applications/loja_didatica_2/` normalmente. Nas execuções seguintes o script regrava apenas
os arquivos que você **não** alterou (ele compara com o hash guardado em `.extraido.json`) e
avisa quais foram preservados; `--atualizar` força a versão embutida. Para os componentes React,
edite o `.jsx`: a página percebe que o hash mudou e passa a compilá-lo no navegador com o Babel
(CDN, ou cópia local com `--babel`).

### Recuperação de senha por e-mail

O formulário informa quando o endereço não está cadastrado e envia um link seguro para redefinir
a senha quando a conta existe. Para enviar mensagens, configure o SMTP antes de iniciar a loja.
No PowerShell, por exemplo:

```powershell
$env:LOJA_SMTP_SERVER = "smtp.exemplo.com:587"
$env:LOJA_SMTP_SENDER = "loja@exemplo.com"
$env:LOJA_SMTP_LOGIN = "loja@exemplo.com:sua-senha-de-aplicativo"
$env:LOJA_SMTP_TLS = "true"
$env:LOJA_SMTP_SSL = "false"
py loja_didatica_2_v2.py
```

`LOJA_SMTP_LOGIN` é opcional quando o servidor não exige autenticação. Para SSL direto
(geralmente porta 465), use `LOJA_SMTP_SSL=true` e `LOJA_SMTP_TLS=false`. Mantenha credenciais
fora do código e do controle de versão. Sem SMTP configurado, a loja avisa que não conseguiu
enviar o link em vez de afirmar que a mensagem foi enviada.

### Lista de desejos

Clientes podem salvar produtos na página de detalhes e abrir **Lista de desejos** no menu após
entrar. Os itens ficam persistidos por conta e podem ser removidos da própria lista.

### Contas de demonstração

| Papel | E-mail | Senha |
|---|---|---|
| administrador (também operador e vendedor) | admin@loja.com | admin123 |
| operador | operador@loja.com | operador123 |
| vendedor | vendedor@loja.com | vendedor123 |
| cliente | cliente@loja.com | cliente123 |

Clientes podem se cadastrar sozinhos; operadores, vendedores e administradores são
criados pelo administrador em *Usuários*.

## Roteiro de demonstração em aula

1. **Cliente** entra, busca no catálogo (React), adiciona itens e abre o carrinho
   (quantidades e remoção sem recarregar a página).
2. Clica em *Finalizar e pagar com PIX*: o pedido é criado **em uma única transação**
   (itens com preço "congelado", **baixa de estoque** e PIX). Aparecem o QR Code e o
   código "copia e cola" (BR Code EMV com CRC16 válido, chave inexistente).
3. Clica em *Já paguei*. A tela consulta `api/pix_status` a cada 5 s.
4. **Operador** abre *PIX*: a fila (React) destaca os pagamentos informados; ele
   **confirma** (pedido → pago) ou **recusa** (pedido cancelado e **estoque devolvido**).
   A tela do cliente muda sozinha.
5. Operador avança a entrega (separando → transportadora → em entrega → entregue);
   o cliente acompanha a linha do tempo, abre reclamação e envia mensagens.
6. **Vendedor** cadastra um produto enviando uma foto qualquer (PNG com transparência,
   foto de celular…): o servidor valida, corrige a orientação, recorta para 800×600 e
   gera a miniatura 400×300 em JPEG, gravando em `imagens/`. Ajusta o estoque na tabela
   React; cada ajuste vira um movimento auditável.
7. **Administrador** cria usuários e papéis, bloqueia contas, gerencia categorias e
   confere em *Conferência de estoque* que `produto.estoque` = soma dos movimentos.
8. Salve itens na **Lista de desejos**, que permanece associada à conta mesmo depois de sair e entrar.
9. Abra `loja.sqlite` com o *DB Browser for SQLite* (ou `sqlite3 loja.sqlite`) para
   mostrar as tabelas — o arquivo está ali, ao lado do .py.

## Arquitetura (MVC do web2py)

O web2py executa os arquivos de `models/` a cada requisição (em ordem alfabética, por isso
`z_dados_iniciais.py` vem por último), depois a *action* do controller, que devolve um `dict`
renderizado pela *view* de mesmo nome. Os componentes React chamam `controllers/api.py`, que
devolve JSON — as regras de negócio são as mesmas dos formulários clássicos, porque ficam
todas em `models/regras.py`.

### Decisões de projeto

- **Imagens dos produtos.** O catálogo traz 46 jogos clássicos e suas capas em `imagens/`,
  incluindo miniaturas e imagens adicionais. As capas são arquivos do projeto e não são
  substituídas pelas imagens de exemplo embutidas no `.py`.
- **Tudo na pasta do .py.** `models/db.py` calcula `RAIZ` (dois níveis acima de
  `request.folder`) e usa `<RAIZ>/loja.sqlite` e `<RAIZ>/imagens/`. O lançador inicia o
  web2py no mesmo processo com a pasta do .py como *applications parent* (equivalente a
  `web2py.py -f <pasta>`), de modo que o framework pode estar em qualquer lugar.
- **Banco sem arquivos auxiliares.** `DAL(..., adapter_args=dict(migrator=InDBMigrator))`
  guarda os metadados de migração do pyDAL dentro do próprio `loja.sqlite` (tabela
  `web2py_filesystem`) em vez dos arquivos `*.table` e `sql.log`.
- **Imagens fora de `static/`.** Como `imagens/` não está dentro da aplicação, a action
  `default/imagem/<nome>` valida o nome e entrega o arquivo com `response.stream()`;
  as URLs levam `?v=mtime` para furar o cache ao trocar a imagem.
- **Papéis = grupos do Auth** (`auth_group`/`auth_membership`). Um usuário pode ter vários
  papéis; o administrador passa em qualquer verificação. `requer_papel()` protege as actions
  e os papéis são lidos do banco a cada requisição.
- **Lista de desejos por conta:** `lista_desejo` relaciona o cliente ao produto; a consulta e
  remoção sempre filtram pelo usuário autenticado. O mesmo produto não é duplicado na lista.
- **Recuperação de senha:** o Auth do web2py gera e valida o token de redefinição; o envio real
  usa os dados SMTP configurados em variáveis `LOJA_SMTP_*`.
- **Estoque consistente com as vendas:** toda alteração passa por `registrar_movimento()`,
  que grava `movimento_estoque`. A saída usa `UPDATE produto SET estoque = estoque - qtd
  WHERE id = ? AND estoque >= qtd`; se nenhuma linha for alterada, houve corrida pelo último
  item e o pedido inteiro sofre `rollback`. Cancelamentos devolvem com movimentos de devolução.
- **Fake PIX:** payload BR Code (EMV) com `crc16_ccitt()` real e QR Code gerado pela
  biblioteca `qrcode`. Estados: gerado → informado → confirmado | recusado.
- **Upload:** Pillow valida formato e tamanho (≤ 5 MB), aplica `exif_transpose`, converte
  para RGB (transparência vira fundo branco), recorta com `ImageOps.fit` para 800×600 e
  400×300 e salva em JPEG (qualidade 85).
- **React sem etapa de build para o aluno:** React 18 UMD embutido no .py; os `.jsx`
  (fonte legível) são acompanhados de versões pré-compiladas pelo Babel (preset `react`),
  cujo cabeçalho guarda o sha256 do fonte. `react.html` usa a versão compilada enquanto o
  hash bater; se o `.jsx` mudar, carrega o Babel standalone e compila ao vivo.
- **Segurança didática:** hash PBKDF2 do Auth, token CSRF único para formulários (`_csrf`)
  e API (`X-CSRF-Token`), consultas via DAL, escape automático das views,
  `check_reserved=['all']` nos nomes de campo, validação estrita do nome em `default/imagem`.

## Modelagem UML (`modelagem/`)

| Arquivo | Diagrama |
|---|---|
| `01_casos_de_uso.puml` | Casos de uso — 5 atores e 5 pacotes (público, cliente, vendedor, operador, administração) |
| `02_atividades.puml` | Atividades — compra, aprovação do PIX e entrega, com raias Cliente / Sistema / Operador |
| `03_classes.puml` | Classes — entidades (tabelas), enumerações e serviços de `regras.py` |
| `04_componentes.puml` | Componentes — navegador (React pré-compilado, loja.js) × pasta do projeto (app MVC, `loja.sqlite`, `imagens/`) × web2py, Pillow, qrcode |
| `05_estados.puml` | Estados — Pedido, PagamentoPix, Reclamacao e Produto |
| `06_implantacao.puml` | Implantação — pasta do projeto, web2py em pasta separada, GitHub/CDN opcionais |
| `07_sequencia.puml` | Sequência — compra (com as imagens via `default/imagem`), aprovação manual do PIX e upload de imagem |
| `08_modelo_dados.puml` | Modelo de dados — as tabelas usadas pela loja em `loja.sqlite`, com chaves e cardinalidades |

Renderização: `java -jar plantuml.jar -tpng modelagem/*.puml` (ou a extensão PlantUML do VS Code).

## Conteúdo do pacote

| Caminho | O que é |
|---|---|
| `loja_didatica_2_v2.py` | **Entregável principal** — fonte da aplicação, React e lançador. |
| `imagens/` | Capas, miniaturas e imagens adicionais dos 46 jogos, além de uploads de produtos. |
| `iniciar.sh`, `iniciar.bat` | Atalhos de inicialização para Linux/macOS e Windows (o .py também os recria). |
| `modelagem/` | 8 diagramas UML em PlantUML (`.puml`) com os `.png` renderizados. |
| `capturas/` | Telas da aplicação (desktop e celular). |
| `requirements.txt` | Bibliotecas Python opcionais (`pillow`, `qrcode`). |
