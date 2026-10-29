/* GERADO AUTOMATICAMENTE a partir de ../operador_pix.jsx pelo Babel (preset react).
   fonte: operador_pix.jsx sha256:2f4330895835c0a43d4d63490b70a9400989c91497c845622b430e512fca027f
   Não edite este arquivo: edite o .jsx e recompile (node compilar_jsx.js) — ou
   simplesmente salve o .jsx: a página vê que o hash mudou e compila com o Babel. */
/* =============================================================================
   <PainelPix/> — fila de pagamentos PIX aguardando aprovação manual do operador.
   GET api/pix_pendentes (atualizado a cada 8 s) | POST api/pix_decidir
   ============================================================================= */
(() => {
  const {
    useState,
    useEffect,
    useRef
  } = React;
  function CartaoPix({
    pix,
    aoDecidir,
    ocupado
  }) {
    const [observacao, setObservacao] = useState('');
    const informado = pix.status === 'informado';
    return /*#__PURE__*/React.createElement("article", {
      className: 'fila-item ' + pix.status
    }, /*#__PURE__*/React.createElement("div", {
      className: "topo-item"
    }, /*#__PURE__*/React.createElement("strong", {
      className: "mono"
    }, pix.pedido_codigo), /*#__PURE__*/React.createElement("span", {
      className: 'etiqueta ' + pix.status
    }, pix.status_rotulo)), /*#__PURE__*/React.createElement("div", {
      className: "preco"
    }, pix.valor_fmt), /*#__PURE__*/React.createElement("div", {
      className: "pequeno texto-2"
    }, pix.cliente, " \xB7 ", pix.cliente_email, /*#__PURE__*/React.createElement("br", null), "Gerado em ", pix.criado_em, informado && /*#__PURE__*/React.createElement("span", null, /*#__PURE__*/React.createElement("br", null), "Cliente informou pagamento em ", pix.informado_em)), /*#__PURE__*/React.createElement("ul", {
      className: "itens"
    }, pix.itens.map((i, k) => /*#__PURE__*/React.createElement("li", {
      key: k
    }, i.quantidade, "\xD7 ", i.nome, " \u2014 ", i.subtotal_fmt))), /*#__PURE__*/React.createElement("input", {
      type: "text",
      placeholder: "Observa\xE7\xE3o (opcional)",
      value: observacao,
      onChange: e => setObservacao(e.target.value),
      "aria-label": "Observa\xE7\xE3o"
    }), /*#__PURE__*/React.createElement("div", {
      className: "acoes"
    }, /*#__PURE__*/React.createElement("button", {
      type: "button",
      className: "btn btn-ok",
      disabled: ocupado,
      onClick: () => aoDecidir(pix, 'confirmar', observacao)
    }, "Confirmar recebimento"), /*#__PURE__*/React.createElement("button", {
      type: "button",
      className: "btn btn-perigo btn-p",
      disabled: ocupado,
      onClick: () => {
        if (window.confirm('Recusar o PIX e cancelar o pedido ' + pix.pedido_codigo + '? O estoque será devolvido.')) aoDecidir(pix, 'recusar', observacao);
      }
    }, "Recusar"), /*#__PURE__*/React.createElement("a", {
      className: "btn btn-discreto btn-p",
      href: pix.url_pedido
    }, "Ver pedido")));
  }
  function PainelPix() {
    const [pendentes, setPendentes] = useState(null);
    const [ocupado, setOcupado] = useState(false);
    const [filtro, setFiltro] = useState('todos');
    const [atualizadoEm, setAtualizadoEm] = useState(null);
    const timer = useRef(null);
    async function carregar() {
      const r = await LojaAPI.get('pix_pendentes');
      if (r.ok) {
        setPendentes(r.pendentes);
        setAtualizadoEm(new Date());
      }
    }
    useEffect(() => {
      carregar();
      timer.current = setInterval(carregar, 8000);
      return () => clearInterval(timer.current);
    }, []);
    async function decidir(pix, decisao, observacao) {
      setOcupado(true);
      const r = await LojaAPI.post('pix_decidir', {
        pix_id: pix.pix_id,
        decisao,
        observacao
      });
      if (r.ok) {
        setPendentes(r.pendentes);
        mostrarToast(r.mensagem);
      } else {
        mostrarToast(r.erro || 'Não foi possível registrar a decisão.', 'erro');
        carregar();
      }
      setOcupado(false);
    }
    if (pendentes === null) return /*#__PURE__*/React.createElement("p", {
      className: "carregando"
    }, "Carregando fila\u2026");
    const visiveis = pendentes.filter(p => filtro === 'todos' || p.status === filtro);
    const nInformados = pendentes.filter(p => p.status === 'informado').length;
    return /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
      className: "chips"
    }, /*#__PURE__*/React.createElement("button", {
      type: "button",
      className: 'chip' + (filtro === 'todos' ? ' ativo' : ''),
      onClick: () => setFiltro('todos')
    }, "Todos (", pendentes.length, ")"), /*#__PURE__*/React.createElement("button", {
      type: "button",
      className: 'chip' + (filtro === 'informado' ? ' ativo' : ''),
      onClick: () => setFiltro('informado')
    }, "Cliente informou pagamento (", nInformados, ")"), /*#__PURE__*/React.createElement("button", {
      type: "button",
      className: 'chip' + (filtro === 'gerado' ? ' ativo' : ''),
      onClick: () => setFiltro('gerado')
    }, "S\xF3 gerados (", pendentes.length - nInformados, ")"), /*#__PURE__*/React.createElement("span", {
      className: "pequeno texto-3",
      style: {
        alignSelf: 'center',
        marginLeft: 'auto'
      }
    }, atualizadoEm && 'Atualizado às ' + atualizadoEm.toLocaleTimeString('pt-BR'), " \xB7 ", /*#__PURE__*/React.createElement("button", {
      type: "button",
      className: "btn btn-discreto btn-p",
      onClick: carregar
    }, "Atualizar agora"))), visiveis.length === 0 ? /*#__PURE__*/React.createElement("div", {
      className: "cartao vazio-caixa"
    }, /*#__PURE__*/React.createElement("p", null, "Nenhum pagamento aguardando decis\xE3o.")) : /*#__PURE__*/React.createElement("div", {
      className: "fila"
    }, visiveis.map(p => /*#__PURE__*/React.createElement(CartaoPix, {
      key: p.pix_id,
      pix: p,
      aoDecidir: decidir,
      ocupado: ocupado
    }))));
  }
  const raiz = document.getElementById('app-pix');
  if (raiz) ReactDOM.createRoot(raiz).render(/*#__PURE__*/React.createElement(PainelPix, null));
})();
