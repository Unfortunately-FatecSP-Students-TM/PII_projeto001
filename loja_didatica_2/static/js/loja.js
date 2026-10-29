/* =============================================================================
   Loja Didática 2 — JavaScript comum (sem framework)
   - LojaAPI: chamadas fetch para a API JSON (com token CSRF)
   - menu responsivo, avisos, toasts
   - pré-visualização do upload de imagem (arrastar e soltar)
   - tela do PIX: copiar código e consultar o status a cada 5 s
   Os componentes React ficam em static/js/componentes/*.jsx e usam LojaAPI.
   ============================================================================= */
(function () {
  'use strict';

  var LOJA = window.LOJA || {};      // preenchido no layout.html
  var CSRF = (document.querySelector('meta[name="csrf-token"]') || {}).content || '';

  // ---------------------------------------------------------------- API JSON
  function chamar(url, opcoes) {
    opcoes = opcoes || {};
    var config = {
      method: opcoes.method || 'GET',
      headers: { 'Accept': 'application/json', 'X-CSRF-Token': CSRF },
      credentials: 'same-origin'
    };
    if (opcoes.body !== undefined) {
      config.headers['Content-Type'] = 'application/json';
      config.body = JSON.stringify(opcoes.body);
    }
    return fetch(url, config).then(function (resp) {
      return resp.json().catch(function () {
        return { ok: false, erro: 'Resposta inválida do servidor (' + resp.status + ').' };
      }).then(function (dados) {
        if (resp.status === 401 && dados.login) {
          window.location = dados.login;      // sessão expirou: volta ao login
        }
        return dados;
      });
    }).catch(function () {
      return { ok: false, erro: 'Falha de rede. Verifique a conexão e tente novamente.' };
    });
  }

  window.LojaAPI = {
    url: function (funcao, args) {
      var u = LOJA.base + '/api/' + funcao;
      if (args !== undefined && args !== null) u += '/' + args;
      return u;
    },
    get: function (funcao, args, query) {
      var u = this.url(funcao, args);
      if (query) u += '?' + new URLSearchParams(query).toString();
      return chamar(u);
    },
    post: function (funcao, body) {
      return chamar(this.url(funcao), { method: 'POST', body: body || {} });
    },
    moeda: function (valor) {
      return 'R$ ' + Number(valor || 0).toFixed(2).replace('.', ',')
        .replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    }
  };

  // -------------------------------------------------------------- toasts/avisos
  var toastTimer = null;
  window.mostrarToast = function (texto, tipo) {
    var antigo = document.querySelector('.toast');
    if (antigo) antigo.remove();
    var el = document.createElement('div');
    el.className = 'toast' + (tipo === 'erro' ? ' erro' : '');
    el.setAttribute('role', 'status');
    el.textContent = texto;
    document.body.appendChild(el);
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { el.remove(); }, 3500);
  };

  window.atualizarBadgeCarrinho = function (quantidade) {
    var b = document.getElementById('badge-carrinho');
    if (!b) return;
    b.textContent = quantidade;
    b.classList.toggle('vazio', !quantidade);
  };

  document.addEventListener('DOMContentLoaded', function () {
    // menu (celular)
    var botao = document.querySelector('.menu-btn');
    var nav = document.getElementById('nav-principal');
    if (botao && nav) {
      botao.addEventListener('click', function () {
        var aberto = nav.classList.toggle('aberto');
        botao.setAttribute('aria-expanded', aberto ? 'true' : 'false');
      });
    }
    // fechar aviso
    document.querySelectorAll('.aviso button').forEach(function (b) {
      b.addEventListener('click', function () { b.parentNode.remove(); });
    });
    // confirmações em formulários destrutivos: <form data-confirmar="texto">
    document.querySelectorAll('form[data-confirmar]').forEach(function (f) {
      f.addEventListener('submit', function (ev) {
        if (!window.confirm(f.getAttribute('data-confirmar'))) ev.preventDefault();
      });
    });
    iniciarUpload();
    iniciarPix();
  });

  // ------------------------------------------ upload com pré-visualização
  function iniciarUpload() {
    var area = document.querySelector('.upload-area');
    if (!area) return;
    var input = area.querySelector('input[type="file"]');
    var previa = area.querySelector('.previa');
    var vazia = area.querySelector('.previa-vazia');
    var info = area.querySelector('.info-arquivo');
    var TIPOS = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/bmp', 'image/tiff'];

    function mostrar(arquivo) {
      if (!arquivo) return;
      if (TIPOS.indexOf(arquivo.type) === -1) {
        info.textContent = 'Formato não aceito (' + (arquivo.type || 'desconhecido') +
          '). Use JPEG, PNG, GIF, WEBP, BMP ou TIFF.';
        input.value = '';
        return;
      }
      if (arquivo.size > 5 * 1024 * 1024) {
        info.textContent = 'Arquivo com mais de 5 MB. Escolha uma imagem menor.';
        input.value = '';
        return;
      }
      var leitor = new FileReader();
      leitor.onload = function (e) {
        var img = new Image();
        img.onload = function () {
          info.textContent = arquivo.name + ' — ' + img.width + '×' + img.height + ' px, ' +
            (arquivo.size / 1024).toFixed(0) + ' KB. Ao salvar, o servidor recorta para ' +
            '800×600 (JPEG) e gera a miniatura 400×300.';
        };
        img.src = e.target.result;
        previa.src = e.target.result;
        previa.classList.remove('oculto');
        if (vazia) vazia.classList.add('oculto');
      };
      leitor.readAsDataURL(arquivo);
    }
    input.addEventListener('change', function () { mostrar(input.files[0]); });
    ['dragenter', 'dragover'].forEach(function (ev) {
      area.addEventListener(ev, function (e) { e.preventDefault(); area.classList.add('arrastando'); });
    });
    ['dragleave', 'drop'].forEach(function (ev) {
      area.addEventListener(ev, function (e) { e.preventDefault(); area.classList.remove('arrastando'); });
    });
    area.addEventListener('drop', function (e) {
      if (e.dataTransfer.files.length) {
        input.files = e.dataTransfer.files;
        mostrar(e.dataTransfer.files[0]);
      }
    });
  }

  // ---------------------------------------------------------- tela do PIX
  function iniciarPix() {
    var botaoCopiar = document.getElementById('copiar-pix');
    if (botaoCopiar) {
      botaoCopiar.addEventListener('click', function () {
        var texto = document.getElementById('codigo-pix').textContent.trim();
        var ok = function () { mostrarToast('Código PIX copiado.'); };
        if (navigator.clipboard) {
          navigator.clipboard.writeText(texto).then(ok, function () { selecionar(); });
        } else { selecionar(); }
        function selecionar() {
          var r = document.createRange();
          r.selectNodeContents(document.getElementById('codigo-pix'));
          var s = window.getSelection(); s.removeAllRanges(); s.addRange(r);
          mostrarToast('Selecione e copie o código (Ctrl+C).');
        }
      });
    }
    var alvo = document.getElementById('status-pix');
    if (!alvo) return;
    var pedidoId = alvo.getAttribute('data-pedido');
    var statusAtual = alvo.getAttribute('data-status');
    function consultar() {
      LojaAPI.get('pix_status', pedidoId).then(function (d) {
        if (!d.ok) return;
        if (d.status_pix !== statusAtual) {
          mostrarToast('Situação do pagamento: ' + d.status_pix_rotulo);
          setTimeout(function () { window.location.reload(); }, 1200);
        }
      });
    }
    if (statusAtual === 'gerado' || statusAtual === 'informado') {
      setInterval(consultar, 5000);
    }
  }
})();
