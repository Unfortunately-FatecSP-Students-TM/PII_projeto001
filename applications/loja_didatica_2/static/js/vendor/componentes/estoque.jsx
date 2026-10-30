/* =============================================================================
   <Estoque/> — tabela de estoque do vendedor com ajuste em linha.
   GET api/estoque | POST api/estoque_ajustar {produto_id, quantidade, motivo}
   Toda alteração vira um movimento_estoque (auditável) no servidor.
   ============================================================================= */
(() => {
const { useState, useEffect } = React;

function LinhaProduto({ p, aoAjustar, ocupado }) {
  const [qtd, setQtd] = useState('');
  const [motivo, setMotivo] = useState('');
  const n = parseInt(qtd, 10);
  const valido = !isNaN(n) && n !== 0;

  async function enviar(sinal) {
    if (!valido) return;
    await aoAjustar(p, sinal * Math.abs(n), motivo);
    setQtd(''); setMotivo('');
  }

  return (
    <tr>
      <td data-rotulo="Produto">
        <div style={{ display: 'flex', gap: '.6rem', alignItems: 'center' }}>
          <img className="mini" src={p.imagem} alt="" />
          <div><strong>{p.nome}</strong><br /><span className="mono pequeno texto-3">{p.codigo}</span></div>
        </div>
      </td>
      <td data-rotulo="Preço" className="num">{p.preco_fmt}</td>
      <td data-rotulo="Estoque" className="num">
        <strong className={p.estoque === 0 ? 'texto-erro' : ''} style={{ fontSize: '1.1rem', color: p.estoque === 0 ? 'var(--erro)' : 'inherit' }}>{p.estoque}</strong>
      </td>
      <td data-rotulo="Último movimento" className="pequeno texto-2">
        {p.ultimo_movimento ? (
          <span>{p.ultimo_movimento.tipo} {p.ultimo_movimento.quantidade > 0 ? '+' : ''}{p.ultimo_movimento.quantidade}<br />{p.ultimo_movimento.quando}{p.ultimo_movimento.motivo && ' — ' + p.ultimo_movimento.motivo}</span>
        ) : '—'}
      </td>
      <td data-rotulo="Ajustar" className="acoes-td">
        <div className="acoes">
          <input type="number" min="1" style={{ width: '5rem' }} placeholder="qtd" value={qtd}
                 onChange={e => setQtd(e.target.value)} aria-label={'Quantidade para ' + p.nome} />
          <input type="text" style={{ width: '11rem' }} placeholder="motivo" value={motivo}
                 onChange={e => setMotivo(e.target.value)} aria-label="Motivo" />
          <button type="button" className="btn btn-ok btn-p" disabled={ocupado || !valido} onClick={() => enviar(+1)}>Entrada</button>
          <button type="button" className="btn btn-secundario btn-p" disabled={ocupado || !valido || Math.abs(n) > p.estoque} onClick={() => enviar(-1)}>Baixa</button>
          <a className="btn btn-discreto btn-p" href={p.url_movimentos}>Histórico</a>
        </div>
      </td>
    </tr>
  );
}

function Estoque() {
  const [produtos, setProdutos] = useState(null);
  const [ocupado, setOcupado] = useState(false);
  const [busca, setBusca] = useState('');

  useEffect(() => { LojaAPI.get('estoque').then(r => { if (r.ok) setProdutos(r.produtos); }); }, []);

  async function ajustar(p, quantidade, motivo) {
    setOcupado(true);
    const r = await LojaAPI.post('estoque_ajustar', { produto_id: p.id, quantidade, motivo });
    if (r.ok) { setProdutos(r.produtos); mostrarToast(r.mensagem); }
    else mostrarToast(r.erro || 'Não foi possível ajustar.', 'erro');
    setOcupado(false);
  }

  if (produtos === null) return <p className="carregando">Carregando estoque…</p>;
  const t = busca.toLowerCase();
  const visiveis = produtos.filter(p => !t || p.nome.toLowerCase().includes(t) || p.codigo.toLowerCase().includes(t));
  const zerados = produtos.filter(p => p.estoque === 0).length;

  return (
    <div>
      <div className="barra-busca">
        <input type="search" placeholder="Filtrar por nome ou código" value={busca} onChange={e => setBusca(e.target.value)} aria-label="Filtrar" />
        <span className="pequeno texto-2" style={{ alignSelf: 'center' }}>{produtos.length} produtos · {zerados} sem estoque</span>
      </div>
      <div className="tabela-wrap">
        <table className="tabela empilha">
          <thead><tr><th>Produto</th><th className="num">Preço</th><th className="num">Estoque</th><th>Último movimento</th><th>Ajustar</th></tr></thead>
          <tbody>
            {visiveis.length === 0 ? <tr><td colSpan="5" className="vazio">Nenhum produto.</td></tr>
              : visiveis.map(p => <LinhaProduto key={p.id} p={p} aoAjustar={ajustar} ocupado={ocupado} />)}
          </tbody>
        </table>
      </div>
    </div>
  );
}

const raiz = document.getElementById('app-estoque');
if (raiz) ReactDOM.createRoot(raiz).render(<Estoque />);
})();
