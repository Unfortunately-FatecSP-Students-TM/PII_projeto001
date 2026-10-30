/* GERADO AUTOMATICAMENTE a partir de ../estoque.jsx pelo Babel (preset react).
   fonte: estoque.jsx sha256:dba4c4ffd7bfac63e69e7250d67c8e7f8cdcbc346e1e60f72ad917286923246d
   Não edite este arquivo: edite o .jsx e recompile (node compilar_jsx.js) — ou
   simplesmente salve o .jsx: a página vê que o hash mudou e compila com o Babel. */
/* =============================================================================
   <Estoque/> — tabela de estoque do vendedor com ajuste em linha.
   GET api/estoque | POST api/estoque_ajustar {produto_id, quantidade, motivo}
   Toda alteração vira um movimento_estoque (auditável) no servidor.
   ============================================================================= */
(() => {
  const {
    useState,
    useEffect
  } = React;
  function LinhaProduto({
    p,
    aoAjustar,
    ocupado
  }) {
    const [qtd, setQtd] = useState('');
    const [motivo, setMotivo] = useState('');
    const n = parseInt(qtd, 10);
    const valido = !isNaN(n) && n !== 0;
    async function enviar(sinal) {
      if (!valido) return;
      await aoAjustar(p, sinal * Math.abs(n), motivo);
      setQtd('');
      setMotivo('');
    }
    return /*#__PURE__*/React.createElement("tr", null, /*#__PURE__*/React.createElement("td", {
      "data-rotulo": "Produto"
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        display: 'flex',
        gap: '.6rem',
        alignItems: 'center'
      }
    }, /*#__PURE__*/React.createElement("img", {
      className: "mini",
      src: p.imagem,
      alt: ""
    }), /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("strong", null, p.nome), /*#__PURE__*/React.createElement("br", null), /*#__PURE__*/React.createElement("span", {
      className: "mono pequeno texto-3"
    }, p.codigo)))), /*#__PURE__*/React.createElement("td", {
      "data-rotulo": "Pre\xE7o",
      className: "num"
    }, p.preco_fmt), /*#__PURE__*/React.createElement("td", {
      "data-rotulo": "Estoque",
      className: "num"
    }, /*#__PURE__*/React.createElement("strong", {
      className: p.estoque === 0 ? 'texto-erro' : '',
      style: {
        fontSize: '1.1rem',
        color: p.estoque === 0 ? 'var(--erro)' : 'inherit'
      }
    }, p.estoque)), /*#__PURE__*/React.createElement("td", {
      "data-rotulo": "\xDAltimo movimento",
      className: "pequeno texto-2"
    }, p.ultimo_movimento ? /*#__PURE__*/React.createElement("span", null, p.ultimo_movimento.tipo, " ", p.ultimo_movimento.quantidade > 0 ? '+' : '', p.ultimo_movimento.quantidade, /*#__PURE__*/React.createElement("br", null), p.ultimo_movimento.quando, p.ultimo_movimento.motivo && ' — ' + p.ultimo_movimento.motivo) : '—'), /*#__PURE__*/React.createElement("td", {
      "data-rotulo": "Ajustar",
      className: "acoes-td"
    }, /*#__PURE__*/React.createElement("div", {
      className: "acoes"
    }, /*#__PURE__*/React.createElement("input", {
      type: "number",
      min: "1",
      style: {
        width: '5rem'
      },
      placeholder: "qtd",
      value: qtd,
      onChange: e => setQtd(e.target.value),
      "aria-label": 'Quantidade para ' + p.nome
    }), /*#__PURE__*/React.createElement("input", {
      type: "text",
      style: {
        width: '11rem'
      },
      placeholder: "motivo",
      value: motivo,
      onChange: e => setMotivo(e.target.value),
      "aria-label": "Motivo"
    }), /*#__PURE__*/React.createElement("button", {
      type: "button",
      className: "btn btn-ok btn-p",
      disabled: ocupado || !valido,
      onClick: () => enviar(+1)
    }, "Entrada"), /*#__PURE__*/React.createElement("button", {
      type: "button",
      className: "btn btn-secundario btn-p",
      disabled: ocupado || !valido || Math.abs(n) > p.estoque,
      onClick: () => enviar(-1)
    }, "Baixa"), /*#__PURE__*/React.createElement("a", {
      className: "btn btn-discreto btn-p",
      href: p.url_movimentos
    }, "Hist\xF3rico"))));
  }
  function Estoque() {
    const [produtos, setProdutos] = useState(null);
    const [ocupado, setOcupado] = useState(false);
    const [busca, setBusca] = useState('');
    useEffect(() => {
      LojaAPI.get('estoque').then(r => {
        if (r.ok) setProdutos(r.produtos);
      });
    }, []);
    async function ajustar(p, quantidade, motivo) {
      setOcupado(true);
      const r = await LojaAPI.post('estoque_ajustar', {
        produto_id: p.id,
        quantidade,
        motivo
      });
      if (r.ok) {
        setProdutos(r.produtos);
        mostrarToast(r.mensagem);
      } else mostrarToast(r.erro || 'Não foi possível ajustar.', 'erro');
      setOcupado(false);
    }
    if (produtos === null) return /*#__PURE__*/React.createElement("p", {
      className: "carregando"
    }, "Carregando estoque\u2026");
    const t = busca.toLowerCase();
    const visiveis = produtos.filter(p => !t || p.nome.toLowerCase().includes(t) || p.codigo.toLowerCase().includes(t));
    const zerados = produtos.filter(p => p.estoque === 0).length;
    return /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
      className: "barra-busca"
    }, /*#__PURE__*/React.createElement("input", {
      type: "search",
      placeholder: "Filtrar por nome ou c\xF3digo",
      value: busca,
      onChange: e => setBusca(e.target.value),
      "aria-label": "Filtrar"
    }), /*#__PURE__*/React.createElement("span", {
      className: "pequeno texto-2",
      style: {
        alignSelf: 'center'
      }
    }, produtos.length, " produtos \xB7 ", zerados, " sem estoque")), /*#__PURE__*/React.createElement("div", {
      className: "tabela-wrap"
    }, /*#__PURE__*/React.createElement("table", {
      className: "tabela empilha"
    }, /*#__PURE__*/React.createElement("thead", null, /*#__PURE__*/React.createElement("tr", null, /*#__PURE__*/React.createElement("th", null, "Produto"), /*#__PURE__*/React.createElement("th", {
      className: "num"
    }, "Pre\xE7o"), /*#__PURE__*/React.createElement("th", {
      className: "num"
    }, "Estoque"), /*#__PURE__*/React.createElement("th", null, "\xDAltimo movimento"), /*#__PURE__*/React.createElement("th", null, "Ajustar"))), /*#__PURE__*/React.createElement("tbody", null, visiveis.length === 0 ? /*#__PURE__*/React.createElement("tr", null, /*#__PURE__*/React.createElement("td", {
      colSpan: "5",
      className: "vazio"
    }, "Nenhum produto.")) : visiveis.map(p => /*#__PURE__*/React.createElement(LinhaProduto, {
      key: p.id,
      p: p,
      aoAjustar: ajustar,
      ocupado: ocupado
    }))))));
  }
  const raiz = document.getElementById('app-estoque');
  if (raiz) ReactDOM.createRoot(raiz).render(/*#__PURE__*/React.createElement(Estoque, null));
})();
