document.addEventListener('DOMContentLoaded', function () {

  // ============================================
  // HAMBÚRGUER / DRAWER
  // ============================================
  const btnHamburguer = document.getElementById('btn-hamburguer');
  const btnFechar     = document.getElementById('btn-fechar-drawer');
  const drawer        = document.getElementById('menu-mobile-drawer');
  const overlay       = document.getElementById('menu-mobile-overlay');

  function abrirDrawer() {
    drawer.classList.add('aberto');
    overlay.style.display = 'block';
    requestAnimationFrame(() => overlay.classList.add('ativo'));
    document.body.style.overflow = 'hidden';
  }

  function fecharDrawer() {
    drawer.classList.remove('aberto');
    overlay.classList.remove('ativo');
    document.body.style.overflow = '';
    setTimeout(() => { overlay.style.display = 'none'; }, 300);
  }

  if (btnHamburguer) btnHamburguer.addEventListener('click', abrirDrawer);
  if (btnFechar)     btnFechar.addEventListener('click', fecharDrawer);
  if (overlay)       overlay.addEventListener('click', fecharDrawer);

  // ============================================
  // ACCORDION DE CATEGORIAS NO DRAWER
  // ============================================
  const btnCategorias = document.getElementById('btn-drawer-categorias');
  const bodyCategoria = document.getElementById('drawer-categorias-body');

  if (btnCategorias && bodyCategoria) {
    btnCategorias.addEventListener('click', function () {
      const aberto = bodyCategoria.classList.contains('aberto');
      bodyCategoria.classList.toggle('aberto', !aberto);
      btnCategorias.classList.toggle('aberto', !aberto);
    });
  }

  // ============================================
  // DROPDOWN USUÁRIO (desktop)
  // ============================================
  const btnUserMenu = document.getElementById('btn-user-menu');
  const userMenu    = document.getElementById('user-menu');

  if (btnUserMenu && userMenu) {
    btnUserMenu.addEventListener('click', function (e) {
      e.stopPropagation();
      userMenu.classList.toggle('aberto');
    });

    document.addEventListener('click', function (e) {
      if (!userMenu.contains(e.target) && e.target !== btnUserMenu) {
        userMenu.classList.remove('aberto');
      }
    });
  }

  // ============================================
  // CARRINHO — botão do drawer abre o lateral
  // ============================================
  const btnCarrinhoDrawer    = document.getElementById('btn-carrinho-drawer');
  const btnCarrinhoPrincipal = document.getElementById('btn-carrinho');

  if (btnCarrinhoDrawer && btnCarrinhoPrincipal) {
    btnCarrinhoDrawer.addEventListener('click', function (e) {
      e.preventDefault();
      fecharDrawer();
      setTimeout(() => btnCarrinhoPrincipal.click(), 320);
    });
  }

  // ============================================
  // SYNC BADGE — copia badge desktop → drawer
  // ============================================
  function sincronizarBadgeDrawer() {
    const badgeDesktop = document.getElementById('badge-carrinho');
    const badgeDrawer  = document.getElementById('badge-carrinho-drawer');
    if (!badgeDesktop || !badgeDrawer) return;

    badgeDrawer.textContent = badgeDesktop.textContent.trim();
    badgeDrawer.classList.toggle('visivel', badgeDesktop.classList.contains('visivel'));
  }

  const badgeDesktop = document.getElementById('badge-carrinho');
  if (badgeDesktop) {
    const observer = new MutationObserver(sincronizarBadgeDrawer);
    observer.observe(badgeDesktop, { attributes: true, childList: true, characterData: true, subtree: true });
    sincronizarBadgeDrawer();
  }

  // ============================================
  // BUSCA
  // ============================================
  const searchInput   = document.getElementById('search-input');
  const searchResults = document.getElementById('search-results');
  let searchTimer;

  if (searchInput && searchResults) {
    searchInput.addEventListener('input', function () {
      clearTimeout(searchTimer);
      const q = this.value.trim();
      if (q.length < 2) {
        searchResults.style.display = 'none';
        searchResults.innerHTML = '';
        return;
      }
      searchTimer = setTimeout(() => buscarProdutos(q), 300);
    });

    document.addEventListener('click', function (e) {
      if (!e.target.closest('.topbar-busca')) {
        searchResults.style.display = 'none';
      }
    });
  }

  function buscarProdutos(q) {
    fetch(`/buscar-produtos/?q=${encodeURIComponent(q)}`)
      .then(r => r.json())
      .then(data => renderizarResultados(data, q))
      .catch(() => { searchResults.style.display = 'none'; });
  }

  function seloStyle(selo) {
    if (!selo) return null;
    const s = selo.toLowerCase().trim();
    if (s.includes('promo') || s.includes('descont') || s.includes('oferta')) return { classe: 'selo-promo',    emoji: '🔥' };
    if (s.includes('novo') || s.includes('lança'))                             return { classe: 'selo-novo',     emoji: '✨' };
    if (s.includes('mais vend') || s.includes('destaque'))                     return { classe: 'selo-destaque', emoji: '⭐' };
    if (s.includes('ltimas') || s.includes('esgot') || s.includes('unidades'))return { classe: 'selo-urgente',  emoji: '⚠️' };
    return { classe: 'selo-default', emoji: '🏷️' };
  }

  function formatarPreco(preco) {
    return parseFloat(preco).toLocaleString('pt-BR', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    });
  }

  // Garante que a URL de destino seja sempre interna (mesma origem)
  function urlSegura(url) {
    try {
      const parsed = new URL(url, window.location.origin);
      if (parsed.origin === window.location.origin) return parsed.pathname + parsed.search + parsed.hash;
    } catch (_) { /* ignora URLs inválidas */ }
    return null;
  }

  function renderizarResultados(data, q) {
    searchResults.innerHTML = '';
    const produtos = data.results || data;

    if (!produtos.length) {
      const vazio = document.createElement('div');
      vazio.className = 'search-vazio';
      vazio.textContent = `🌸 Nenhum produto encontrado para "${q}"`;
      searchResults.appendChild(vazio);
      searchResults.style.display = 'block';
      return;
    }

    const header = document.createElement('div');
    header.className = 'search-header';
    header.textContent = `${produtos.length} produto${produtos.length > 1 ? 's' : ''} encontrado${produtos.length > 1 ? 's' : ''}`;
    searchResults.appendChild(header);

    produtos.forEach(p => {
      const item = document.createElement('div');
      item.className = 'search-item';

      // Imagem ou placeholder — sem innerHTML
      if (p.imagem) {
        const img = document.createElement('img');
        img.src = p.imagem;
        img.alt = p.nome;
        item.appendChild(img);
      } else {
        const placeholder = document.createElement('div');
        placeholder.className = 'search-item-img-placeholder';
        const icon = document.createElement('i');
        icon.className = 'bi bi-image';
        placeholder.appendChild(icon);
        item.appendChild(placeholder);
      }

      // Info (nome + preço)
      const info = document.createElement('div');
      info.className = 'search-item-info';

      const nome = document.createElement('span');
      nome.className = 'search-item-nome';
      nome.textContent = p.nome;
      info.appendChild(nome);

      const preco = document.createElement('span');
      preco.className = 'search-item-preco';
      preco.textContent = `R$ ${formatarPreco(p.preco)}`;
      info.appendChild(preco);

      item.appendChild(info);

      // Selo
      const seloInfo = seloStyle(p.selo);
      if (seloInfo) {
        const selo = document.createElement('span');
        selo.className = `search-item-selo ${seloInfo.classe}`;
        selo.textContent = `${seloInfo.emoji} ${p.selo}`;
        item.appendChild(selo);
      }

      // Navegação segura: valida URL vinda da API antes de usar
      item.addEventListener('click', () => {
        const destino = (p.url && urlSegura(p.url))
          || `/produtos/${encodeURIComponent(p.id)}/${encodeURIComponent(p.slug)}/`;
        window.location.href = destino;
      });

      searchResults.appendChild(item);
    });

    // Footer com link para todos os resultados
    const footer = document.createElement('div');
    footer.className = 'search-footer';

    const link = document.createElement('a');
    link.href = `/buscar-produtos/?q=${encodeURIComponent(q)}`;

    const textoAntes = document.createTextNode('Ver todos os resultados para "');
    const strong = document.createElement('strong');
    strong.textContent = q;
    const textoDepois = document.createTextNode('" →');

    link.appendChild(textoAntes);
    link.appendChild(strong);
    link.appendChild(textoDepois);
    footer.appendChild(link);

    searchResults.appendChild(footer);
    searchResults.style.display = 'block';
  }

});