document.addEventListener("DOMContentLoaded", function () {
  atualizarMiniCarrinho();

  const csrfToken = document
    .querySelector('meta[name="csrf-token"]')
    ?.getAttribute('content');

  function atualizarQuantidade(url, itemId, callback) {
    fetch(url, {
      method: "POST",
      headers: {
        "X-CSRFToken": csrfToken,
        "X-Requested-With": "XMLHttpRequest",
      },
    })
      .then(response => response.json())
      .then(data => callback(data))
      .catch(error => console.error("Erro:", error));
  }

  // ➕ AUMENTAR
  document.querySelectorAll(".btn-aumentar").forEach(btn => {
    btn.addEventListener("click", function () {
      const itemId = this.dataset.itemId;
      const url = `/carrinho/aumentar/${itemId}/`;

      atualizarQuantidade(url, itemId, data => {
        document.getElementById(`quantidade-${itemId}`).innerText =
          data.quantidade;

        document.getElementById(`subtotal-${itemId}`).innerText =
          data.subtotal.toFixed(2);

        // 🔥 ATUALIZA O MINI CARRINHO
        atualizarMiniCarrinho();
      });
    });
  });

  // ➖ DIMINUIR
  document.querySelectorAll(".btn-diminuir").forEach(btn => {
    btn.addEventListener("click", function () {
      const itemId = this.dataset.itemId;
      const url = `/carrinho/diminuir/${itemId}/`;

      atualizarQuantidade(url, itemId, data => {
        if (data.removido) {
          location.reload(); // simples e seguro
        } else {
          document.getElementById(`quantidade-${itemId}`).innerText =
            data.quantidade;

          document.getElementById(`subtotal-${itemId}`).innerText =
            data.subtotal.toFixed(2);
        }

        // 🔥 ATUALIZA O MINI CARRINHO
        atualizarMiniCarrinho();
      });
    });
  });

});

function atualizarBadge(qtd) {
  const badge = document.getElementById("badge-carrinho");
  if (!badge) return;

  badge.innerText = qtd;
  badge.style.display = qtd > 0 ? "inline-block" : "none";
}

function atualizarMiniCarrinho() {
  fetch("/carrinho/mini/")
    .then(response => response.json())
    .then(data => {
      atualizarBadge(data.quantidade_total);
    })
    .catch(error => console.error("Erro mini carrinho:", error));
}
