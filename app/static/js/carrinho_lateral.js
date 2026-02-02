document.addEventListener("DOMContentLoaded", () => {
  const botaoCarrinho = document.getElementById("btn-carrinho");
  const carrinho = document.getElementById("carrinho");
  const botaoFechar = document.getElementById("fechar-carrinho");

  if (botaoCarrinho && carrinho && botaoFechar) {
    botaoCarrinho.addEventListener("click", (e) => {
      e.preventDefault();
      carrinho.classList.toggle("aberto");
    });

    botaoFechar.addEventListener("click", () => {
      carrinho.classList.remove("aberto");
    });
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
          <li class="item-carrinho" data-item-id="${item.id}">
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
   REMOVER ITEM (EVENT DELEGATION)
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
      const li = btn.closest(".item-carrinho");
      if (li) li.remove();

      const totalEl = document.getElementById("mini-carrinho-total");
      if (totalEl) {
        totalEl.innerText = data.total.toFixed(2);
      }

      atualizarMiniCarrinho();
    })
    .catch((err) => console.error("Erro ao remover item:", err));
});