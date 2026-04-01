document.addEventListener("DOMContentLoaded", () => {
  const botaoCarrinho = document.getElementById("btn-carrinho");
  const carrinho      = document.getElementById("carrinho");
  const botaoFechar   = document.getElementById("fechar-carrinho");
  const overlay       = document.getElementById("overlay-carrinho");

  const etapa = window.CHECKOUT_ETAPA || 0;

  // ── Etapa 3 e 4: some tudo, registra no-ops e sai ──────────────────────────
  if (etapa === 3 || etapa === 4) {
    if (carrinho)      carrinho.style.display      = "none";
    if (botaoCarrinho) botaoCarrinho.style.display  = "none";
    window.abrirCarrinho        = () => {};
    window.atualizarMiniCarrinho = () => {};
    return;
  }

  // ── Funções de abrir/fechar ─────────────────────────────────────────────────
  function abrirCarrinho() {
    if (etapa === 2) {
      window.location.href = "/carrinho/";
      return;
    }
    carrinho.classList.add("aberto");
    overlay.classList.add("ativo");
    document.body.classList.add("no-scroll");
  }

  function fecharCarrinho() {
    carrinho.classList.remove("aberto");
    overlay.classList.remove("ativo");
    document.body.classList.remove("no-scroll");
  }

  window.abrirCarrinho        = abrirCarrinho;
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

/* ========================= */
function formatarMoeda(valor) {
  return valor
    .toFixed(2)
    .replace(".", ",")
    .replace(/\B(?=(\d{3})+(?!\d))/g, ".");
}

/* ========================= */
const csrfToken = document
  .querySelector('meta[name="csrf-token"]')
  ?.getAttribute("content");

/* ========================= */
function atualizarBadge(qtd) {
  const badge = document.getElementById("badge-carrinho");
  if (!badge) return;
  badge.innerText = qtd;
  badge.classList.toggle("visivel", qtd > 0);
  badge.style.display = qtd > 0 ? "flex" : "none";
}

/* ========================= */
// Valida que a URL é interna (mesma origem) antes de navegar
function urlSegura(url) {
  try {
    const parsed = new URL(url, window.location.origin);
    if (parsed.origin === window.location.origin) {
      return parsed.pathname + parsed.search + parsed.hash;
    }
  } catch (_) { /* URL inválida */ }
  return null;
}

/* ========================= */
function atualizarMiniCarrinho() {
  const etapa = window.CHECKOUT_ETAPA || 0;

  return fetch("/carrinho/mini/")
    .then((r) => r.json())
    .then((data) => {
      atualizarBadge(data.quantidade_total);

      const lista   = document.getElementById("mini-carrinho-lista");
      const totalEl = document.getElementById("mini-carrinho-total");
      const finais  = document.querySelector(".btn-finais");

      if (!lista || !totalEl) return;

      lista.innerHTML = "";

      if (data.itens.length === 0) {
        const vazio = document.createElement("p");
        vazio.textContent = "Seu carrinho está vazio.";
        lista.appendChild(vazio);
        totalEl.innerText = "0,00";
        if (finais) finais.style.display = "none";
        return;
      }

      if (finais) finais.style.display = "block";

      data.itens.forEach((item) => {
        const li = document.createElement("li");
        li.className = "item-carrinho clicavel";
        li.dataset.itemId = item.id;
        // Armazena apenas o path validado, nunca URL externa
        li.dataset.url = urlSegura(item.url) || "";

        // Imagem
        if (item.imagem) {
          const img = document.createElement("img");
          img.src       = item.imagem;
          img.className = "item-carrinho-img";
          img.alt       = item.nome;
          li.appendChild(img);
        }

        // Info
        const info = document.createElement("div");
        info.className = "item-carrinho-info";

        const strong = document.createElement("strong");
        strong.textContent = item.nome;
        info.appendChild(strong);

        if (item.opcao) {
          const opcaoDiv = document.createElement("div");
          opcaoDiv.className   = "mini-opcao";
          opcaoDiv.textContent = item.opcao;
          info.appendChild(opcaoDiv);
        }

        const span = document.createElement("span");
        span.textContent = `${item.quantidade} x R$ ${formatarMoeda(item.preco)}`;
        info.appendChild(span);

        li.appendChild(info);

        // Botão remover
        if (etapa !== 2) {
          const btn = document.createElement("button");
          btn.className        = "btn-remover-mini";
          btn.dataset.itemId   = item.id;
          btn.setAttribute("aria-label", "Remover item");
          btn.textContent      = "×";
          li.appendChild(btn);
        }

        lista.appendChild(li);
      });

      totalEl.innerText = formatarMoeda(data.total);
    })
    .catch((err) => console.error("Erro mini carrinho:", err));
}

/* ========================= */
function atualizarPaginaCarrinho(data) {
  const subtotalGeralEl = document.getElementById("subtotal-geral");
  if (subtotalGeralEl) subtotalGeralEl.innerText = formatarMoeda(data.total);

  const totalGeralEl = document.getElementById("total-geral");
  const freteValorEl = document.getElementById("frete-valor");
  if (totalGeralEl) {
    const frete = parseFloat(freteValorEl?.innerText?.replace(",", ".")) || 0;
    totalGeralEl.innerText = formatarMoeda(data.total + frete);
  }
}

/* ========================= */
document.addEventListener("click", function (e) {
  const btn = e.target.closest(".btn-remover-mini");
  if (!btn) return;

  if ((window.CHECKOUT_ETAPA || 0) === 2) {
    alert("Finalize ou volte ao carrinho para alterar os itens.");
    return;
  }

  const itemId = btn.dataset.itemId;

  fetch(`/carrinho/remover/${encodeURIComponent(itemId)}/`, {
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
        atualizarPaginaCarrinho({ total: data.total });
      }
    })
    .catch((err) => console.error("Erro ao remover item:", err));
});

/* ========================= */
document.addEventListener("click", function (e) {
  const item = e.target.closest(".item-carrinho.clicavel");
  if (!item) return;
  if (e.target.closest(".btn-remover-mini")) return;

  const url = item.dataset.url;
  // urlSegura() já foi aplicada ao armazenar no dataset, mas validamos de novo por segurança
  const destino = urlSegura(url);
  if (destino) window.location.href = destino;
});