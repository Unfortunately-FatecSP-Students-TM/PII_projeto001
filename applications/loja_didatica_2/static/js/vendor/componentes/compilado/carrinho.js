/* GERADO AUTOMATICAMENTE a partir de ../carrinho.jsx pelo Babel (preset react).
   fonte: carrinho.jsx sha256:e584e48d83c28db20bbea8dea3a88bbbeae3d2eba5b2069ca49407c4acd69247
   Não edite este arquivo: edite o .jsx e recompile (node compilar_jsx.js) — ou
   simplesmente salve o .jsx: a página vê que o hash mudou e compila com o Babel. */
/* =============================================================================
   <Carrinho/> — carrinho persistente do cliente.
   GET api/carrinho | POST api/carrinho_atualizar | api/carrinho_remover |
   api/carrinho_finalizar (cria o pedido e redireciona para a tela do PIX).
   ============================================================================= */
(() => {
  const {
    useState,
    useEffect
  } = React;
  function ItemCarrinho({
    item,
    aoAlterar,
    aoRemover,
    ocupado
  }) {
    return /*#__PURE__*/React.createElement("div", {
      className: "item-carrinho"
    }, /*#__PURE__*/React.createElement("a", {
      href: item.url
    }, /*#__PURE__*/React.createElement("img", {
      src: item.imagem,
      alt: ""
    })), /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("a", {
      className: "nome",
      href: item.url
    }, item.nome), /*#__PURE__*/React.createElement("div", {
      className: "meta"
    }, item.codigo, " \xB7 ", item.preco_fmt, " a unidade", !item.ativo && /*#__PURE__*/React.createElement("strong", {
      className: "texto-erro"
    }, " \xB7 produto indispon\xEDvel")), /*#__PURE__*/React.createElement("div", {
      className: "controles"
    }, /*#__PURE__*/React.createElement("div", {
      className: "qtd",
      "aria-label": 'Quantidade de ' + item.nome
    }, /*#__PURE__*/React.createElement("button", {
      type: "button",
      disabled: ocupado,
      onClick: () => aoAlterar(item, item.quantidade - 1)
    }, "\u2212"), /*#__PURE__*/React.createElement("input", {
      type: "text",
      value: item.quantidade,
      readOnly: true,
      "aria-label": "quantidade"
    }), /*#__PURE__*/React.createElement("button", {
      type: "button",
      disabled: ocupado || item.quantidade >= item.estoque,
      onClick: () => aoAlterar(item, item.quantidade + 1)
    }, "+")), /*#__PURE__*/React.createElement("button", {
      type: "button",
      className: "btn btn-discreto btn-p",
      disabled: ocupado,
      onClick: () => aoRemover(item)
    }, "Remover"), /*#__PURE__*/React.createElement("span", {
      className: "subtotal"
    }, item.subtotal_fmt)), item.quantidade > item.estoque && /*#__PURE__*/React.createElement("div", {
      className: "pequeno",
      style: {
        color: 'var(--erro)'
      }
    }, "S\xF3 h\xE1 ", item.estoque, " em estoque. Reduza a quantidade para finalizar.")));
  }
  function Carrinho({
    inicial
  }) {
    const [carrinho, setCarrinho] = useState(inicial);
    const [ocupado, setOcupado] = useState(false);
    const [erro, setErro] = useState('');
    useEffect(() => {
      if (!inicial) LojaAPI.get('carrinho').then(r => {
        if (r.ok) setCarrinho(r.carrinho);
      });
    }, []);
    function aplicar(r) {
      if (r.ok) {
        setCarrinho(r.carrinho);
        setErro('');
        atualizarBadgeCarrinho(r.carrinho.quantidade_total);
      } else {
        setErro(r.erro || 'Algo deu errado.');
      }
    }
    async function alterar(item, quantidade) {
      setOcupado(true);
      aplicar(await LojaAPI.post('carrinho_atualizar', {
        item_id: item.item_id,
        quantidade
      }));
      setOcupado(false);
    }
    async function remover(item) {
      setOcupado(true);
      aplicar(await LojaAPI.post('carrinho_remover', {
        item_id: item.item_id
      }));
      setOcupado(false);
      mostrarToast(item.nome + ' removido do carrinho.');
    }
    async function finalizar() {
      setOcupado(true);
      const r = await LojaAPI.post('carrinho_finalizar', {});
      if (r.ok) {
        mostrarToast('Pedido criado. Abrindo o pagamento PIX…');
        window.location = r.url_pix;
      } else {
        setErro(r.erro || 'Não foi possível finalizar.');
        const atual = await LojaAPI.get('carrinho'); // estoque pode ter mudado
        if (atual.ok) setCarrinho(atual.carrinho);
        setOcupado(false);
      }
    }
    if (!carrinho) return /*#__PURE__*/React.createElement("p", {
      className: "carregando"
    }, "Carregando carrinho\u2026");
    if (carrinho.itens.length === 0) {
      return /*#__PURE__*/React.createElement("div", {
        className: "cartao vazio-caixa"
      }, /*#__PURE__*/React.createElement("p", null, "Seu carrinho est\xE1 vazio."), /*#__PURE__*/React.createElement("a", {
        className: "btn btn-primario",
        href: LOJA.urls.catalogo
      }, "Ver o cat\xE1logo"));
    }
    const bloqueado = carrinho.itens.some(i => i.quantidade > i.estoque || !i.ativo);
    return /*#__PURE__*/React.createElement("div", {
      className: "carrinho"
    }, /*#__PURE__*/React.createElement("div", {
      className: "cartao"
    }, erro && /*#__PURE__*/React.createElement("div", {
      className: "aviso aviso-erro",
      style: {
        margin: '0 0 1rem'
      }
    }, erro), carrinho.itens.map(item => /*#__PURE__*/React.createElement(ItemCarrinho, {
      key: item.item_id,
      item: item,
      aoAlterar: alterar,
      aoRemover: remover,
      ocupado: ocupado
    }))), /*#__PURE__*/React.createElement("aside", {
      className: "cartao"
    }, /*#__PURE__*/React.createElement("h2", null, "Resumo"), /*#__PURE__*/React.createElement("div", {
      className: "resumo-linha"
    }, /*#__PURE__*/React.createElement("span", null, "Itens"), /*#__PURE__*/React.createElement("span", null, carrinho.quantidade_total)), /*#__PURE__*/React.createElement("div", {
      className: "resumo-linha"
    }, /*#__PURE__*/React.createElement("span", null, "Entrega"), /*#__PURE__*/React.createElement("span", null, "at\xE9 ", carrinho.prazo_dias, " dias \xFAteis")), /*#__PURE__*/React.createElement("div", {
      className: "resumo-linha"
    }, /*#__PURE__*/React.createElement("span", null, "Frete"), /*#__PURE__*/React.createElement("span", null, "gr\xE1tis")), /*#__PURE__*/React.createElement("div", {
      className: "resumo-linha resumo-total"
    }, /*#__PURE__*/React.createElement("span", null, "Total"), /*#__PURE__*/React.createElement("span", {
      className: "preco"
    }, carrinho.total_fmt)), /*#__PURE__*/React.createElement("button", {
      type: "button",
      className: "btn btn-primario btn-largo mt-1",
      onClick: finalizar,
      disabled: ocupado || bloqueado
    }, ocupado ? 'Aguarde…' : 'Finalizar e pagar com PIX'), bloqueado && /*#__PURE__*/React.createElement("p", {
      className: "pequeno texto-2 mt-1"
    }, "Ajuste os itens sem estoque antes de finalizar."), /*#__PURE__*/React.createElement("a", {
      className: "btn btn-discreto btn-largo mt-1",
      href: LOJA.urls.catalogo
    }, "Continuar comprando"), /*#__PURE__*/React.createElement("p", {
      className: "pequeno texto-3 mt-1"
    }, "O estoque \xE9 reservado quando o pedido \xE9 criado e devolvido se ele for cancelado.")));
  }
  const raiz = document.getElementById('app-carrinho');
  if (raiz) {
    const inicial = raiz.dataset.inicial ? JSON.parse(raiz.dataset.inicial) : null;
    ReactDOM.createRoot(raiz).render(/*#__PURE__*/React.createElement(Carrinho, {
      inicial: inicial
    }));
  }
})();
