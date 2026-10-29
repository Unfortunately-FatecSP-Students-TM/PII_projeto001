/* =============================================================================
   <Catalogo/> — grade de produtos com busca ao digitar e filtro por categoria.
   Consome GET api/produtos e, ao comprar, POST api/carrinho_adicionar.
   Versão pré-compilada em compilado/<nome>.js (carregada pelas páginas); se este
   .jsx for editado, a página passa a compilá-lo no navegador com o Babel standalone.
   ============================================================================= */
(() => {
const { useState, useEffect, useRef } = React;

function CardProduto({ p, podeComprar, logado, aoAdicionar }) {
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
  if (esgotado) estoqueInfo = <span className="estoque-info zerado">Esgotado</span>;
  else if (p.estoque <= 5) estoqueInfo = <span className="estoque-info baixo">Só {p.estoque} em estoque</span>;
  else estoqueInfo = <span className="estoque-info">{p.estoque} em estoque</span>;

  return (
    <article className="produto-card">
      <a className="foto" href={p.url}>
        <img src={p.imagem} alt={p.nome} loading="lazy" />
      </a>
      <div className="corpo">
        <span className="categoria">{p.categoria || 'Sem categoria'} · {p.codigo}</span>
        <a className="nome" href={p.url}>{p.nome}</a>
        <p className="descricao">{p.descricao}</p>
        <div className="rodape-card">
          <span className="preco">{p.preco_fmt}</span>
          {estoqueInfo}
        </div>
        <span className="estoque-info">Entrega em {p.prazo_dias} dias úteis</span>
      </div>
      <div className="comprar">
        {podeComprar ? (
          <div className="acoes">
            <div className="qtd" aria-label={'Quantidade de ' + p.nome}>
              <button type="button" onClick={() => setQtd(Math.max(1, qtd - 1))} disabled={esgotado || qtd <= 1}>−</button>
              <input type="text" inputMode="numeric" value={qtd} readOnly aria-label="quantidade" />
              <button type="button" onClick={() => setQtd(Math.min(p.estoque, qtd + 1))} disabled={esgotado || qtd >= p.estoque}>+</button>
            </div>
            <button type="button" className="btn btn-primario" onClick={adicionar} disabled={esgotado || enviando}>
              {esgotado ? 'Esgotado' : enviando ? 'Adicionando…' : 'Adicionar'}
            </button>
          </div>
        ) : logado ? (
          <span className="pequeno texto-3">Só clientes compram. Sua conta tem outro papel.</span>
        ) : (
          <a className="btn btn-secundario btn-largo" href={LOJA.urls.login}>Entre para comprar</a>
        )}
      </div>
    </article>
  );
}

function Catalogo({ buscaInicial }) {
  const [busca, setBusca] = useState(buscaInicial || '');
  const [categoria, setCategoria] = useState('');
  const [dados, setDados] = useState({ produtos: [], categorias: [], pode_comprar: false, logado: false });
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState('');
  const temporizador = useRef(null);

  // recarrega a lista quando busca/categoria mudam (com atraso de 300 ms ao digitar)
  useEffect(() => {
    clearTimeout(temporizador.current);
    temporizador.current = setTimeout(async () => {
      setCarregando(true);
      const r = await LojaAPI.get('produtos', null, { q: busca, categoria });
      if (r.ok) { setDados(r); setErro(''); } else { setErro(r.erro || 'Não foi possível carregar o catálogo.'); }
      setCarregando(false);
    }, busca ? 300 : 0);
    return () => clearTimeout(temporizador.current);
  }, [busca, categoria]);

  async function adicionar(p, qtd) {
    const r = await LojaAPI.post('carrinho_adicionar', { produto_id: p.id, quantidade: qtd });
    if (r.ok) {
      mostrarToast(r.mensagem);
      atualizarBadgeCarrinho(r.carrinho.quantidade_total);
    } else {
      mostrarToast(r.erro || 'Não foi possível adicionar.', 'erro');
    }
  }

  return (
    <div>
      <div className="barra-busca">
        <input type="search" placeholder="Buscar por nome, descrição ou código" value={busca}
               onChange={e => setBusca(e.target.value)} aria-label="Buscar produtos" />
        {busca && <button type="button" className="btn btn-secundario" onClick={() => setBusca('')}>Limpar</button>}
      </div>
      <div className="chips" role="tablist" aria-label="Categorias">
        <button type="button" className={'chip' + (categoria === '' ? ' ativo' : '')} onClick={() => setCategoria('')}>Todas</button>
        {dados.categorias.map(c => (
          <button key={c.id} type="button" className={'chip' + (String(categoria) === String(c.id) ? ' ativo' : '')}
                  onClick={() => setCategoria(String(c.id))}>{c.nome}</button>
        ))}
      </div>
      {erro && <div className="aviso aviso-erro">{erro}</div>}
      {carregando && dados.produtos.length === 0 ? (
        <p className="carregando">Carregando produtos…</p>
      ) : dados.produtos.length === 0 ? (
        <div className="cartao vazio-caixa">
          <p>Nenhum produto encontrado{busca ? ' para "' + busca + '"' : ''}.</p>
          <button type="button" className="btn btn-secundario" onClick={() => { setBusca(''); setCategoria(''); }}>Ver todos os produtos</button>
        </div>
      ) : (
        <div className="grade-produtos" aria-busy={carregando}>
          {dados.produtos.map(p => (
            <CardProduto key={p.id} p={p} podeComprar={dados.pode_comprar} logado={dados.logado} aoAdicionar={adicionar} />
          ))}
        </div>
      )}
    </div>
  );
}

const raizCatalogo = document.getElementById('app-catalogo');
if (raizCatalogo) {
  ReactDOM.createRoot(raizCatalogo).render(<Catalogo buscaInicial={raizCatalogo.dataset.busca} />);
}
})();
