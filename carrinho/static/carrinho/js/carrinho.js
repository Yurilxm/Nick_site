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
          data.quantidade_item;

        document.getElementById(`subtotal-${itemId}`).innerText =
          data.subtotal_item.toFixed(2);

        document.getElementById("subtotal-geral").innerText =
          data.total.toFixed(2);

        document.getElementById("total-geral").innerText =
          data.total.toFixed(2);

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
          const li = this.closest("li");
          if (li) li.remove();
        } else {
          document.getElementById(`quantidade-${itemId}`).innerText =
            data.quantidade_item;

          document.getElementById(`subtotal-${itemId}`).innerText =
            data.subtotal_item.toFixed(2);
        }

        document.getElementById("subtotal-geral").innerText =
          data.total.toFixed(2);

        document.getElementById("total-geral").innerText =
          data.total.toFixed(2);

        atualizarMiniCarrinho();
      });
    });
  });

  // ❌ REMOVER (sem reload)
  document.querySelectorAll(".form-remover").forEach(form => {
    form.addEventListener("submit", function (e) {
      e.preventDefault();

      const url = this.action;

      fetch(url, {
        method: "POST",
        headers: {
          "X-CSRFToken": csrfToken,
          "X-Requested-With": "XMLHttpRequest",
        },
      })
        .then(response => response.json())
        .then(data => {
          const li = this.closest("li");
          if (li) li.remove();

          document.getElementById("subtotal-geral").innerText =
            data.total.toFixed(2);

          document.getElementById("total-geral").innerText =
            data.total.toFixed(2);

          atualizarMiniCarrinho();
        })
        .catch(err => console.error("Erro ao remover item:", err));
    });
  });
});

function atualizarBadge(qtd) {
  const badge = document.getElementById("badge-carrinho");
  if (!badge) return;

  badge.innerText = qtd;
  badge.style.display = qtd > 0 ? "inline-block" : "none";
}