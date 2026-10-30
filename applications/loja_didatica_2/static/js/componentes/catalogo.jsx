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
        <span className="pequeno">Estado: {p.estado}</span>
        {p.console && <span className="pequeno">Console: {p.console}</span>}
        <span className="avaliacao">
          {p.avaliacao_media ? '★ ' + p.avaliacao_media.toFixed(1) + ' / 5 (' + p.avaliacao_quantidade + ')' : 'Sem avaliações'}
        </span>
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
  const [consoleProduto, setConsoleProduto] = useState('');
  const [precoMin, setPrecoMin] = useState('');
  const [precoMax, setPrecoMax] = useState('');
  const [avaliacaoMinima, setAvaliacaoMinima] = useState('');
  const [estado, setEstado] = useState('');
  const [dados, setDados] = useState({
    produtos: [], categorias: [], consoles: [], estados: [], pode_comprar: false, logado: false
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
        q: busca, categoria, console: consoleProduto, preco_min: precoMin,
        preco_max: precoMax, avaliacao_minima: avaliacaoMinima, estado
      });
      if (requisicao !== requisicaoAtual.current) return;
      if (r.ok) { setDados(r); setErro(''); } else { setErro(r.erro || 'Não foi possível carregar o catálogo.'); }
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
      </div>
      <section className="cartao filtros-avancados" aria-label="Busca avançada">
        <div className="filtros-titulo">
          <h2>Busca avançada</h2>
          <button type="button" className="btn btn-secundario" onClick={limparFiltros}>Limpar filtros</button>
        </div>
        <div className="filtros-grade">
          <div className="campo">
            <label htmlFor="filtro-console">Console</label>
            <select id="filtro-console" value={consoleProduto} onChange={e => setConsoleProduto(e.target.value)}>
              <option value="">Todos os consoles</option>
              <option value="sem_console">Sem console</option>
              {dados.consoles.map(c => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
          <div className="campo">
            <label htmlFor="filtro-preco-min">Preço mínimo (R$)</label>
            <input id="filtro-preco-min" type="number" min="0" step="0.01" value={precoMin}
                   onChange={e => setPrecoMin(e.target.value)} />
          </div>
          <div className="campo">
            <label htmlFor="filtro-preco-max">Preço máximo (R$)</label>
            <input id="filtro-preco-max" type="number" min="0" step="0.01" value={precoMax}
                   onChange={e => setPrecoMax(e.target.value)} />
          </div>
          <div className="campo">
            <label htmlFor="filtro-categoria">Categoria</label>
            <select id="filtro-categoria" value={categoria} onChange={e => setCategoria(e.target.value)}>
              <option value="">Todas as categorias</option>
              {dados.categorias.map(c => <option key={c.id} value={c.id}>{c.nome}</option>)}
            </select>
          </div>
          <div className="campo">
            <label htmlFor="filtro-avaliacao">Avaliação mínima</label>
            <select id="filtro-avaliacao" value={avaliacaoMinima}
                    onChange={e => setAvaliacaoMinima(e.target.value)}>
              <option value="">Qualquer avaliação</option>
              {[1, 2, 3, 4, 5].map(n => <option key={n} value={n}>{n} {n === 1 ? 'estrela' : 'estrelas'} ou mais</option>)}
            </select>
          </div>
          <div className="campo">
            <label htmlFor="filtro-estado">Estado</label>
            <select id="filtro-estado" value={estado} onChange={e => setEstado(e.target.value)}>
              <option value="">Todos os estados</option>
              {dados.estados.map(e => <option key={e} value={e}>{e}</option>)}
            </select>
          </div>
        </div>
      </section>
      {erro && <div className="aviso aviso-erro">{erro}</div>}
      {carregando && dados.produtos.length === 0 ? (
        <p className="carregando">Carregando produtos…</p>
      ) : dados.produtos.length === 0 ? (
        <div className="cartao vazio-caixa">
          <p>Nenhum produto encontrado{busca ? ' para "' + busca + '"' : ''}.</p>
          <button type="button" className="btn btn-secundario" onClick={limparFiltros}>Ver todos os produtos</button>
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
