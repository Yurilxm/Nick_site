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

    btnCalcularFrete.disabled = true;
    btnCalcularFrete.textContent = "Calculando...";

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
        btnCalcularFrete.disabled = false;
        btnCalcularFrete.textContent = "Calcular";

        if (data.status === "erro") {
          if (freteResultadoEl) {
            freteResultadoEl.innerHTML = `<p class="frete-erro">${data.mensagem}</p>`;
            freteResultadoEl.style.display = "block";
          }
          return;
        }

        // Monta opções de frete
        let html = '<div class="frete-opcoes">';
        data.opcoes.forEach((opcao, index) => {
          const checked = index === 0 ? "checked" : "";
          html += `
            <label class="frete-opcao ${index === 0 ? 'selecionada' : ''}">
              <input type="radio" name="frete-opcao" value="${opcao.id}"
                data-valor="${opcao.preco}"
                data-nome="${opcao.nome}"
                data-prazo="${opcao.prazo}"
                data-transportadora="${opcao.transportadora}"
                ${checked}>
              <div class="frete-opcao-info">
                <span class="frete-opcao-nome">${opcao.transportadora} — ${opcao.nome}</span>
                <span class="frete-opcao-prazo">${opcao.prazo} dia(s) úteis</span>
              </div>
              <span class="frete-opcao-preco">R$ ${parseFloat(opcao.preco).toFixed(2).replace(".", ",")}</span>
            </label>`;
        });
        html += '</div>';

        if (freteResultadoEl) {
          freteResultadoEl.innerHTML = html;
          freteResultadoEl.style.display = "block";
        }

        // Seleciona o primeiro por padrão
        const primeiroValor = parseFloat(data.opcoes[0].preco) || 0;
        valorFrete = primeiroValor;
        if (freteValorEl) freteValorEl.innerText = valorFrete.toFixed(2).replace(".", ",");
        atualizarTotal();

        // Ao trocar opção
        document.querySelectorAll('input[name="frete-opcao"]').forEach(radio => {
          radio.addEventListener("change", function () {
            document.querySelectorAll(".frete-opcao").forEach(el => el.classList.remove("selecionada"));
            this.closest(".frete-opcao").classList.add("selecionada");

            valorFrete = parseFloat(this.dataset.valor) || 0;
            if (freteValorEl) freteValorEl.innerText = valorFrete.toFixed(2).replace(".", ",");
            atualizarTotal();

            // Atualiza sessão com opção escolhida
            fetch("/carrinho/frete/selecionar/", {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(),
                "X-Requested-With": "XMLHttpRequest",
              },
              body: JSON.stringify({
                id: this.value,
                valor: this.dataset.valor,
                nome: this.dataset.nome,
                prazo: this.dataset.prazo,
                transportadora: this.dataset.transportadora,
                cep: cep,
              })
            });
          });
        });
      });
  });
}
});