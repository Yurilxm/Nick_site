document.addEventListener("DOMContentLoaded", function () {

  const subtotalGeralEl  = document.getElementById("subtotal-geral");
  const totalGeralEl     = document.getElementById("total-geral");
  const freteValorEl     = document.getElementById("frete-valor");
  const freteResultadoEl = document.getElementById("frete-resultado");
  const cepInput         = document.getElementById("cep-input");
  const btnCalcularFrete = document.getElementById("btn-calcular-frete");

  let subtotalProdutos = parseFloat(subtotalGeralEl?.innerText.replace(",", ".")) || 0;
  let valorFrete       = parseFloat(freteValorEl?.innerText.replace(",", "."))    || 0;

  function getCSRFToken() {
    return document.querySelector("[name=csrfmiddlewaretoken]")?.value || "";
  }

  function atualizarTotal() {
    const total = subtotalProdutos + valorFrete;
    if (subtotalGeralEl) subtotalGeralEl.innerText = subtotalProdutos.toFixed(2);
    if (totalGeralEl)    totalGeralEl.innerText    = total.toFixed(2);
  }

  function postJSON(url, callback) {
    fetch(url, {
      method: "POST",
      headers: {
        "X-CSRFToken": getCSRFToken(),
        "X-Requested-With": "XMLHttpRequest"
      }
    }).then(r => r.json()).then(data => { if (callback) callback(data); });
  }

  atualizarTotal();

  // ==========================
  // CEP — MÁSCARA
  // ==========================
  if (cepInput) {
    const cepSalvo = sessionStorage.getItem('cep_digitado');
    if (cepSalvo && cepSalvo.length === 8) {
      cepInput.value = cepSalvo.slice(0, 5) + "-" + cepSalvo.slice(5);
    }

    cepInput.addEventListener('input', () => {
      let v = cepInput.value.replace(/\D/g, "").substring(0, 8);
      if (v.length > 5) v = v.slice(0, 5) + "-" + v.slice(5);
      cepInput.value = v;

      const cepLimpo = v.replace(/\D/g, "");
      sessionStorage.setItem('cep_digitado', cepLimpo);

      if (cepLimpo.length === 0) {
        sessionStorage.removeItem('cep_digitado');
        if (freteResultadoEl) freteResultadoEl.style.display = "none";
        valorFrete = 0;
        if (freteValorEl) freteValorEl.innerText = "0.00";
        atualizarTotal();

        fetch("/carrinho/frete/limpar/", {
          method: "POST",
          headers: {
            "X-CSRFToken": getCSRFToken(),
            "X-Requested-With": "XMLHttpRequest"
          }
        });
      }
    });

    cepInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') { e.preventDefault(); btnCalcularFrete?.click(); }
    });
  }

  // ==========================
  // QUANTIDADE
  // ==========================
  document.querySelectorAll(".btn-aumentar").forEach(btn => {
    btn.addEventListener("click", function () {
      postJSON(`/carrinho/aumentar/${this.dataset.itemId}/`, () => location.reload());
    });
  });

  document.querySelectorAll(".btn-diminuir").forEach(btn => {
    btn.addEventListener("click", function () {
      postJSON(`/carrinho/diminuir/${this.dataset.itemId}/`, () => location.reload());
    });
  });

  document.querySelectorAll(".form-remover").forEach(form => {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      postJSON(form.action, () => location.reload());
    });
  });

  // ==========================
  // CALCULAR FRETE
  // ==========================
  function calcularFrete(cep, idSelecionadoAntes) {
    if (!btnCalcularFrete || !cep || cep.length !== 8) return;

    btnCalcularFrete.disabled     = true;
    btnCalcularFrete.textContent  = "Calculando...";

    fetch("/carrinho/frete/calcular/", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-CSRFToken": getCSRFToken(),
        "X-Requested-With": "XMLHttpRequest",
      },
      body: `cep=${cep}`
    })
      .then(r => r.json())
      .then(data => {
        btnCalcularFrete.disabled    = false;
        btnCalcularFrete.textContent = "Calcular";

        if (data.status === "erro") {
          if (freteResultadoEl) {
            freteResultadoEl.innerHTML     = `<p class="frete-erro">${data.mensagem}</p>`;
            freteResultadoEl.style.display = "block";
          }
          return;
        }

        // Mantém seleção anterior se possível, senão usa a primeira
        const idSalvo = idSelecionadoAntes || sessionStorage.getItem('frete_selecionado_id');

        let html = '<div class="frete-opcoes">';
        data.opcoes.forEach((opcao, index) => {
          const selecionada = idSalvo
            ? String(opcao.id) === String(idSalvo)
            : index === 0;
          html += `
            <label class="frete-opcao ${selecionada ? 'selecionada' : ''}">
              <input type="radio" name="frete-opcao" value="${opcao.id}"
                data-valor="${opcao.preco}" data-nome="${opcao.nome}"
                data-prazo="${opcao.prazo}" data-transportadora="${opcao.transportadora}"
                ${selecionada ? 'checked' : ''}>
              <div class="frete-opcao-info">
                <span class="frete-opcao-nome">${opcao.transportadora} — ${opcao.nome}</span>
                <span class="frete-opcao-prazo">${opcao.prazo} dia(s) úteis</span>
              </div>
              <span class="frete-opcao-preco">R$ ${parseFloat(opcao.preco).toFixed(2).replace(".", ",")}</span>
            </label>`;
        });
        html += '</div>';

        if (freteResultadoEl) {
          freteResultadoEl.innerHTML     = html;
          freteResultadoEl.style.display = "block";
        }

        // Aplica opção selecionada
        const opcaoSelecionada = idSalvo
          ? data.opcoes.find(o => String(o.id) === String(idSalvo)) || data.opcoes[0]
          : data.opcoes[0];

        valorFrete = parseFloat(opcaoSelecionada.preco) || 0;
        if (freteValorEl) freteValorEl.innerText = valorFrete.toFixed(2).replace(".", ",");
        atualizarTotal();

        // Salva opção selecionada na sessão Django
        fetch("/carrinho/frete/selecionar/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken(),
            "X-Requested-With": "XMLHttpRequest"
          },
          body: JSON.stringify({
            id: opcaoSelecionada.id,
            valor: opcaoSelecionada.preco,
            nome: opcaoSelecionada.nome,
            prazo: opcaoSelecionada.prazo,
            transportadora: opcaoSelecionada.transportadora,
            cep: cep,
          })
        });

        // Listeners de troca de opção
        document.querySelectorAll('input[name="frete-opcao"]').forEach(radio => {
          radio.addEventListener("change", function () {
            document.querySelectorAll(".frete-opcao").forEach(el => el.classList.remove("selecionada"));
            this.closest(".frete-opcao").classList.add("selecionada");
            sessionStorage.setItem('frete_selecionado_id', this.value);
            valorFrete = parseFloat(this.dataset.valor) || 0;
            if (freteValorEl) freteValorEl.innerText = valorFrete.toFixed(2).replace(".", ",");
            atualizarTotal();

            fetch("/carrinho/frete/selecionar/", {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(),
                "X-Requested-With": "XMLHttpRequest"
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
  }

  // Botão manual
  btnCalcularFrete?.addEventListener("click", function () {
    const cep = cepInput.value.replace(/\D/g, "");
    if (cep.length !== 8) { alert("CEP inválido"); return; }
    sessionStorage.setItem('cep_digitado', cep);
    calcularFrete(cep, null);
  });

  // ==========================
  // AUTO-RECALCULA ao carregar
  // (quando quantidade muda e página recarrega, recalcula com CEP já salvo)
  // ==========================
  const cepParaRecalcular = sessionStorage.getItem('cep_digitado');
  if (cepParaRecalcular && cepParaRecalcular.length === 8 && btnCalcularFrete) {
    if (cepInput) {
      cepInput.value = cepParaRecalcular.slice(0, 5) + "-" + cepParaRecalcular.slice(5);
    }
    // Recalcula mantendo a opção que a pessoa tinha selecionado
    setTimeout(() => calcularFrete(cepParaRecalcular, sessionStorage.getItem('frete_selecionado_id')), 300);
  }
});