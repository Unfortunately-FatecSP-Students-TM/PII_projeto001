/* =============================================================================
   <Carrinho/> — carrinho persistente do cliente.
   GET api/carrinho | POST api/carrinho_atualizar | api/carrinho_remover |
   api/carrinho_finalizar (cria o pedido e redireciona para a tela do PIX).
   ============================================================================= */
(() => {
const { useState, useEffect } = React;

function ItemCarrinho({ item, aoAlterar, aoRemover, ocupado }) {
  return (
    <div className="item-carrinho">
      <a href={item.url}><img src={item.imagem} alt="" /></a>
      <div>
        <a className="nome" href={item.url}>{item.nome}</a>
        <div className="meta">{item.codigo} · {item.preco_fmt} a unidade
          {!item.ativo && <strong className="texto-erro"> · produto indisponível</strong>}
        </div>
        <div className="controles">
          <div className="qtd" aria-label={'Quantidade de ' + item.nome}>
            <button type="button" disabled={ocupado} onClick={() => aoAlterar(item, item.quantidade - 1)}>−</button>
            <input type="text" value={item.quantidade} readOnly aria-label="quantidade" />
            <button type="button" disabled={ocupado || item.quantidade >= item.estoque}
                    onClick={() => aoAlterar(item, item.quantidade + 1)}>+</button>
          </div>
          <button type="button" className="btn btn-discreto btn-p" disabled={ocupado} onClick={() => aoRemover(item)}>Remover</button>
          <span className="subtotal">{item.subtotal_fmt}</span>
        </div>
        {item.quantidade > item.estoque && (
          <div className="pequeno" style={{ color: 'var(--erro)' }}>Só há {item.estoque} em estoque. Reduza a quantidade para finalizar.</div>
        )}
      </div>
    </div>
  );
}

function Carrinho({ inicial }) {
  const [carrinho, setCarrinho] = useState(inicial);
  const [ocupado, setOcupado] = useState(false);
  const [erro, setErro] = useState('');

  useEffect(() => {
    if (!inicial) LojaAPI.get('carrinho').then(r => { if (r.ok) setCarrinho(r.carrinho); });
  }, []);

  function aplicar(r) {
    if (r.ok) { setCarrinho(r.carrinho); setErro(''); atualizarBadgeCarrinho(r.carrinho.quantidade_total); }
    else { setErro(r.erro || 'Algo deu errado.'); }
  }

  async function alterar(item, quantidade) {
    setOcupado(true);
    aplicar(await LojaAPI.post('carrinho_atualizar', { item_id: item.item_id, quantidade }));
    setOcupado(false);
  }

  async function remover(item) {
    setOcupado(true);
    aplicar(await LojaAPI.post('carrinho_remover', { item_id: item.item_id }));
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
      const atual = await LojaAPI.get('carrinho');     // estoque pode ter mudado
      if (atual.ok) setCarrinho(atual.carrinho);
      setOcupado(false);
    }
  }

  if (!carrinho) return <p className="carregando">Carregando carrinho…</p>;

  if (carrinho.itens.length === 0) {
    return (
      <div className="cartao vazio-caixa">
        <p>Seu carrinho está vazio.</p>
        <a className="btn btn-primario" href={LOJA.urls.catalogo}>Ver o catálogo</a>
      </div>
    );
  }

  const bloqueado = carrinho.itens.some(i => i.quantidade > i.estoque || !i.ativo);

  return (
    <div className="carrinho">
      <div className="cartao">
        {erro && <div className="aviso aviso-erro" style={{ margin: '0 0 1rem' }}>{erro}</div>}
        {carrinho.itens.map(item => (
          <ItemCarrinho key={item.item_id} item={item} aoAlterar={alterar} aoRemover={remover} ocupado={ocupado} />
        ))}
      </div>
      <aside className="cartao">
        <h2>Resumo</h2>
        <div className="resumo-linha"><span>Itens</span><span>{carrinho.quantidade_total}</span></div>
        <div className="resumo-linha"><span>Entrega</span><span>até {carrinho.prazo_dias} dias úteis</span></div>
        <div className="resumo-linha"><span>Frete</span><span>grátis</span></div>
        <div className="resumo-linha resumo-total"><span>Total</span><span className="preco">{carrinho.total_fmt}</span></div>
        <button type="button" className="btn btn-primario btn-largo mt-1" onClick={finalizar} disabled={ocupado || bloqueado}>
          {ocupado ? 'Aguarde…' : 'Finalizar e pagar com PIX'}
        </button>
        {bloqueado && <p className="pequeno texto-2 mt-1">Ajuste os itens sem estoque antes de finalizar.</p>}
        <a className="btn btn-discreto btn-largo mt-1" href={LOJA.urls.catalogo}>Continuar comprando</a>
        <p className="pequeno texto-3 mt-1">O estoque é reservado quando o pedido é criado e devolvido se ele for cancelado.</p>
      </aside>
    </div>
  );
}

const raiz = document.getElementById('app-carrinho');
if (raiz) {
  const inicial = raiz.dataset.inicial ? JSON.parse(raiz.dataset.inicial) : null;
  ReactDOM.createRoot(raiz).render(<Carrinho inicial={inicial} />);
}
})();
