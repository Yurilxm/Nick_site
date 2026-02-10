document.addEventListener("DOMContentLoaded", function () {

  // ==========================
  // ELEMENTOS PRINCIPAIS
  // ==========================
  const subtotalGeralEl = document.getElementById("subtotal-geral");
  const totalGeralEl = document.getElementById("total-geral");
  const freteValorEl = document.getElementById("frete-valor");
  const freteResultadoEl = document.getElementById("frete-resultado");

  const cepInput = document.getElementById("cep-input");
  const btnCalcularFrete = document.getElementById("btn-calcular-frete");

  // ==========================
  // VALORES INICIAIS SEGUROS
  // ==========================
  let subtotalProdutos = parseFloat(subtotalGeralEl?.innerText.replace(",", ".")) || 0;
  let valorFrete = parseFloat(freteValorEl?.innerText.replace(",", ".")) || 0;

  // Sempre recalcula o total ao carregar a página
  atualizarTotal();

  // ==========================
  // FUNÇÕES
  // ==========================
  function atualizarTotal() {
    const total = subtotalProdutos + valorFrete;

    if (subtotalGeralEl) {
      subtotalGeralEl.innerText = subtotalProdutos.toFixed(2);
    }

    if (totalGeralEl) {
      totalGeralEl.innerText = total.toFixed(2);
    }
  }

  function getCSRFToken() {
    const csrfInput = document.querySelector("[name=csrfmiddlewaretoken]");
    return csrfInput ? csrfInput.value : "";
  }

  function postJSON(url, callback) {
    fetch(url, {
      method: "POST",
      headers: {
        "X-CSRFToken": getCSRFToken(),
        "X-Requested-With": "XMLHttpRequest",
      }
    })
      .then(response => response.json())
      .then(data => {
        if (callback) callback(data);
      });
  }

  // ==========================
  // BOTÕES + / -
  // ==========================
  document.querySelectorAll(".btn-aumentar").forEach(btn => {
    btn.addEventListener("click", function () {
      const itemId = this.dataset.itemId;
      postJSON(`/carrinho/aumentar/${itemId}/`, () => {
        location.reload();
      });
    });
  });

  document.querySelectorAll(".btn-diminuir").forEach(btn => {
    btn.addEventListener("click", function () {
      const itemId = this.dataset.itemId;
      postJSON(`/carrinho/diminuir/${itemId}/`, () => {
        location.reload();
      });
    });
  });

  // ==========================
  // REMOVER ITEM
  // ==========================
  document.querySelectorAll(".form-remover").forEach(form => {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      postJSON(form.action, () => {
        location.reload();
      });
    });
  });

  // ==========================
  // CALCULAR FRETE
  // ==========================
  if (btnCalcularFrete) {
    btnCalcularFrete.addEventListener("click", function () {
      const cep = cepInput.value.replace(/\D/g, "");

      if (cep.length !== 8) {
        alert("CEP inválido");
        return;
      }

      fetch("/carrinho/frete/calcular/", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
          "X-CSRFToken": getCSRFToken(),
          "X-Requested-With": "XMLHttpRequest",
        },
        body: `cep=${cep}`
      })
        .then(response => response.json())
        .then(data => {
          // Backend é a fonte da verdade
          valorFrete = parseFloat(data.frete.valor) || 0;

          if (freteValorEl) {
            freteValorEl.innerText = valorFrete.toFixed(2);
          }

          if (freteResultadoEl) {
            freteResultadoEl.style.display = "block";
          }

          // Atualiza total corretamente (produto + frete)
          atualizarTotal();
        });
    });
  }

});