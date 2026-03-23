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

  window.abrirCarrinho = abrirCarrinho;
  window.atualizarMiniCarrinho = atualizarMiniCarrinho;

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
   FUNÇÃO FORMATAR MOEDA
========================= */
function formatarMoeda(valor) {
  return valor
    .toFixed(2)
    .replace(".", ",")
    .replace(/\B(?=(\d{3})+(?!\d))/g, ".");
}

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
  badge.classList.toggle("visivel", qtd > 0);
  badge.style.display = qtd > 0 ? "flex" : "none";
}

/* =========================
   MINI CARRINHO
========================= */
function atualizarMiniCarrinho() {
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
        lista.innerHTML = "<p>Seu carrinho está vazio.</p>";
        totalEl.innerText = "0,00";
        if (finais) finais.style.display = "none";
        return;
      }

      if (finais) finais.style.display = "block";

      data.itens.forEach((item) => {
        const li = document.createElement("li");
        li.className = "item-carrinho clicavel";
        li.dataset.itemId = item.id;
        li.dataset.url = item.url;

        li.innerHTML = `
          ${item.imagem ? `<img src="${item.imagem}" class="item-carrinho-img" alt="${item.nome}">` : ""}
          <div class="item-carrinho-info">
            <strong>${item.nome}</strong>
            ${item.opcao ? `<div class="mini-opcao">${item.opcao}</div>` : ""}
            <span>${item.quantidade} x R$ ${formatarMoeda(item.preco)}</span>
          </div>
          <button class="btn-remover-mini" data-item-id="${item.id}" aria-label="Remover item">×</button>
        `;

        lista.appendChild(li);
      });

      totalEl.innerText = formatarMoeda(data.total);
    })
    .catch((err) => console.error("Erro mini carrinho:", err));
}

/* =========================
   ATUALIZA PÁGINA CARRINHO
========================= */
function atualizarPaginaCarrinho(data) {
  const subtotalGeralEl = document.getElementById("subtotal-geral");
  if (subtotalGeralEl) {
    subtotalGeralEl.innerText = formatarMoeda(data.total);
  }

  const totalGeralEl = document.getElementById("total-geral");
  const freteValorEl = document.getElementById("frete-valor");

  if (totalGeralEl) {
    const frete = parseFloat(freteValorEl?.innerText?.replace(",", ".")) || 0;
    totalGeralEl.innerText = formatarMoeda(data.total + frete);
  }
}

/* =========================
   REMOVER ITEM
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
      atualizarMiniCarrinho();

      if (window.location.pathname.includes("/carrinho")) {
        atualizarPaginaCarrinho({
          total: data.total,
          carrinho_vazio: data.carrinho_vazio,
          itens_removidos: [itemId],
        });
      }
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
  if (url) window.location.href = url;
});