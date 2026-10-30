/* GERADO a partir de catalogo.jsx; sha256:0d28fb3119d3b80ba1ecb14e223cb13e4a16463ebb2e2ca9f1423b36b87ce0fb */
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
    }, p.descricao), /*#__PURE__*/React.createElement("span", {
      className: "pequeno"
    }, "Estado: ", p.estado), p.console && /*#__PURE__*/React.createElement("span", {
      className: "pequeno"
    }, "Console: ", p.console), /*#__PURE__*/React.createElement("span", {
      className: "avaliacao"
    }, p.avaliacao_media ? '★ ' + p.avaliacao_media.toFixed(1) + ' / 5 (' + p.avaliacao_quantidade + ')' : 'Sem avaliações'), /*#__PURE__*/React.createElement("div", {
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
    const [consoleProduto, setConsoleProduto] = useState('');
    const [precoMin, setPrecoMin] = useState('');
    const [precoMax, setPrecoMax] = useState('');
    const [avaliacaoMinima, setAvaliacaoMinima] = useState('');
    const [estado, setEstado] = useState('');
    const [dados, setDados] = useState({
      produtos: [],
      categorias: [],
      consoles: [],
      estados: [],
      pode_comprar: false,
      logado: false
    });
    const [carregando, setCarregando] = useState(true);
    const [erro, setErro] = useState('');
    const temporizador = useRef(null);
    const requisicaoAtual = useRef(0);

    // recarrega o catálogo quando qualquer filtro muda
    useEffect(() => {
      clearTimeout(temporizador.current);
      temporizador.current = setTimeout(async () => {
        const requisicao = ++requisicaoAtual.current;
        setCarregando(true);
        const r = await LojaAPI.get('produtos', null, {
          q: busca,
          categoria,
          console: consoleProduto,
          preco_min: precoMin,
          preco_max: precoMax,
          avaliacao_minima: avaliacaoMinima,
          estado
        });
        if (requisicao !== requisicaoAtual.current) return;
        if (r.ok) {
          setDados(r);
          setErro('');
        } else {
          setErro(r.erro || 'Não foi possível carregar o catálogo.');
        }
        setCarregando(false);
      }, busca ? 300 : 0);
      return () => {
        clearTimeout(temporizador.current);
        requisicaoAtual.current += 1;
      };
    }, [busca, categoria, consoleProduto, precoMin, precoMax, avaliacaoMinima, estado]);
    function limparFiltros() {
      setBusca('');
      setCategoria('');
      setConsoleProduto('');
      setPrecoMin('');
      setPrecoMax('');
      setAvaliacaoMinima('');
      setEstado('');
    }
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
    })), /*#__PURE__*/React.createElement("section", {
      className: "cartao filtros-avancados",
      "aria-label": "Busca avan\xE7ada"
    }, /*#__PURE__*/React.createElement("div", {
      className: "filtros-titulo"
    }, /*#__PURE__*/React.createElement("h2", null, "Busca avan\xE7ada"), /*#__PURE__*/React.createElement("button", {
      type: "button",
      className: "btn btn-secundario",
      onClick: limparFiltros
    }, "Limpar filtros")), /*#__PURE__*/React.createElement("div", {
      className: "filtros-grade"
    }, /*#__PURE__*/React.createElement("div", {
      className: "campo"
    }, /*#__PURE__*/React.createElement("label", {
      htmlFor: "filtro-console"
    }, "Console"), /*#__PURE__*/React.createElement("select", {
      id: "filtro-console",
      value: consoleProduto,
      onChange: e => setConsoleProduto(e.target.value)
    }, /*#__PURE__*/React.createElement("option", {
      value: ""
    }, "Todos os consoles"), /*#__PURE__*/React.createElement("option", {
      value: "sem_console"
    }, "Sem console"), dados.consoles.map(c => /*#__PURE__*/React.createElement("option", {
      key: c,
      value: c
    }, c)))), /*#__PURE__*/React.createElement("div", {
      className: "campo"
    }, /*#__PURE__*/React.createElement("label", {
      htmlFor: "filtro-preco-min"
    }, "Pre\xE7o m\xEDnimo (R$)"), /*#__PURE__*/React.createElement("input", {
      id: "filtro-preco-min",
      type: "number",
      min: "0",
      step: "0.01",
      value: precoMin,
      onChange: e => setPrecoMin(e.target.value)
    })), /*#__PURE__*/React.createElement("div", {
      className: "campo"
    }, /*#__PURE__*/React.createElement("label", {
      htmlFor: "filtro-preco-max"
    }, "Pre\xE7o m\xE1ximo (R$)"), /*#__PURE__*/React.createElement("input", {
      id: "filtro-preco-max",
      type: "number",
      min: "0",
      step: "0.01",
      value: precoMax,
      onChange: e => setPrecoMax(e.target.value)
    })), /*#__PURE__*/React.createElement("div", {
      className: "campo"
    }, /*#__PURE__*/React.createElement("label", {
      htmlFor: "filtro-categoria"
    }, "Categoria"), /*#__PURE__*/React.createElement("select", {
      id: "filtro-categoria",
      value: categoria,
      onChange: e => setCategoria(e.target.value)
    }, /*#__PURE__*/React.createElement("option", {
      value: ""
    }, "Todas as categorias"), dados.categorias.map(c => /*#__PURE__*/React.createElement("option", {
      key: c.id,
      value: c.id
    }, c.nome)))), /*#__PURE__*/React.createElement("div", {
      className: "campo"
    }, /*#__PURE__*/React.createElement("label", {
      htmlFor: "filtro-avaliacao"
    }, "Avalia\xE7\xE3o m\xEDnima"), /*#__PURE__*/React.createElement("select", {
      id: "filtro-avaliacao",
      value: avaliacaoMinima,
      onChange: e => setAvaliacaoMinima(e.target.value)
    }, /*#__PURE__*/React.createElement("option", {
      value: ""
    }, "Qualquer avalia\xE7\xE3o"), [1, 2, 3, 4, 5].map(n => /*#__PURE__*/React.createElement("option", {
      key: n,
      value: n
    }, n, " ", n === 1 ? 'estrela' : 'estrelas', " ou mais")))), /*#__PURE__*/React.createElement("div", {
      className: "campo"
    }, /*#__PURE__*/React.createElement("label", {
      htmlFor: "filtro-estado"
    }, "Estado"), /*#__PURE__*/React.createElement("select", {
      id: "filtro-estado",
      value: estado,
      onChange: e => setEstado(e.target.value)
    }, /*#__PURE__*/React.createElement("option", {
      value: ""
    }, "Todos os estados"), dados.estados.map(e => /*#__PURE__*/React.createElement("option", {
      key: e,
      value: e
    }, e)))))), erro && /*#__PURE__*/React.createElement("div", {
      className: "aviso aviso-erro"
    }, erro), carregando && dados.produtos.length === 0 ? /*#__PURE__*/React.createElement("p", {
      className: "carregando"
    }, "Carregando produtos\u2026") : dados.produtos.length === 0 ? /*#__PURE__*/React.createElement("div", {
      className: "cartao vazio-caixa"
    }, /*#__PURE__*/React.createElement("p", null, "Nenhum produto encontrado", busca ? ' para "' + busca + '"' : '', "."), /*#__PURE__*/React.createElement("button", {
      type: "button",
      className: "btn btn-secundario",
      onClick: limparFiltros
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
