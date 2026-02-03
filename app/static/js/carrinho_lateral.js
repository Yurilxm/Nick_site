document.addEventListener("DOMContentLoaded", () => {
  const botaoCarrinho = document.getElementById("btn-carrinho");
  const carrinho = document.getElementById("carrinho");
  const botaoFechar = document.getElementById("fechar-carrinho");
  const overlay = document.getElementById("overlay-carrinho");

  function abrirCarrinho() {
    carrinho.classList.add("aberto");
    overlay.classList.add("ativo");
    document.body.classList.add("no-scroll");
  }

  function fecharCarrinho() {
    carrinho.classList.remove("aberto");
    overlay.classList.remove("ativo");
    document.body.classList.remove("no-scroll");
  }

  if (botaoCarrinho && carrinho && botaoFechar && overlay) {
    botaoCarrinho.addEventListener("click", (e) => {
      e.preventDefault();
      abrirCarrinho();
    });

    botaoFechar.addEventListener("click", fecharCarrinho);
    overlay.addEventListener("click", fecharCarrinho);
  }

  atualizarMiniCarrinho();
});

/* =========================
   CSRF TOKEN
========================= */
const csrfToken = document
  .querySelector('meta[name="csrf-token"]')
  ?.getAttribute("content");

/* =========================
   BADGE DO CARRINHO
========================= */
function atualizarBadge(qtd) {
  const badge = document.getElementById("badge-carrinho");
  if (!badge) return;

  badge.innerText = qtd;
  badge.style.display = qtd > 0 ? "inline-block" : "none";
}

/* =========================
   MINI CARRINHO (AJAX)
========================= */
function atualizarMiniCarrinho() {
  fetch("/carrinho/mini/")
    .then((response) => response.json())
    .then((data) => {
      atualizarBadge(data.quantidade_total);

      const lista = document.getElementById("mini-carrinho-lista");
      const totalEl = document.getElementById("mini-carrinho-total");

      if (!lista || !totalEl) return;

      lista.innerHTML = "";

      if (data.itens.length === 0) {
        lista.innerHTML = "<p>Seu carrinho está vazio.</p>";
        totalEl.innerText = "0,00";
        return;
      }

      data.itens.forEach((item) => {
        lista.innerHTML += `
          <li class="item-carrinho clicavel" data-item-id="${item.id}" data-url="${item.url}">
            ${
              item.imagem
                ? `<img src="${item.imagem}" class="item-carrinho-img" alt="${item.nome}">`
                : ""
            }
            <div class="item-carrinho-info">
              <strong>${item.nome}</strong>
              <span>${item.quantidade} × R$ ${item.preco.toFixed(2)}</span>
            </div>
            <button 
              class="btn-remover-mini" 
              data-item-id="${item.id}" 
              aria-label="Remover item"
            >
              ×
            </button>
          </li>
        `;
      });

      totalEl.innerText = data.total.toFixed(2);
    })
    .catch((err) => console.error("Erro mini carrinho:", err));
}

/* =========================
   REMOVER ITEM (X DO MINI CARRINHO) - EVENT DELEGATION
========================= */
document.addEventListener("click", function (e) {
  const btn = e.target.closest(".btn-remover-mini");
  if (!btn) return;

  const itemId = btn.dataset.itemId;

  fetch(`/carrinho/remover/${itemId}/`, {
    method: "POST",
    headers: {
      "X-CSRFToken": csrfToken,
      "X-Requested-With": "XMLHttpRequest",
    },
  })
    .then((res) => res.json())
    .then((data) => {
      // Remove do minicarrinho
      const liMini = btn.closest(".item-carrinho");
      if (liMini) liMini.remove();

      // Atualiza subtotal do minicarrinho
      const totalMini = document.getElementById("mini-carrinho-total");
      if (totalMini) totalMini.innerText = data.total.toFixed(2);

      // Atualiza badge
      atualizarBadge(data.quantidade_total ?? 0);

      // ✅ Sincroniza com a página de carrinho, se aberta
      const liPagina = document.querySelector(`li[data-item-id="${itemId}"]`);
      if (liPagina) {
        liPagina.remove();
      }

      const subtotalGeral = document.getElementById("subtotal-geral");
      const totalGeral = document.getElementById("total-geral");
      if (subtotalGeral) subtotalGeral.innerText = data.total.toFixed(2);
      if (totalGeral) totalGeral.innerText = data.total.toFixed(2);
    })
    .catch((err) => console.error("Erro ao remover item:", err));
});


document.addEventListener("click", function (e) {
  const item = e.target.closest(".item-carrinho.clicavel");
  if (!item) return;

  // Se clicou no botão de remover, NÃO navega
  if (e.target.closest(".btn-remover-mini")) return;

  const url = item.dataset.url;
  if (url) {
    window.location.href = url;
  }
});