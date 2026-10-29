/* GERADO AUTOMATICAMENTE a partir de ../catalogo.jsx pelo Babel (preset react).
   fonte: catalogo.jsx sha256:a9e6c71ae47bcf08c73e1019356cc5e5b31e089ad2b47dea53c5f3c6c9146df5
   Não edite este arquivo: edite o .jsx e recompile (node compilar_jsx.js) — ou
   simplesmente salve o .jsx: a página vê que o hash mudou e compila com o Babel. */
/* =============================================================================
   <Catalogo/> — grade de produtos com busca ao digitar e filtro por categoria.
   Consome GET api/produtos e, ao comprar, POST api/carrinho_adicionar.
   Versão pré-compilada em compilado/<nome>.js (carregada pelas páginas); se este
   .jsx for editado, a página passa a compilá-lo no navegador com o Babel standalone.
   ============================================================================= */
(() => {
  const {
    useState,
    useEffect,
    useRef
  } = React;
  function CardProduto({
    p,
    podeComprar,
    logado,
    aoAdicionar
  }) {
    const [qtd, setQtd] = useState(1);
    const [enviando, setEnviando] = useState(false);
    const esgotado = p.estoque <= 0;
    async function adicionar() {
      setEnviando(true);
      await aoAdicionar(p, qtd);
      setEnviando(false);
      setQtd(1);
    }
    let estoqueInfo = null;
    if (esgotado) estoqueInfo = /*#__PURE__*/React.createElement("span", {
      className: "estoque-info zerado"
    }, "Esgotado");else if (p.estoque <= 5) estoqueInfo = /*#__PURE__*/React.createElement("span", {
      className: "estoque-info baixo"
    }, "S\xF3 ", p.estoque, " em estoque");else estoqueInfo = /*#__PURE__*/React.createElement("span", {
      className: "estoque-info"
    }, p.estoque, " em estoque");
    return /*#__PURE__*/React.createElement("article", {
      className: "produto-card"
    }, /*#__PURE__*/React.createElement("a", {
      className: "foto",
      href: p.url
    }, /*#__PURE__*/React.createElement("img", {
      src: p.imagem,
      alt: p.nome,
      loading: "lazy"
    })), /*#__PURE__*/React.createElement("div", {
      className: "corpo"
    }, /*#__PURE__*/React.createElement("span", {
      className: "categoria"
    }, p.categoria || 'Sem categoria', " \xB7 ", p.codigo), /*#__PURE__*/React.createElement("a", {
      className: "nome",
      href: p.url
    }, p.nome), /*#__PURE__*/React.createElement("p", {
      className: "descricao"
    }, p.descricao), /*#__PURE__*/React.createElement("div", {
      className: "rodape-card"
    }, /*#__PURE__*/React.createElement("span", {
      className: "preco"
    }, p.preco_fmt), estoqueInfo), /*#__PURE__*/React.createElement("span", {
      className: "estoque-info"
    }, "Entrega em ", p.prazo_dias, " dias \xFAteis")), /*#__PURE__*/React.createElement("div", {
      className: "comprar"
    }, podeComprar ? /*#__PURE__*/React.createElement("div", {
      className: "acoes"
    }, /*#__PURE__*/React.createElement("div", {
      className: "qtd",
      "aria-label": 'Quantidade de ' + p.nome
    }, /*#__PURE__*/React.createElement("button", {
      type: "button",
      onClick: () => setQtd(Math.max(1, qtd - 1)),
      disabled: esgotado || qtd <= 1
    }, "\u2212"), /*#__PURE__*/React.createElement("input", {
      type: "text",
      inputMode: "numeric",
      value: qtd,
      readOnly: true,
      "aria-label": "quantidade"
    }), /*#__PURE__*/React.createElement("button", {
      type: "button",
      onClick: () => setQtd(Math.min(p.estoque, qtd + 1)),
      disabled: esgotado || qtd >= p.estoque
    }, "+")), /*#__PURE__*/React.createElement("button", {
      type: "button",
      className: "btn btn-primario",
      onClick: adicionar,
      disabled: esgotado || enviando
    }, esgotado ? 'Esgotado' : enviando ? 'Adicionando…' : 'Adicionar')) : logado ? /*#__PURE__*/React.createElement("span", {
      className: "pequeno texto-3"
    }, "S\xF3 clientes compram. Sua conta tem outro papel.") : /*#__PURE__*/React.createElement("a", {
      className: "btn btn-secundario btn-largo",
      href: LOJA.urls.login
    }, "Entre para comprar")));
  }
  function Catalogo({
    buscaInicial
  }) {
    const [busca, setBusca] = useState(buscaInicial || '');
    const [categoria, setCategoria] = useState('');
    const [dados, setDados] = useState({
      produtos: [],
      categorias: [],
      pode_comprar: false,
      logado: false
    });
    const [carregando, setCarregando] = useState(true);
    const [erro, setErro] = useState('');
    const temporizador = useRef(null);

    // recarrega a lista quando busca/categoria mudam (com atraso de 300 ms ao digitar)
    useEffect(() => {
      clearTimeout(temporizador.current);
      temporizador.current = setTimeout(async () => {
        setCarregando(true);
        const r = await LojaAPI.get('produtos', null, {
          q: busca,
          categoria
        });
        if (r.ok) {
          setDados(r);
          setErro('');
        } else {
          setErro(r.erro || 'Não foi possível carregar o catálogo.');
        }
        setCarregando(false);
      }, busca ? 300 : 0);
      return () => clearTimeout(temporizador.current);
    }, [busca, categoria]);
    async function adicionar(p, qtd) {
      const r = await LojaAPI.post('carrinho_adicionar', {
        produto_id: p.id,
        quantidade: qtd
      });
      if (r.ok) {
        mostrarToast(r.mensagem);
        atualizarBadgeCarrinho(r.carrinho.quantidade_total);
      } else {
        mostrarToast(r.erro || 'Não foi possível adicionar.', 'erro');
      }
    }
    return /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
      className: "barra-busca"
    }, /*#__PURE__*/React.createElement("input", {
      type: "search",
      placeholder: "Buscar por nome, descri\xE7\xE3o ou c\xF3digo",
      value: busca,
      onChange: e => setBusca(e.target.value),
      "aria-label": "Buscar produtos"
    }), busca && /*#__PURE__*/React.createElement("button", {
      type: "button",
      className: "btn btn-secundario",
      onClick: () => setBusca('')
    }, "Limpar")), /*#__PURE__*/React.createElement("div", {
      className: "chips",
      role: "tablist",
      "aria-label": "Categorias"
    }, /*#__PURE__*/React.createElement("button", {
      type: "button",
      className: 'chip' + (categoria === '' ? ' ativo' : ''),
      onClick: () => setCategoria('')
    }, "Todas"), dados.categorias.map(c => /*#__PURE__*/React.createElement("button", {
      key: c.id,
      type: "button",
      className: 'chip' + (String(categoria) === String(c.id) ? ' ativo' : ''),
      onClick: () => setCategoria(String(c.id))
    }, c.nome))), erro && /*#__PURE__*/React.createElement("div", {
      className: "aviso aviso-erro"
    }, erro), carregando && dados.produtos.length === 0 ? /*#__PURE__*/React.createElement("p", {
      className: "carregando"
    }, "Carregando produtos\u2026") : dados.produtos.length === 0 ? /*#__PURE__*/React.createElement("div", {
      className: "cartao vazio-caixa"
    }, /*#__PURE__*/React.createElement("p", null, "Nenhum produto encontrado", busca ? ' para "' + busca + '"' : '', "."), /*#__PURE__*/React.createElement("button", {
      type: "button",
      className: "btn btn-secundario",
      onClick: () => {
        setBusca('');
        setCategoria('');
      }
    }, "Ver todos os produtos")) : /*#__PURE__*/React.createElement("div", {
      className: "grade-produtos",
      "aria-busy": carregando
    }, dados.produtos.map(p => /*#__PURE__*/React.createElement(CardProduto, {
      key: p.id,
      p: p,
      podeComprar: dados.pode_comprar,
      logado: dados.logado,
      aoAdicionar: adicionar
    }))));
  }
  const raizCatalogo = document.getElementById('app-catalogo');
  if (raizCatalogo) {
    ReactDOM.createRoot(raizCatalogo).render(/*#__PURE__*/React.createElement(Catalogo, {
      buscaInicial: raizCatalogo.dataset.busca
    }));
  }
})();
