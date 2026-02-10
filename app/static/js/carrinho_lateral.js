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

  // Expoe globalmente para o toast chamar
  window.abrirCarrinho = abrirCarrinho;

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
   BADGE
========================= */
function atualizarBadge(qtd) {
  const badge = document.getElementById("badge-carrinho");
  if (!badge) return;

  badge.innerText = qtd;
  badge.style.display = qtd > 0 ? "inline-block" : "none";
}

/* =========================
   MINI CARRINHO
========================= */
function atualizarMiniCarrinho() {
  // RETURN obrigatorio para poder usar .then() em quem chamar
  return fetch("/carrinho/mini/")
    .then((response) => response.json())
    .then((data) => {
      atualizarBadge(data.quantidade_total);

      const lista = document.getElementById("mini-carrinho-lista");
      const totalEl = document.getElementById("mini-carrinho-total");
      const finais = document.querySelector(".btn-finais");

      if (!lista || !totalEl) return;

      lista.innerHTML = "";

      if (data.itens.length === 0) {
        lista.innerHTML = "<p>Seu carrinho esta vazio.</p>";
        totalEl.innerText = "0,00";
        if (finais) finais.style.display = "none";
        return;
      }

      if (finais) finais.style.display = "block";

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
              <span>${item.quantidade} x R$ ${item.preco.toFixed(2)}</span>
            </div>
            <button class="btn-remover-mini" data-item-id="${item.id}" aria-label="Remover item">x</button>
          </li>
        `;
      });

      totalEl.innerText = data.total.toFixed(2);
    })
    .catch((err) => console.error("Erro mini carrinho:", err));
}

/* =========================
   REMOVER ITEM (DELEGACAO)
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
      atualizarBadge(data.quantidade_total ?? 0);

      if (data.carrinho_vazio) {
        atualizarMiniCarrinho();

        if (window.location.pathname.includes("/carrinho")) {
          window.location.reload();
        }
        return;
      }

      atualizarMiniCarrinho();
    })
    .catch((err) => console.error("Erro ao remover item:", err));
});

/* =========================
   CLICK NO ITEM -> PRODUTO
========================= */
document.addEventListener("click", function (e) {
  const item = e.target.closest(".item-carrinho.clicavel");
  if (!item) return;

  if (e.target.closest(".btn-remover-mini")) return;

  const url = item.dataset.url;
  if (url) {
    window.location.href = url;
  }
});