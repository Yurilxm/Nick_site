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

  function renderizarResultados(data, q) {
    searchResults.innerHTML = '';
    const produtos = data.results || data; // suporta ambos os formatos

    if (!produtos.length) {
      searchResults.innerHTML = `
        <div class="search-vazio">
          🌸 Nenhum produto encontrado para "<strong>${q}</strong>"
        </div>`;
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

      const seloInfo = seloStyle(p.selo);
      const seloHTML = seloInfo
        ? `<span class="search-item-selo ${seloInfo.classe}">${seloInfo.emoji} ${p.selo}</span>`
        : '';

      const imgHTML = p.imagem
        ? `<img src="${p.imagem}" alt="${p.nome}">`
        : `<div class="search-item-img-placeholder"><i class="bi bi-image"></i></div>`;

      item.innerHTML = `
        ${imgHTML}
        <div class="search-item-info">
          <span class="search-item-nome">${p.nome}</span>
          <span class="search-item-preco">R$ ${formatarPreco(p.preco)}</span>
        </div>
        ${seloHTML}
      `;

      item.addEventListener('click', () => {
        window.location.href = p.url || `/produtos/${p.id}/${p.slug}/`;
      });

      searchResults.appendChild(item);
    });

    const footer = document.createElement('div');
    footer.className = 'search-footer';
    footer.innerHTML = `
      <a href="/buscar-produtos/?q=${encodeURIComponent(q)}">
        Ver todos os resultados para "<strong>${q}</strong>" →
      </a>`;
    searchResults.appendChild(footer);

    searchResults.style.display = 'block';
  }

});