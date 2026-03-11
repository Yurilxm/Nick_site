// ================================================
// MENU — Nick Brindes
// ================================================

// ---- BUSCA ----
document.addEventListener('DOMContentLoaded', function () {
  const input = document.getElementById('search-input');
  const resultsBox = document.getElementById('search-results');

  if (input && resultsBox) {
    let timeout = null;

    input.addEventListener('input', function () {
      const query = this.value.trim();
      clearTimeout(timeout);

      if (query.length < 2) {
        resultsBox.style.display = 'none';
        resultsBox.innerHTML = '';
        return;
      }

      timeout = setTimeout(() => {
        fetch(`/buscar-produtos/?q=${encodeURIComponent(query)}`)
          .then(r => r.json())
          .then(data => {
            resultsBox.innerHTML = '';
            if (!data.results.length) { resultsBox.style.display = 'none'; return; }

            data.results.forEach(produto => {
              const item = document.createElement('div');
              item.classList.add('search-item');
              item.innerHTML = `
                <img src="${produto.imagem}" alt="${produto.nome}">
                <div>
                  <strong>${produto.nome}</strong><br>
                  <small>R$ ${produto.preco}</small>
                </div>
              `;
              item.addEventListener('click', () => {
                window.location.href = `/produtos/${produto.id}/${produto.slug}/`;
              });
              resultsBox.appendChild(item);
            });

            resultsBox.style.display = 'block';
          });
      }, 300);
    });
  }
});

// ---- DROPDOWN USUÁRIO + DRAWER MOBILE ----
document.addEventListener('DOMContentLoaded', () => {

  // Dropdown do usuário (clique)
  const btnUser = document.getElementById('btn-user-menu');
  const userMenu = document.getElementById('user-menu');

  if (btnUser && userMenu) {
    btnUser.addEventListener('click', (e) => {
      e.stopPropagation();
      userMenu.classList.toggle('aberto');
    });

    // Fecha ao clicar fora
    document.addEventListener('click', (e) => {
      if (!e.target.closest('.user-dropdown')) {
        userMenu.classList.remove('aberto');
      }
    });
  }

  // Fecha busca ao clicar fora
  document.addEventListener('click', (e) => {
    const resultsBox = document.getElementById('search-results');
    if (resultsBox && !e.target.closest('.topbar-busca')) {
      resultsBox.style.display = 'none';
    }
  });

  // ---- DRAWER MOBILE ----
  const btnHamburguer = document.getElementById('btn-hamburguer');
  const drawer = document.getElementById('menu-mobile-drawer');
  const overlay = document.getElementById('menu-mobile-overlay');
  const btnFechar = document.getElementById('btn-fechar-drawer');

  function abrirDrawer() {
    drawer?.classList.add('aberto');
    if (overlay) {
      overlay.style.display = 'block';
      requestAnimationFrame(() => overlay.classList.add('ativo'));
    }
    document.body.classList.add('no-scroll');
  }

  function fecharDrawer() {
    drawer?.classList.remove('aberto');
    overlay?.classList.remove('ativo');
    setTimeout(() => { if (overlay) overlay.style.display = 'none'; }, 300);
    document.body.classList.remove('no-scroll');
  }

  btnHamburguer?.addEventListener('click', abrirDrawer);
  btnFechar?.addEventListener('click', fecharDrawer);
  overlay?.addEventListener('click', fecharDrawer);
});