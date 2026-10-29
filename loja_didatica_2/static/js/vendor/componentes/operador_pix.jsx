/* =============================================================================
   <PainelPix/> — fila de pagamentos PIX aguardando aprovação manual do operador.
   GET api/pix_pendentes (atualizado a cada 8 s) | POST api/pix_decidir
   ============================================================================= */
(() => {
const { useState, useEffect, useRef } = React;

function CartaoPix({ pix, aoDecidir, ocupado }) {
  const [observacao, setObservacao] = useState('');
  const informado = pix.status === 'informado';
  return (
    <article className={'fila-item ' + pix.status}>
      <div className="topo-item">
        <strong className="mono">{pix.pedido_codigo}</strong>
        <span className={'etiqueta ' + pix.status}>{pix.status_rotulo}</span>
      </div>
      <div className="preco">{pix.valor_fmt}</div>
      <div className="pequeno texto-2">
        {pix.cliente} · {pix.cliente_email}<br />
        Gerado em {pix.criado_em}{informado && <span><br />Cliente informou pagamento em {pix.informado_em}</span>}
      </div>
      <ul className="itens">
        {pix.itens.map((i, k) => <li key={k}>{i.quantidade}× {i.nome} — {i.subtotal_fmt}</li>)}
      </ul>
      <input type="text" placeholder="Observação (opcional)" value={observacao}
             onChange={e => setObservacao(e.target.value)} aria-label="Observação" />
      <div className="acoes">
        <button type="button" className="btn btn-ok" disabled={ocupado}
                onClick={() => aoDecidir(pix, 'confirmar', observacao)}>Confirmar recebimento</button>
        <button type="button" className="btn btn-perigo btn-p" disabled={ocupado}
                onClick={() => { if (window.confirm('Recusar o PIX e cancelar o pedido ' + pix.pedido_codigo + '? O estoque será devolvido.')) aoDecidir(pix, 'recusar', observacao); }}>
          Recusar
        </button>
        <a className="btn btn-discreto btn-p" href={pix.url_pedido}>Ver pedido</a>
      </div>
    </article>
  );
}

function PainelPix() {
  const [pendentes, setPendentes] = useState(null);
  const [ocupado, setOcupado] = useState(false);
  const [filtro, setFiltro] = useState('todos');
  const [atualizadoEm, setAtualizadoEm] = useState(null);
  const timer = useRef(null);

  async function carregar() {
    const r = await LojaAPI.get('pix_pendentes');
    if (r.ok) { setPendentes(r.pendentes); setAtualizadoEm(new Date()); }
  }

  useEffect(() => {
    carregar();
    timer.current = setInterval(carregar, 8000);
    return () => clearInterval(timer.current);
  }, []);

  async function decidir(pix, decisao, observacao) {
    setOcupado(true);
    const r = await LojaAPI.post('pix_decidir', { pix_id: pix.pix_id, decisao, observacao });
    if (r.ok) { setPendentes(r.pendentes); mostrarToast(r.mensagem); }
    else { mostrarToast(r.erro || 'Não foi possível registrar a decisão.', 'erro'); carregar(); }
    setOcupado(false);
  }

  if (pendentes === null) return <p className="carregando">Carregando fila…</p>;

  const visiveis = pendentes.filter(p => filtro === 'todos' || p.status === filtro);
  const nInformados = pendentes.filter(p => p.status === 'informado').length;

  return (
    <div>
      <div className="chips">
        <button type="button" className={'chip' + (filtro === 'todos' ? ' ativo' : '')} onClick={() => setFiltro('todos')}>Todos ({pendentes.length})</button>
        <button type="button" className={'chip' + (filtro === 'informado' ? ' ativo' : '')} onClick={() => setFiltro('informado')}>Cliente informou pagamento ({nInformados})</button>
        <button type="button" className={'chip' + (filtro === 'gerado' ? ' ativo' : '')} onClick={() => setFiltro('gerado')}>Só gerados ({pendentes.length - nInformados})</button>
        <span className="pequeno texto-3" style={{ alignSelf: 'center', marginLeft: 'auto' }}>
          {atualizadoEm && 'Atualizado às ' + atualizadoEm.toLocaleTimeString('pt-BR')} · <button type="button" className="btn btn-discreto btn-p" onClick={carregar}>Atualizar agora</button>
        </span>
      </div>
      {visiveis.length === 0 ? (
        <div className="cartao vazio-caixa"><p>Nenhum pagamento aguardando decisão.</p></div>
      ) : (
        <div className="fila">
          {visiveis.map(p => <CartaoPix key={p.pix_id} pix={p} aoDecidir={decidir} ocupado={ocupado} />)}
        </div>
      )}
    </div>
  );
}

const raiz = document.getElementById('app-pix');
if (raiz) ReactDOM.createRoot(raiz).render(<PainelPix />);
})();
